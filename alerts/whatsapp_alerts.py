"""
whatsapp_alerts.py — AgriTech AI WhatsApp Alert System
Uses Twilio WhatsApp API to send farm alerts to farmers.

Setup:
  1. Sign up at https://www.twilio.com (free)
  2. Go to Messaging → Try it out → WhatsApp
  3. Copy Account SID, Auth Token from Console Dashboard
  4. Add to your .env file or configure directly in the app.
  5. Farmer must send "join <sandbox-word>" to +1 415 523 8886 on WhatsApp first.
"""

import os
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)
logger = logging.getLogger(__name__)


def get_twilio_credentials():
    """Retrieve Twilio credentials from session state or environment variables."""
    import streamlit as st
    
    # Check session state first, then environment variables
    # Priority: session_state > .env > Streamlit secrets (cloud)
    def _get_secret(key, default=""):
        val = os.getenv(key, "").strip()
        if not val:
            try:
                val = st.secrets.get(key, "").strip()
            except Exception:
                pass
        return val or default

    sid = st.session_state.get("twilio_sid", "").strip() or _get_secret("TWILIO_ACCOUNT_SID")
    token = st.session_state.get("twilio_token", "").strip() or _get_secret("TWILIO_AUTH_TOKEN")
    from_number = st.session_state.get("twilio_from", "").strip() or _get_secret("TWILIO_WHATSAPP_FROM")
    
    if not from_number:
        from_number = "whatsapp:+14155238886"
        
    return sid, token, from_number


def is_twilio_configured() -> bool:
    """Check if Twilio credentials are set."""
    sid, token, _ = get_twilio_credentials()
    return bool(sid and token)


