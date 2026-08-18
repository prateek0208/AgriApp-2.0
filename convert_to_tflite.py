"""
Convert .h5 Keras model to .tflite format for lightweight cloud deployment.
TFLite Runtime is ~5MB vs TensorFlow's ~500MB.
"""
import tensorflow as tf
import os

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# Try MobileNetV2 first, fall back to DSANet
mobilenet_path = os.path.join(MODEL_DIR, "plant_disease_mobilenetv2.h5")
dsanet_path = os.path.join(MODEL_DIR, "sarva_krishi_dsanet_v2_optimized.h5")

if os.path.exists(mobilenet_path):
    h5_path = mobilenet_path
    print(f"Converting MobileNetV2 model: {h5_path}")
elif os.path.exists(dsanet_path):
    h5_path = dsanet_path
    print(f"Converting DSANet model: {h5_path}")
else:
    print("ERROR: No .h5 model found!")
    exit(1)

# Load and convert
model = tf.keras.models.load_model(h5_path, compile=False)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Quantize for smaller size
tflite_model = converter.convert()

# Save
output_path = os.path.join(MODEL_DIR, "plant_disease.tflite")
with open(output_path, 'wb') as f:
    f.write(tflite_model)

size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"Converted successfully! Saved to: {output_path} ({size_mb:.1f} MB)")
