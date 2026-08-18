import streamlit as st
import time
import numpy as np
from PIL import Image
from core.language_pack import t
from core.paths import get_path

# ─────────────────────────────────────────────────────────────
# REAL ML MODEL LOADER (CACHED) — Uses TFLite for lightweight cloud deployment
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🧠 Loading AI Model into memory... (This takes a few seconds)")
def load_ml_assets():
    """Loads the TFLite model and class labels. Caches to avoid reloading on every click."""
    try:
        import os
        
        tflite_path = get_path("models", "plant_disease.tflite")
        h5_mobilenet_path = get_path("models", "plant_disease_mobilenetv2.h5")
        h5_dsanet_path = get_path("models", "sarva_krishi_dsanet_v2_optimized.h5")
        classes_path = get_path("models", "classes.txt")
        
        interpreter = None
        model_type = "tflite"
        
        # Priority: TFLite (lightweight) > H5 via TensorFlow (heavy)
        if os.path.exists(tflite_path):
            try:
                import tflite_runtime.interpreter as tflite
                interpreter = tflite.Interpreter(model_path=tflite_path)
            except ImportError:
                # Fallback: try tensorflow's built-in tflite interpreter
                try:
                    import tensorflow as tf
                    interpreter = tf.lite.Interpreter(model_path=tflite_path)
                except ImportError:
                    pass
            
            if interpreter is not None:
                interpreter.allocate_tensors()
                with open(classes_path, 'r') as f:
                    class_names = [line.strip() for line in f.readlines() if line.strip()]
                return interpreter, class_names, "tflite"
        
        # Fallback: Load .h5 model with full TensorFlow (for local dev)
        try:
            import tensorflow as tf
            if os.path.exists(h5_mobilenet_path):
                model = tf.keras.models.load_model(h5_mobilenet_path, compile=False)
                model_type = "mobilenetv2"
            elif os.path.exists(h5_dsanet_path):
                model = tf.keras.models.load_model(h5_dsanet_path, compile=False)
                model_type = "dsanet"
            else:
                st.error("🚨 No model file found in the models/ folder.")
                return None, [], "none"
            
            with open(classes_path, 'r') as f:
                class_names = [line.strip() for line in f.readlines() if line.strip()]
            return model, class_names, model_type
        except ImportError:
            st.error("🚨 No ML runtime available. Install tflite-runtime or tensorflow.")
            return None, [], "none"
            
    except Exception as e:
        st.error(f"🚨 Failed to load model: {e}")
        return None, [], "none"

# ─────────────────────────────────────────────────────────────
# TREATMENT GENERATOR
# ─────────────────────────────────────────────────────────────
def get_treatments(disease_name):
    """Returns specialized treatments based on the disease name."""
    disease = disease_name.lower()
    
    if "healthy" in disease:
        return {
            "status": "Healthy",
            "color": "#4CAF50", # Green
            "organic": "Maintain good air circulation and water at the base of the plant.",
            "chemical": "No chemicals needed. Continue standard NPK fertilization."
        }
    
    if "blight" in disease:
        return {
            "status": "Critical Infection",
            "color": "#F44336", # Red
            "organic": "Destroy infected plants immediately. Apply copper-based fungicide sprays.",
            "chemical": "Use systemic fungicides like Metalaxyl, Dimethomorph, or Mancozeb."
        }
        
    if "rust" in disease:
        return {
            "status": "Fungal Infection",
            "color": "#FF9800", # Orange
            "organic": "Apply sulfur dust. Ensure proper crop rotation next season.",
            "chemical": "Apply Triazole fungicides (like Tebuconazole) immediately."
        }
        
    if "spot" in disease or "scab" in disease:
        return {
            "status": "Bacterial/Fungal Spot",
            "color": "#FF9800",
            "organic": "Spray neem oil or baking soda solution. Avoid overhead watering.",
            "chemical": "Use Copper oxychloride or Chlorothalonil sprays every 7-10 days."
        }
        
    if "virus" in disease or "greening" in disease or "curl" in disease or "mosaic" in disease:
        return {
            "status": "Viral Infection",
            "color": "#9C27B0", # Purple
            "organic": "Viruses cannot be cured. Uproot and burn infected plants to save the rest.",
            "chemical": "Use insecticides (like Imidacloprid) to kill the insects transmitting the virus."
        }

    if "mold" in disease or "mildew" in disease:
        return {
            "status": "Fungal Infection",
            "color": "#FF9800",
            "organic": "Improve air circulation. Remove affected leaves. Apply neem oil spray.",
            "chemical": "Use fungicides containing Chlorothalonil or Mancozeb."
        }

    if "rot" in disease:
        return {
            "status": "Fungal/Bacterial Rot",
            "color": "#F44336",
            "organic": "Remove and destroy infected parts. Avoid overwatering. Apply compost tea.",
            "chemical": "Apply Copper-based fungicides or Captan spray."
        }

    if "scorch" in disease:
        return {
            "status": "Leaf Scorch",
            "color": "#FF9800",
            "organic": "Ensure adequate watering. Mulch around plants to retain moisture.",
            "chemical": "Apply potassium-based fertilizers to strengthen leaf tissue."
        }
        
    # Default fallback
    return {
        "status": "Action Required",
        "color": "#FF9800",
        "organic": "Consult a local agricultural expert for a targeted organic plan.",
        "chemical": "Use a broad-spectrum pesticide cautiously after consulting a professional."
    }