def save_credentials_to_env(sid: str, token: str, from_number: str) -> bool:
    """Saves the Twilio credentials directly to the .env file and reloads dotenv."""
    try:
        env_path = get_path(".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        sid_found = False
        token_found = False
        from_found = False
        
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("TWILIO_ACCOUNT_SID="):
                new_lines.append(f"TWILIO_ACCOUNT_SID={sid}\n")
                sid_found = True
            elif stripped.startswith("TWILIO_AUTH_TOKEN="):
                new_lines.append(f"TWILIO_AUTH_TOKEN={token}\n")
                token_found = True
            elif stripped.startswith("TWILIO_WHATSAPP_FROM="):
                new_lines.append(f"TWILIO_WHATSAPP_FROM={from_number}\n")
                from_found = True
            else:
                new_lines.append(line)
                
        if not sid_found:
            new_lines.append(f"TWILIO_ACCOUNT_SID={sid}\n")
        if not token_found:
            new_lines.append(f"TWILIO_AUTH_TOKEN={token}\n")
        if not from_found:
            new_lines.append(f"TWILIO_WHATSAPP_FROM={from_number}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        # Reload dotenv with override to update os.environ immediately
        load_dotenv(override=True)
        return True
    except Exception as e:
        logger.error(f"Failed to save credentials to .env: {e}")
        return False


def send_whatsapp_alert(
    to_number: str,
    crop: str,
    modal_price: int,
    weather_temp: float,
    weather_desc: str,
    soil_score: float,
    location: str,
    lang: str = "en"
) -> dict:
    """
    Sends a WhatsApp alert to the farmer with farm summary.

    Args:
        to_number:    Farmer's phone number (e.g. +919876543210)
        crop:         Recommended crop name
        modal_price:  Today's mandi price in ₹/quintal
        weather_temp: Current temperature in °C
        weather_desc: Weather description string
        soil_score:   Soil health score (0–100)
        location:     Farmer's city/state
        lang:         'en' for English, 'hi' for Hindi

    Returns:
        dict with 'success' bool and 'message' string
    """
    sid, token, from_number = get_twilio_credentials()
    
    if not sid or not token:
        return {
            "success": False,
            "message": (
                "Twilio credentials not configured. "
                "Please configure them in the Settings panel."
            )
        }

    try:
        from twilio.rest import Client
    except ImportError:
        return {
            "success": False,
            "message": "Twilio package not installed. Run: pip install twilio"
        }

    # Normalize phone numbers (must have + and country code, e.g., +91)
    to_number = to_number.strip()
    if not to_number.startswith("+"):
        if len(to_number) == 10:
            to_number = "+91" + to_number  # Default to India if 10 digits
        elif len(to_number) == 12 and to_number.startswith("91"):
            to_number = "+" + to_number
        else:
            return {
                "success": False,
                "message": "❌ Invalid phone number. Please include your country code (e.g., +919876543210)."
            }

    # ── Build message content ──
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    if lang == "hi":
        message_body = f"""🌾 *AgriTech AI — किसान अलर्ट*
📅 {now}
📍 स्थान: {location}

━━━━━━━━━━━━━━━━━━
🤖 *AI फसल सिफारिश*
➡️ *{crop.upper()}* उगाने की सलाह दी जाती है।

💰 *आज का मंडी भाव*
{crop}: ₹{modal_price:,} / क्विंटल

🌡️ *मौसम अपडेट*
तापमान: {weather_temp}°C
स्थिति: {weather_desc}

📊 *मिट्टी स्वास्थ्य स्कोर*
{soil_score:.0f}/100 {'✅ उत्तम' if soil_score > 70 else '⚠️ मध्यम' if soil_score > 40 else '🔴 खराब'}

━━━━━━━━━━━━━━━━━━
🙏 AgriTech AI आपकी मदद के लिए हमेशा तैयार है।
app.agritech.ai"""
    else:
        message_body = f"""🌾 *AgriTech AI — Farm Alert*
📅 {now}
📍 Location: {location}

━━━━━━━━━━━━━━━━━━
🤖 *AI Crop Recommendation*
➡️ Best crop for your soil: *{crop.upper()}*

💰 *Today's Mandi Price*
{crop}: ₹{modal_price:,} / quintal

🌡️ *Weather Update*
Temp: {weather_temp}°C
Condition: {weather_desc}

📊 *Soil Health Score*
{soil_score:.0f}/100 {'✅ Excellent' if soil_score > 70 else '⚠️ Moderate' if soil_score > 40 else '🔴 Poor'}

━━━━━━━━━━━━━━━━━━
💡 Open AgriTech AI for detailed analysis.
Powered by AgriTech AI 🇮🇳"""

    # ── Send via Twilio ──
    try:
        client = Client(sid, token)
        to_whatsapp = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
        from_whatsapp = f"whatsapp:{from_number}" if not from_number.startswith("whatsapp:") else from_number

        msg = client.messages.create(
            from_=from_whatsapp,
            to=to_whatsapp,
            body=message_body
        )
        logger.info(f"WhatsApp alert sent to {to_number}. SID: {msg.sid}")
        return {
            "success": True,
            "message": f"✅ Alert sent successfully! Message SID: {msg.sid}",
            "sid": msg.sid
        }

    except Exception as e:
        logger.error(f"Failed to send WhatsApp alert to {to_number}: {e}")
        err_msg = str(e)
        if "Authenticate" in err_msg or "20003" in err_msg:
            return {
                "success": False,
                "message": "❌ Authentication failed! Please check your Twilio Account SID and Auth Token."
            }
        elif "21610" in err_msg or "opt-in" in err_msg or "unsubscribed" in err_msg:
            return {
                "success": False,
                "message": (
                    "❌ Opt-in required! You must send 'join <sandbox-keyword>' on WhatsApp to "
                    "your Twilio Sandbox number (+1 415 523 8886) first."
                )
            }
        return {
            "success": False,
            "message": f"❌ Send failed: {err_msg}"
        }


def build_price_alert(crop: str, price: int, change_pct: float, lang: str = "en") -> str:
    """Builds a short price-only alert message."""
    arrow = "↑" if change_pct >= 0 else "↓"
    if lang == "hi":
        return (
            f"💰 *मंडी भाव अलर्ट*\n"
            f"{crop}: ₹{price:,}/क्विंटल\n"
            f"{arrow} {abs(change_pct):.1f}% इस सप्ताह\n"
            f"— AgriTech AI"
        )
    return (
        f"💰 *Mandi Price Alert*\n"
        f"{crop}: ₹{price:,}/quintal\n"
        f"{arrow} {abs(change_pct):.1f}% this week\n"
        f"— AgriTech AI"
    )


def build_weather_alert(temp: float, desc: str, rain_warning: bool, lang: str = "en") -> str:
    """Builds a weather-only alert message."""
    if lang == "hi":
        warning = "⚠️ *बारिश की चेतावनी!* कल स्प्रे न करें।\n" if rain_warning else ""
        return (
            f"🌦️ *मौसम अलर्ट*\n"
            f"तापमान: {temp}°C\n"
            f"स्थिति: {desc}\n"
            f"{warning}"
            f"— AgriTech AI"
        )
    warning = "⚠️ *Rain Warning!* Avoid spraying tomorrow.\n" if rain_warning else ""
    return (
        f"🌦️ *Weather Alert*\n"
        f"Temp: {temp}°C\n"
        f"Condition: {desc}\n"
        f"{warning}"
        f"— AgriTech AI"
    )


# ─────────────────────────────────────────────
# STREAMLIT UI COMPONENT
# ─────────────────────────────────────────────
def show_whatsapp_panel(
    crop: str,
    modal_price: int,
    weather: dict,
    soil_score: float,
    location: str,
    lang: str = "en"
):
    """
    Renders the WhatsApp Alert settings panel inside the app.
    Call this anywhere in main.py where you want to show it.
    """
    import streamlit as st
    from core.database import add_subscriber, remove_subscriber, get_subscribers, is_subscribed

    # Initialize credential fields in session state if not present
    if "twilio_sid" not in st.session_state:
        st.session_state.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    if "twilio_token" not in st.session_state:
        st.session_state.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    if "twilio_from" not in st.session_state:
        st.session_state.twilio_from = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

    configured = is_twilio_configured()

    with st.expander("📱 WhatsApp Alerts" if lang == "en" else "📱 WhatsApp अलर्ट", expanded=True):
        
        # Segment 1: Credentials configuration tab
        st.subheader("⚙️ Twilio Settings" if lang == "en" else "⚙️ ट्विलियो सेटिंग्स")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            sid_val = st.text_input(
                "Twilio Account SID", 
                value=st.session_state.twilio_sid, 
                type="default",
                help="Found in your Twilio Console dashboard"
            )
            st.session_state.twilio_sid = sid_val
            
        with col_c2:
            token_val = st.text_input(
                "Twilio Auth Token", 
                value=st.session_state.twilio_token, 
                type="password",
                help="Found in your Twilio Console dashboard"
            )
            st.session_state.twilio_token = token_val
            
        from_val = st.text_input(
            "Twilio Sandbox Sender Number" if lang == "en" else "ट्विलियो सैंडबॉक्स भेजने वाला नंबर", 
            value=st.session_state.twilio_from,
            help="Usually whatsapp:+14155238886"
        )
        st.session_state.twilio_from = from_val

        # Save to .env button
        if st.button("💾 Save Credentials permanently to .env" if lang == "en" else "💾 क्रेडेंशियल को .env में स्थायी रूप से सहेजें"):
            if sid_val and token_val:
                success = save_credentials_to_env(sid_val, token_val, from_val)
                if success:
                    st.success("🎉 Credentials successfully saved to .env and loaded!" if lang == "en" else "🎉 क्रेडेंशियल .env में सहेजे गए और लोड किए गए!")
                    st.rerun()
                else:
                    st.error("Failed to save credentials to file." if lang == "en" else "फ़ाइल में क्रेडेंशियल सहेजने में विफल।")
            else:
                st.warning("Please fill in both SID and Auth Token." if lang == "en" else "कृपया SID और Auth टोकन दोनों भरें।")

        st.divider()

        # Step-by-step connection guide
        st.markdown(
            """
            ### 🛠️ Step-by-Step Twilio WhatsApp Setup Guide
            
            Follow these **3 simple steps** to start receiving alerts on your phone:
            
            1. **Sign Up**: Register a free account at [twilio.com](https://www.twilio.com).
            2. **Copy Credentials**: Paste your **Account SID** and **Auth Token** in the settings fields above and click **Save**.
            3. **🚨 Sandbox Activation (CRITICAL STEP) 🚨**:
               - Open WhatsApp on your phone.
               - Send a message saying **`join <sandbox-keyword>`** (for example, `join yield-gold` or `join standard-glass`) to **+1 415 523 8886**.
               - *Note*: You can find your exact `<sandbox-keyword>` in your Twilio Console under **Messaging → Try it out → Send a WhatsApp Message**.
               - **You will not receive any alerts until you complete this step!**
            """ if lang == "en" else
            """
            ### 🛠️ चरण-दर-चरण ट्विलियो व्हाट्सएप सेटअप गाइड
            
            अपने फोन पर अलर्ट प्राप्त करना शुरू करने के लिए इन **3 सरल चरणों** का पालन करें:
            
            1. **साइन अप करें**: [twilio.com](https://www.twilio.com) पर एक मुफ्त खाता पंजीकृत करें।
            2. **क्रेडेंशियल कॉपी करें**: अपना **Account SID** और **Auth Token** ऊपर दिए गए फ़ील्ड में पेस्ट करें और **Save** पर क्लिक करें।
            3. **🚨 सैंडबॉक्स सक्रियण (महत्वपूर्ण चरण) 🚨**:
               - अपने फोन पर व्हाट्सएप खोलें।
               - **+1 415 523 8886** नंबर पर व्हाट्सएप मैसेज भेजें: **`join <आपका-सैंडबॉक्स-कीवर्ड>`** (जैसे, `join yield-gold` या `join standard-glass`)।
               - *नोट*: आप अपना सही कीवर्ड ट्विलियो कंसोल में **Messaging → Try it out → Send a WhatsApp Message** के तहत पा सकते हैं।
               - **जब तक आप इस चरण को पूरा नहीं करते, आपको कोई भी अलर्ट नहीं मिलेगा!**
            """
        )

        st.divider()

        # ==========================================
        # TABBED ALERT CONTROL PANELS
        # ==========================================
        ui_tab1, ui_tab2, ui_tab3 = st.tabs([
            "📤 Send Manual Alert" if lang == "en" else "📤 मैन्युअल अलर्ट भेजें",
            "🔔 Subscribe to Automated Daily Alerts" if lang == "en" else "🔔 दैनिक स्वचालित अलर्ट सदस्यता",
            "🚀 Backend Worker Control" if lang == "en" else "🚀 बैकएंड वर्कर नियंत्रण"
        ])

        with ui_tab1:
            st.markdown("### Send a One-Time Alert" if lang == "en" else "### एक बार का अलर्ट भेजें")
            
            # Phone input
            phone_label = "📞 Your WhatsApp Number" if lang == "en" else "📞 आपका WhatsApp नंबर"
            phone_hint  = "+919876543210 (with country code)" if lang == "en" else "+919876543210 (देश कोड के साथ)"
            phone = st.text_input(phone_label, placeholder=phone_hint, key="wa_phone")

            # Alert type
            alert_type_label = "Alert Type" if lang == "en" else "अलर्ट का प्रकार"
            alert_options = {
                "en": ["📊 Full Farm Summary", "💰 Price Alert Only", "🌦️ Weather Alert Only"],
                "hi": ["📊 पूरा खेत सारांश", "💰 केवल मूल्य अलर्ट", "🌦️ केवल मौसम अलर्ट"],
            }
            alert_choice = st.radio(alert_type_label, alert_options[lang], key="wa_alert_type")

            # Send button
            btn_label = "📤 Send WhatsApp Alert" if lang == "en" else "📤 WhatsApp अलर्ट भेजें"
            if st.button(btn_label, use_container_width=True, key="wa_send_btn"):
                if not phone or len(phone) < 10:
                    err = "Please enter a valid phone number with country code." if lang == "en" else "कृपया देश कोड के साथ वैध फ़ोन नंबर दर्ज करें।"
                    st.error(err)
                elif not is_twilio_configured():
                    err = "Twilio credentials are not set. Please enter SID and Auth Token above." if lang == "en" else "ट्विलियो क्रेडेंशियल सेट नहीं हैं। कृपया ऊपर SID और Auth टोकन दर्ज करें।"
                    st.error(err)
                else:
                    with st.spinner("Sending WhatsApp message..." if lang == "en" else "व्हाट्सएप संदेश भेज रहे हैं..."):
                        temp = weather.get("current_temp", 25.0) if weather else 25.0
                        desc = weather.get("current_desc", "N/A") if weather else "N/A"
                        rain_warn = any(
                            "rain" in d.get("desc", "").lower()
                            for d in (weather.get("forecast", []) if weather else [])
                        )

                        sid, token, from_num = get_twilio_credentials()
                        
                        # Choose message type
                        idx = alert_options[lang].index(alert_choice)
                        if idx == 0:
                            result = send_whatsapp_alert(
                                phone, crop, modal_price, temp, desc,
                                soil_score, location, lang
                            )
                        elif idx == 1:
                            from twilio.rest import Client as TC
                            try:
                                client = TC(sid, token)
                                body   = build_price_alert(crop, modal_price, 2.5, lang)
                                to_wa  = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
                                from_wa = f"whatsapp:{from_num}" if not from_num.startswith("whatsapp:") else from_num
                                msg    = client.messages.create(from_=from_wa, to=to_wa, body=body)
                                result = {"success": True, "message": f"✅ Price alert sent! SID: {msg.sid}"}
                            except Exception as e:
                                logger.error(f"Failed to send price alert: {e}")
                                err_msg = str(e)
                                if "21610" in err_msg or "opt-in" in err_msg:
                                    err_msg = "Opt-in required! Send 'join <sandbox-keyword>' on WhatsApp to +1 415 523 8886 first."
                                result = {"success": False, "message": f"❌ Send failed: {err_msg}"}
                        else:
                            from twilio.rest import Client as TC
                            try:
                                client = TC(sid, token)
                                body   = build_weather_alert(temp, desc, rain_warn, lang)
                                to_wa  = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
                                from_wa = f"whatsapp:{from_num}" if not from_num.startswith("whatsapp:") else from_num
                                msg    = client.messages.create(from_=from_wa, to=to_wa, body=body)
                                result = {"success": True, "message": f"✅ Weather alert sent! SID: {msg.sid}"}
                            except Exception as e:
                                logger.error(f"Failed to send weather alert: {e}")
                                err_msg = str(e)
                                if "21610" in err_msg or "opt-in" in err_msg:
                                    err_msg = "Opt-in required! Send 'join <sandbox-keyword>' on WhatsApp to +1 415 523 8886 first."
                                result = {"success": False, "message": f"❌ Send failed: {err_msg}"}

                        if result["success"]:
                            st.success(result["message"])
                            st.balloons()
                        else:
                            st.error(result["message"])

        with ui_tab2:
            st.markdown("### 🔔 Automated Alert Registration" if lang == "en" else "### 🔔 स्वचालित अलर्ट पंजीकरण")
            st.write(
                "Register your WhatsApp number to automatically receive weather updates, "
                "mandi price shifts, and precision crop alerts every day in the background!"
                if lang == "en" else
                "मौसम अपडेट, मंडी के बदलते भाव, और फसल सटीक विश्लेषण की अलर्ट सीधे व्हाट्सएप पर रोजाना पाने के लिए रजिस्टर करें!"
            )
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                sub_phone = st.text_input(
                    "📞 Subscriber Phone Number" if lang == "en" else "📞 ग्राहक का फोन नंबर",
                    placeholder="+919876543210",
                    key="sub_phone"
                )
                sub_crop = st.selectbox(
                    "🌾 Crop of Interest" if lang == "en" else "🌾 फसल रुचि",
                    ["Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Soybean", 
                     "Groundnut", "Tomato", "Onion", "Potato", "Mustard", "Gram"],
                    key="sub_crop"
                )
            with sub_col2:
                sub_loc = st.text_input(
                    "📍 Location / Market State" if lang == "en" else "📍 स्थान / बाजार राज्य",
                    value=location,
                    key="sub_loc"
                )
                sub_lang = st.selectbox(
                    "🗣️ Alert Language" if lang == "en" else "🗣️ अलर्ट भाषा",
                    ["English", "Hindi / हिंदी"],
                    index=0 if lang == "en" else 1,
                    key="sub_lang"
                )
                
            if st.button("🔔 Subscribe to Automated Daily Alerts" if lang == "en" else "🔔 दैनिक स्वचालित अलर्ट की सदस्यता लें", use_container_width=True):
                if not sub_phone or len(sub_phone) < 10:
                    st.error("Please enter a valid phone number." if lang == "en" else "कृपया वैध फ़ोन नंबर दर्ज करें।")
                elif not sub_loc:
                    st.error("Please enter a location." if lang == "en" else "कृपया स्थान दर्ज करें।")
                else:
                    target_lang = "hi" if "Hindi" in sub_lang else "en"
                    # Add country code +91 if 10 digits
                    formatted_phone = sub_phone.strip()
                    if not formatted_phone.startswith("+"):
                        if len(formatted_phone) == 10:
                            formatted_phone = "+91" + formatted_phone
                        elif len(formatted_phone) == 12 and formatted_phone.startswith("91"):
                            formatted_phone = "+" + formatted_phone
                    
                    ok = add_subscriber(
                        phone=formatted_phone,
                        location=sub_loc,
                        crop=sub_crop.lower(),
                        lang=target_lang,
                        alert_type="Full"
                    )
                    if ok:
                        st.success(f"🎉 Successfully subscribed {formatted_phone}! Automated daily alerts will start executing in the background." if lang == "en" else f"🎉 सफलतापूर्वक सदस्यता ली गई: {formatted_phone}! स्वचालित दैनिक अलर्ट पृष्ठभूमि में चलना शुरू हो जाएंगे।")
                        st.rerun()
                    else:
                        st.error("Failed to add subscriber to database." if lang == "en" else "डेटाबेस में ग्राहक जोड़ने में विफल।")
            
            # Show list of subscribers
            st.divider()
            st.subheader("📋 Subscribed Farmers" if lang == "en" else "📋 सदस्यता प्राप्त किसान")
            subs = get_subscribers()
            if not subs:
                st.info("No active subscribers yet." if lang == "en" else "अभी कोई सक्रिय ग्राहक नहीं है।")
            else:
                for s in subs:
                    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
                    with col_s1:
                        st.write(f"📞 **{s['phone']}** ({s['lang'].upper()})")
                    with col_s2:
                        st.caption(f"🌾 {s['crop'].title()} | 📍 {s['location']}")
                    with col_s3:
                        if st.button("🗑️ Remove" if lang == "en" else "🗑️ हटाएं", key=f"unsub_{s['phone']}"):
                            remove_subscriber(s['phone'])
                            st.success("Unsubscribed successfully!" if lang == "en" else "सफलतापूर्वक हटाया गया!")
                            st.rerun()

        with ui_tab3:
            st.markdown("### ⚙️ Automated Backend Dispatch Control" if lang == "en" else "### ⚙️ स्वचालित बैकएंड डिस्पैच नियंत्रण")
            st.write(
                "You can trigger the automated alert dispatcher manually from here to test if "
                "subscribers receive their background alerts without needing to wait for the scheduled daily time."
            )
            
            if st.button("🚀 Run Backend Alert Dispatcher Once" if lang == "en" else "🚀 एक बार बैकएंड अलर्ट डिस्पैचर चलाएं", use_container_width=True):
                with st.spinner("Executing backend alert worker..."):
                    try:
                        # Executing backend_alerts.py --once
                        res = subprocess.run(["python", get_path("alerts", "backend_alerts.py"), "--once"], capture_output=True, text=True, timeout=30)
                        
                        st.subheader("📋 Backend Output Logs:")
                        if res.returncode == 0:
                            st.success("✅ Backend dispatcher run completed successfully!")
                        else:
                            st.error(f"❌ Backend run failed with exit code {res.returncode}")
                        
                        # Display stdout or stderr
                        log_out = res.stdout if res.stdout else res.stderr
                        st.code(log_out if log_out else "No output generated.")
                    except Exception as e:
                        st.error(f"Error running backend script: {e}")

        # Preview message
        st.divider()
        with st.expander("👀 Preview Message" if lang == "en" else "👀 संदेश पूर्वावलोकन"):
            temp = weather.get("current_temp", 25.0) if weather else 25.0
            desc = weather.get("current_desc", "Clear sky") if weather else "N/A"
            preview_text = (
                f"🌾 *AgriTech AI {'— Farm Alert' if lang == 'en' else '— किसान अलर्ट'}*\n"
                f"📍 {'Location' if lang == 'en' else 'स्थान'}: {location}\n\n"
                f"🤖 {'Recommended' if lang == 'en' else 'अनुशंसित'}: *{crop.upper()}*\n"
                f"💰 {'Price' if lang == 'en' else 'मूल्य'}: ₹{modal_price:,}/{'quintal' if lang == 'en' else 'क्विंटल'}\n"
                f"🌡️ {'Temp' if lang == 'en' else 'तापमान'}: {temp}°C — {desc}\n"
                f"📊 {'Soil Score' if lang == 'en' else 'मिट्टी स्कोर'}: {soil_score:.0f}/100"
            )
            st.code(preview_text, language=None)