# ─────────────────────────────────────────────────────────────
# INFERENCE ENGINE
# ─────────────────────────────────────────────────────────────
def analyze_leaf_image(image_bytes, model, class_names, model_type):
    """Runs inference with TFLite or TensorFlow depending on what's loaded."""
    import io
    
    # 1. Open and resize image
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((224, 224))
    
    # 2. Convert to Array
    img_array = np.array(img).astype('float32')
    
    if model_type == "tflite":
        # TFLite inference
        img_array = np.expand_dims(img_array, axis=0)
        
        input_details = model.get_input_details()
        output_details = model.get_output_details()
        
        model.set_tensor(input_details[0]['index'], img_array)
        model.invoke()
        predictions = model.get_tensor(output_details[0]['index'])
    else:
        # Full TensorFlow inference
        if model_type == "mobilenetv2":
            import tensorflow as tf
            img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        
        img_array = np.expand_dims(img_array, axis=0)
        predictions = model.predict(img_array, verbose=0)
    
    result_index = np.argmax(predictions[0])
    disease_name = class_names[result_index]
    confidence = float(np.max(predictions[0]) * 100)
    
    return disease_name, confidence

# ─────────────────────────────────────────────────────────────
# STREAMLIT UI COMPONENT
# ─────────────────────────────────────────────────────────────
def show_plant_doctor_tab():
    """Renders the improved Plant Doctor UI."""
    
    st.header(t('pd_title'))
    st.markdown("---")
    
    model, class_names, model_type = load_ml_assets()
    
    if model is None:
        st.warning("Cannot start Plant Doctor. The ML model is missing or ML runtime is not installed.")
        return
    
    # Show which model is active
    if model_type == "tflite":
        st.success("🧠 **AI Engine:** TFLite Optimized (Lightweight Cloud Model)")
    elif model_type == "mobilenetv2":
        st.success("🧠 **AI Engine:** MobileNetV2 (High Accuracy, 90%+ on PlantVillage)")
    else:
        st.info("🧠 **AI Engine:** DSANet v2 (Lightweight model)")
        
    # Image Upload
    uploaded_file = st.file_uploader(t('pd_upload_lbl'), type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.image(Image.open(uploaded_file), caption="Uploaded Leaf", use_container_width=True)
            
        with col2:
            st.info(t('pd_analyzing'))
            
            # Progress bar animation (just for UX feel)
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1)
                
            # Run Real AI Inference
            disease_name, confidence = analyze_leaf_image(uploaded_file.getvalue(), model, class_names, model_type)
            
            # Formatting the raw class name (e.g., 'Tomato___Early_blight' -> 'Tomato - Early Blight')
            clean_name = disease_name.replace("___", " — ").replace("_", " ")
            
            # Get specific treatments
            treats = get_treatments(disease_name)
            
            # Dynamic Styling based on severity
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.2); border-left: 5px solid {treats['color']}; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="margin-top:0; color: {treats['color']};">{clean_name}</h2>
                <h4 style="margin:0; opacity: 0.9;">{t('pd_confidence')} {confidence:.1f}%</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Low confidence warning
            if confidence < 70:
                st.warning("⚠️ Low confidence prediction. The image may not be clear enough or the disease may not be in our database. Try uploading a clearer, close-up photo of the affected leaf.")
            
            # Treatment Recommendations
            st.subheader("💡 Recommended Actions")
            
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid #4CAF50 !important; background: rgba(76, 175, 80, 0.1) !important;">
                    <h4 style="margin-top:0;">{t('pd_organic')}</h4>
                    <p style="font-size: 0.9em;">{treats['organic']}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with t_col2:
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid #FF5252 !important; background: rgba(255, 82, 82, 0.1) !important;">
                    <h4 style="margin-top:0;">{t('pd_chemical')}</h4>
                    <p style="font-size: 0.9em;">{treats['chemical']}</p>
                </div>
                """, unsafe_allow_html=True)
                
    else:
        st.warning(t('pd_no_image'))
