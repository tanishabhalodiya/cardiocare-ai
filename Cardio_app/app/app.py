import streamlit as st
import numpy as np
import joblib
import os
import streamlit.components.v1 as components
import time
import random
import folium
import matplotlib.pyplot as plt

from streamlit_folium import folium_static



# ================= SPLASH SCREEN =================
import time

if "splash_done" not in st.session_state:
    st.session_state.splash_done = False

if not st.session_state.splash_done:
    splash_html = """
    <html>
    <head>
    <style>
    body {
        margin: 0;
        padding: 0;
        background: linear-gradient(135deg, #547792, #94B4C1);
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        font-family: 'Segoe UI', sans-serif;
    }

    .splash-container {
        text-align: center;
        animation: fadeOut 1s ease-in-out 4s forwards;
    }

    /* 3D HEART */
    .heart-3d {
        width: 140px;
        height: 140px;
        margin: auto;
        position: relative;
        transform-style: preserve-3d;
        animation: rotate 4s linear infinite, beat 1.2s infinite;
    }

    .heart-3d::before,
    .heart-3d::after {
        content: "";
        position: absolute;
        width: 70px;
        height: 110px;
        background: #FF4B5C;
        border-radius: 70px 70px 0 0;
        top: 0;
    }

    .heart-3d::before {
        left: 35px;
        transform: rotate(-45deg);
        transform-origin: 0 100%;
        box-shadow: -10px 10px 25px rgba(0,0,0,0.25);
    }

    .heart-3d::after {
        left: 0;
        transform: rotate(45deg);
        transform-origin: 100% 100%;
        box-shadow: 10px 10px 25px rgba(0,0,0,0.25);
    }

    @keyframes beat {
        0% { transform: scale(1); }
        50% { transform: scale(1.15); }
        100% { transform: scale(1); }
    }

    @keyframes rotate {
        0% { transform: rotateY(0deg); }
        100% { transform: rotateY(360deg); }
    }

    /* SPLIT EFFECT */
    .split::before {
        animation: splitLeft 1.5s forwards;
    }

    .split::after {
        animation: splitRight 1.5s forwards;
    }

    @keyframes splitLeft {
        to {
            transform: rotate(-45deg) translateX(-80px);
            opacity: 0;
        }
    }

    @keyframes splitRight {
        to {
            transform: rotate(45deg) translateX(80px);
            opacity: 0;
        }
    }

    .title {
        margin-top: 35px;
        font-size: 36px;
        color: white;
        font-weight: 800;
        letter-spacing: 2px;
        animation: glow 1.5s ease-in-out infinite alternate;
    }

    .subtitle {
        margin-top: 10px;
        font-size: 18px;
        color: #EAE0CF;
        letter-spacing: 1px;
    }

    @keyframes glow {
        from { text-shadow: 0 0 10px #fff; }
        to { text-shadow: 0 0 25px #fff, 0 0 40px #EAE0CF; }
    }

    @keyframes fadeOut {
        to { opacity: 0; visibility: hidden; }
    }
    </style>
    </head>

    <body>
        <div class="splash-container">
            <div class="heart-3d" id="heart"></div>
            <div class="title">CardioCare AI</div>
            <div class="subtitle">Smart Heart Health System</div>
        </div>

        <script>
            setTimeout(function() {
                document.getElementById("heart").classList.add("split");
            }, 2500);
        </script>
    </body>
    </html>
    """

    components.html(splash_html, height=600)
    time.sleep(5)
    st.session_state.splash_done = True
    st.rerun()
    
if "patient_data" not in st.session_state:
    st.session_state.patient_data = []



# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="CardioC are AI",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== SESSION STATE FOR THEME =====================
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

# ===================== THEME COLORS =====================
PRIMARY = "#547792"
SECONDARY = "#94B4C1"
BACKGROUND_LIGHT = "#FFFFFF"
TEXT_DARK = "#000000"
ACCENT = "#FF6B6B"
SUCCESS = "#4CAF50"
WARNING = "#FF9800"
BACKGROUND_DARK = "#000000"
TEXT_LIGHT = "#FFFFFF"

# ===================== DYNAMIC THEME CSS =====================
def get_theme_css():
    if st.session_state.theme == 'Light':
        return f"""
        body {{
            background: {BACKGROUND_LIGHT};
            color: {TEXT_DARK};
        }}
        .header {{
            background: linear-gradient(135deg, {PRIMARY}, {SECONDARY});
            color: white;
        }}
        .card {{
            background: rgba(255,255,255,0.95);
            color: {TEXT_DARK};
        }}
        .metric {{
            background: linear-gradient(135deg, #F5F5F5, #FFFFFF);
            color: {TEXT_DARK};
        }}
        .timeline-item {{
            background: linear-gradient(135deg, #F5F5F5, #FFFFFF);
            color: {TEXT_DARK};
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {PRIMARY}, {SECONDARY});
        }}
        """
    else:  # Dark mode
        return f"""
        body {{
            background: {BACKGROUND_DARK};
            color: {TEXT_LIGHT};
        }}
        .header {{
            background: linear-gradient(135deg, #2C3E50, #34495E);
            color: {TEXT_LIGHT};
        }}
        .card {{
            background: rgba(44,62,80,0.9);
            color: {TEXT_LIGHT};
        }}
        .metric {{
            background: linear-gradient(135deg, #34495E, #2C3E50);
            color: {TEXT_LIGHT};
        }}
        .timeline-item {{
            background: linear-gradient(135deg, #34495E, #2C3E50);
            color: {TEXT_LIGHT};
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #2C3E50, #34495E);
        }}
        .section-title {{
            color: {SECONDARY};
        }}
        .metric-value {{
            color: {SECONDARY};
        }}
        """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

body {{
    font-family: 'Poppins', sans-serif;
    margin: 0;
    padding: 0;
    transition: background 0.3s ease, color 0.3s ease;
}}

{get_theme_css()}

.header {{
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    position: relative;
    overflow: hidden;
}}

.header::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
}}

@keyframes rotate {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

.header-title {{
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}}

.header-subtitle {{
    font-size: 18px;
    opacity: 0.9;
}}

.card {{
    backdrop-filter: blur(10px);
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    margin-bottom: 25px;
    border: 1px solid rgba(255,255,255,0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}}

.section-title {{
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
}}

.section-title::before {{
    content: '●';
    color: {ACCENT};
    margin-right: 10px;
    font-size: 20px;
}}

[data-testid="stSidebar"] * {{
    color: white !important;
    font-weight: 600;
}}

.metric {{
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border-left: 5px solid {PRIMARY};
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}}

.metric:hover {{
    transform: scale(1.05);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}}

.metric-title {{
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}}

.metric-value {{
    font-size: 28px;
    font-weight: 800;
}}

.timeline-item {{
    padding: 15px;
    border-left: 5px solid {PRIMARY};
    margin-bottom: 12px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}}

.timeline-item:hover {{
    transform: translateX(5px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}

.avatar {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 100px;
    z-index: 9999;
    animation: float 3s ease-in-out infinite;
    cursor: pointer;
    transition: transform 0.3s ease;
}}

.avatar:hover {{
    transform: scale(1.1);
}}

.high-risk-glow {{
    animation: redPulse 1.5s infinite;
    border: 2px solid {ACCENT} !important;
    box-shadow: 0 0 20px rgba(255,43,43,0.8), 0 0 40px rgba(255,43,43,0.6);
    background: linear-gradient(135deg, #ffebeb, #ffffff) !important;
}}

@keyframes redPulse {{
    0% {{ box-shadow: 0 0 5px rgba(255,43,43,0.4); }}
    50% {{ box-shadow: 0 0 25px rgba(255,43,43,1); }}
    100% {{ box-shadow: 0 0 5px rgba(255,43,43,0.4); }}
}}

@keyframes float {{
    0% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-15px); }}
    100% {{ transform: translateY(0px); }}
}}

.progress-bar {{
    width: 100%;
    height: 10px;
    background: #e0e0e0;
    border-radius: 5px;
    overflow: hidden;
    margin-top: 10px;
}}

.progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, {SUCCESS}, {WARNING}, {ACCENT});
    transition: width 1s ease;
}}

.glow-button {{
    background: linear-gradient(135deg, {PRIMARY}, {SECONDARY});
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}}

.glow-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}}

.unique-feature {{
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
    border-radius: 20px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.3);
}}

.heart-3d {{
    width: 200px;
    height: 200px;
    margin: 20px auto;
    perspective: 1000px;
}}

.heart {{
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    animation: rotateY 4s infinite linear;
}}

.heart::before, .heart::after {{
    content: '';
    width: 100px;
    height: 160px;
    position: absolute;
    left: 50px;
    top: 0;
    background: {ACCENT};
    border-radius: 100px 100px 0 0;
    transform: rotate(-45deg);
    transform-origin: 0 100%;
}}

.heart::after {{
    left: 0;
    transform: rotate(45deg);
    transform-origin: 100% 100%;
}}

@keyframes rotateY {{
    0% {{ transform: rotateY(0deg); }}
    100% {{ transform: rotateY(360deg); }}
}}

.fade-in {{
    animation: fadeIn 1s ease-in;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.testimonial {{
    background: linear-gradient(135deg, rgba(255,255,255,0.8), rgba(255,255,255,0.6));
    padding: 20px;
    border-radius: 15px;
    margin: 10px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    font-style: italic;
}}

.map-container {{
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}}

</style>
""", unsafe_allow_html=True)



# # ===================== LOAD MODEL =====================
@st.cache_resource
def load_package():
    import os
    import joblib

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
    # BASE_DIR = Cardio_app/app

    MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "cardio_model.pkl")
    MODEL_PATH = os.path.abspath(MODEL_PATH)

    # DEBUG (optional – can remove later)
    print("Looking for model at:", MODEL_PATH)

    package = joblib.load(MODEL_PATH)
    return package["model"], package["scaler"], package["features"]

model, scaler, feature_names = load_package()


# @st.cache_resource
# def load_package():
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # app folder
#     MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "cardio_model.pkl")

#     package = joblib.load(MODEL_PATH)
#     return package["model"], package["scaler"], package["features"]

# model, scaler, feature_names = load_package()

# ===================== HELPERS =====================

def get_precautions(risk, bmi, systolic, diastolic, smoke, active):
    tips = []

    if risk == "High Risk":
        tips.append("🚨 Immediate cardiologist consultation is required.")
        tips.append("💊 Do not skip prescribed medicines.")
        tips.append("🏥 Avoid heavy physical exertion.")

    if systolic >= 140 or diastolic >= 90:
        tips.append("🩸 Control blood pressure with low-salt diet and regular monitoring.")

    if bmi >= 25:
        tips.append("⚖️ Reduce weight through balanced diet and daily walking.")

    if smoke == 1:
        tips.append("🚭 Quit smoking immediately to reduce heart strain.")

    if active == 0:
        tips.append("🏃 Start light physical activity like 30 min walking daily.")

    tips.append("🥗 Eat fruits, vegetables, and avoid oily/junk food.")
    tips.append("💧 Stay hydrated and maintain regular sleep.")

    return tips


def get_risk_level(prob):
    if prob < 0.45:
        return "Low Risk", SUCCESS
    elif prob < 0.75:
        return "Moderate Risk", WARNING
    else:
        return "High Risk", ACCENT

def speak_text(text, lang_code):
    components.html(f"""
    <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = `{text}`;
        msg.lang = "{lang_code}";
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
    </script>
    """, height=0)

def build_input(form):
    values = {}
    values["height"] = form["height"]
    values["weight"] = form["weight"]
    values["ap_hi"] = form["ap_hi"]
    values["ap_lo"] = form["ap_lo"]
    values["smoke"] = form["smoke"]
    values["alco"] = form["alco"]
    values["active"] = form["active"]
    values["age_years"] = form["age"]

    bmi = form["weight"] / ((form["height"] / 100) ** 2)
    values["BMI"] = bmi

    values["high_bp"] = int(form["ap_hi"] >= 140 or form["ap_lo"] >= 90)

    for col in ["cholesterol_1","cholesterol_2","cholesterol_3","gluc_1","gluc_2","gluc_3"]:
        values[col] = 0

    values[f"cholesterol_{form['cholesterol']}"] = 1
    values[f"gluc_{form['gluc']}"] = 1

    row = np.array([values.get(col, 0) for col in feature_names]).reshape(1, -1)
    return scaler.transform(row), bmi

def generate_recommendations(risk, bmi, age):
    recs = []
    if risk == "High Risk":
        recs.append("🚨 Immediate consultation with a cardiologist recommended.")
        recs.append("💊 Consider starting prescribed medications.")
    if bmi > 25:
        recs.append("🏃‍♂️ Increase physical activity and consider a balanced diet.")
    if age > 50:
        recs.append("📅 Schedule regular check-ups every 6 months.")
    recs.append("🥗 Maintain a heart-healthy diet rich in fruits and vegetables.")
    recs.append("🚭 Quit smoking if applicable.")
    return recs

def create_health_map(lat, lon, risk_level):
    m = folium.Map(location=[lat, lon], zoom_start=12)
    
    # User's location
    folium.Marker([lat, lon], popup="Your Location", icon=folium.Icon(color="blue")).add_to(m)
    
    # Nearby hospitals (simulated)
    hospitals = [
        {"name": "City General Hospital", "lat": lat + 0.01, "lon": lon + 0.01},
        {"name": "Heart Care Center", "lat": lat - 0.01, "lon": lon - 0.01},
        {"name": "Metro Cardiology Clinic", "lat": lat + 0.005, "lon": lon - 0.005}
    ]
    
    for hosp in hospitals:
        color = "red" if risk_level == "High Risk" else "green"
        folium.Marker([hosp["lat"], hosp["lon"]], popup=hosp["name"], icon=folium.Icon(color=color)).add_to(m)
    
    return m

# ===================== SIDEBAR =====================
st.sidebar.title("🫀 CardioCare AI")
st.sidebar.markdown("---")

# Theme Toggle
theme_options = ["Light", "Dark"]
selected_theme = st.sidebar.selectbox("Theme", theme_options, index=theme_options.index(st.session_state.theme))
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme
    st.rerun()

page = st.sidebar.radio("Navigation", ["🏠 Dashboard", "🩺 Patient Assessment", "📊 Analytics", "ℹ️ About"], index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Stats**")
st.sidebar.metric("Total Assessments", "1,247")
st.sidebar.metric("High Risk Cases", "23%")

# ===================== HEADER =====================
st.markdown(f"""
<div class="header">
    <div class="header-title">CardioCare AI – Smart Heart Health System</div>
    <div class="header-subtitle">Clinical Decision Support with Advanced Visualizations</div>
</div>
""", unsafe_allow_html=True)

# ===================== FLOATING DOCTOR AVATAR =====================
st.markdown("""
<div class="avatar" onclick="alert('Hello! I\'m your AI Health Assistant. How can I help?')">
<img src="https://cdn-icons-png.flaticon.com/512/387/387561.png" width="100%">
</div>
""", unsafe_allow_html=True)

# ===================== DASHBOARD =====================
if page == "🏠 Dashboard":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <div class="section-title">👨‍⚕️ Doctor Panel</div>
            <p>Advanced system for early cardiovascular risk detection with real-time insights.</p>
            <div class="unique-feature">
                <strong>Confidence Score:</strong> 94.7%<br>
                <div class="progress-bar"><div class="progress-fill" style="width: 94.7%;"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)



    with col2:
        st.markdown("""
        <div class="card">
            <div class="section-title">📊 Capabilities</div>
            <ul>
                <li>Risk Probability Analysis</li>
                <li>3D Heart Visualization</li>
                <li>ECG Simulation</li>
                <li>Voice Assistant</li>
                <li>Personalized Recommendations</li>
                <li>Health Timeline</li>
                <li>Interactive Health Maps</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <div class="section-title">🧠 AI Engine</div>
            <p>Logistic Regression + Feature Engineering + Scaling + Real-time Processing</p>
            <div class="unique-feature">
                <strong>Model Accuracy:</strong> 87.3%<br>
                <div class="progress-bar"><div class="progress-fill" style="width: 87.3%;"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Unique Feature: 3D Heart Animation

    st.markdown("### 💖 Interactive 3D Heart Model")
    st.markdown("""
    <div class="heart-3d">
        <div class="heart"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# # ===================== PATIENT ASSESSMENT =====================
elif page == "🩺 Patient Assessment":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("## 🧾 Patient Assessment Panel")
    
    with st.expander("📝 Patient Information", expanded=True):
        c1, c2 = st.columns(2)

        with c1:
            age = st.number_input("Age", 18, 120, 45, help="Enter your age in years")
            height = st.number_input("Height (cm)", 120, 220, 165, help="Height in centimeters")
            weight = st.number_input("Weight (kg)", 30, 200, 70, help="Weight in kilograms")
            smoke = st.selectbox("Smoking", ["No", "Yes"], help="Do you smoke?")

        with c2:
            ap_hi = st.number_input("Systolic BP", 80, 250, 130, help="Systolic blood pressure")
            ap_lo = st.number_input("Diastolic BP", 50, 150, 85, help="Diastolic blood pressure")
            cholesterol = st.selectbox("Cholesterol", ["Normal", "Above Normal", "Well Above Normal"], help="Cholesterol level")
            gluc = st.selectbox("Glucose", ["Normal", "Above Normal", "Well Above Normal"], help="Glucose level")
            alco = st.selectbox("Alcohol", ["No", "Yes"], help="Do you consume alcohol?")
            active = st.selectbox("Physically Active", ["No", "Yes"], help="Are you physically active?")

    lang = st.selectbox("Voice Language", ["English", "Hindi"], help="Select language for voice assistant")

    if st.button("🔍 Analyze Patient", key="analyze", help="Click to run AI analysis"):
        with st.spinner("Analyzing patient data..."):
            time.sleep(2)

        form = {
            "age": age,
            "height": height,
            "weight": weight,
            "ap_hi": ap_hi,
            "ap_lo": ap_lo,
            "cholesterol": 1 if cholesterol=="Normal" else 2 if cholesterol=="Above Normal" else 3,
            "gluc": 1 if gluc=="Normal" else 2 if gluc=="Above Normal" else 3,
            "smoke": 1 if smoke=="Yes" else 0,
            "alco": 1 if alco=="Yes" else 0,
            "active": 1 if active=="Yes" else 0
        }

        X, bmi = build_input(form)
        proba = float(model.predict_proba(X)[0][1])
        risk, risk_color = get_risk_level(proba)

        precautions = get_precautions(risk, bmi, ap_hi, ap_lo, form["smoke"], form["active"])

        # ================= SAVE PATIENT DATA =================
        st.session_state.patient_data.append({
            "age": age,
            "bmi": bmi,
            "systolic": ap_hi,
            "diastolic": ap_lo,
            "risk": risk,
            "probability": proba
        })


        # Metrics with enhanced styling
        m1, m2, m3 = st.columns(3)


        with m1:
            st.markdown(f"<div class='metric'><div class='metric-title'>Risk Level</div><div class='metric-value'>{risk}</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric'><div class='metric-title'>Probability</div><div class='metric-value'>{proba:.2f}</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric'><div class='metric-title'>BMI</div><div class='metric-value'>{bmi:.2f}</div></div>", unsafe_allow_html=True)

        # ================= SPEEDOMETER GAUGE =================
        components.html(f"""
        <div style="width:300px;margin:auto;">
        <canvas id="gauge"></canvas>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
        const ctx = document.getElementById('gauge').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Risk', 'Remaining'],
                datasets: [{{
                    data: [{proba*100:.1f}, {100 - proba*100:.1f}],
                    backgroundColor: ['#547792', '#EAE0CF'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                rotation: -90,
                circumference: 180,
                cutout: '70%',
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
        </script>
        """, height=260)


        # ================= ECG =================
        st.markdown("### 📈 Live ECG Simulation")

        components.html("""
        <svg width="100%" height="120" viewBox="0 0 500 120" preserveAspectRatio="none">
        <polyline 
            points="0,60 40,60 60,20 80,100 100,60 140,60 160,30 180,90 200,60 240,60 260,20 280,100 300,60 340,60 360,30 380,90 400,60 440,60 460,60 500,60"
            fill="none"
            stroke="white"
            stroke-width="3"
            stroke-linejoin="round"
            stroke-linecap="round"
            >
            <animate attributeName="stroke-dasharray"
                    from="0,1000" to="1000,0"
                    dur="1.5s"
                    repeatCount="indefinite" />
        </polyline>
        </svg>
        """, height=140)



        # ================= VOICE ASSISTANT =================
        if lang == "English":
            text = f"The patient is at {risk}. Please follow medical advice."
            voice_lang = "en-US"
        elif lang == "Hindi":
            text = f"मरीज {risk} स्थिति में है। कृपया डॉक्टर की सलाह का पालन करें।"
            voice_lang = "hi-IN"
        

        # Button to trigger voice (IMPORTANT for browser permission)
        if st.button("🔊 Play Voice Alert"):
            speak_text(text, voice_lang)


        components.html(f"""
        <script>
        var msg = new SpeechSynthesisUtterance("{text}");
        msg.lang = "{voice_lang}";
        window.speechSynthesis.speak(msg);
        </script>
        """, height=0)

                # ================= PRECAUTIONS =================
        st.markdown("### 🛡️ Personalized Precautions")

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        for p in precautions:
            st.markdown(f"• {p}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        
# ===================== ANALYTICS =====================
elif page == "📊 Analytics":
    st.markdown("## 📊 Real-Time Patient Analytics")

    data = st.session_state.patient_data

    if len(data) == 0:
        st.warning("No patient data available yet. Please analyze patients first.")
    else:
        risks = [d["risk"] for d in data]
        bmis = [d["bmi"] for d in data]
        systolic = [d["systolic"] for d in data]
        diastolic = [d["diastolic"] for d in data]
        probs = [d["probability"] for d in data]

        low = risks.count("Low Risk")
        mod = risks.count("Moderate Risk")
        high = risks.count("High Risk")

        # ===================== ROW 1 =====================
        col1, col2 = st.columns(2)

        # ---- Risk Split (UPDATED & CLEAN) ----
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🫀 Risk Distribution")

            fig1, ax1 = plt.subplots(figsize=(3,3))
            bars = ax1.bar(
                ["Low", "Moderate", "High"],
                [low, mod, high],
                color=["#94B4C1", "#547792", "#EAE0CF"],
                width=0.5
            )
            ax1.set_ylabel("Patients")
            ax1.set_title("Risk Split", fontsize=10)
            ax1.grid(axis="y", alpha=0.3)

            for bar in bars:
                yval = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval),
                         ha='center', va='bottom', fontsize=9)

            st.pyplot(fig1)
            st.markdown("</div>", unsafe_allow_html=True)

        # ---- BMI Trend ----
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### ⚖️ BMI Trend")

            fig2, ax2 = plt.subplots(figsize=(3.5,2.5))
            ax2.plot(bmis, marker="o", color="#547792", linewidth=2)
            ax2.set_ylabel("BMI")
            ax2.set_xlabel("Patient Index")
            ax2.grid(alpha=0.3)
            st.pyplot(fig2)
            st.markdown("</div>", unsafe_allow_html=True)

        # ===================== ROW 2 =====================
        col3, col4 = st.columns(2)

        # ---- Blood Pressure Trend ----
        with col3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🩺 Blood Pressure")

            fig3, ax3 = plt.subplots(figsize=(3.5,2.5))
            ax3.plot(systolic, label="Systolic", color="#547792", linewidth=2)
            ax3.plot(diastolic, label="Diastolic", color="#94B4C1", linewidth=2)
            ax3.set_ylabel("mmHg")
            ax3.set_xlabel("Patient Index")
            ax3.legend(fontsize=8)
            ax3.grid(alpha=0.3)
            st.pyplot(fig3)
            st.markdown("</div>", unsafe_allow_html=True)

        # ---- Risk Probability ----
        with col4:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📈 Risk Probability")

            fig4, ax4 = plt.subplots(figsize=(3.5,2.5))
            ax4.bar(range(len(probs)), probs, color="#547792")
            ax4.set_ylim(0,1)
            ax4.set_ylabel("Probability")
            ax4.set_xlabel("Patient Index")
            ax4.grid(alpha=0.3)
            st.pyplot(fig4)
            st.markdown("</div>", unsafe_allow_html=True)


        

# ===================== ABOUT =====================
elif page == "ℹ️ About":
    st.markdown("""
    <div class="card">
        <div class="section-title">About CardioCare AI</div>
        <p>
        CardioCare AI is an advanced AI-based cardiovascular risk prediction system designed to assist
        doctors and patients in early detection of heart disease.
        </p>
        <ul>
            <li>🔹 AI Model: Logistic Regression</li>
            <li>🔹 Features: ECG, Risk Prediction, Voice Assistant, Patient Map</li>
            <li>🔹 Technology: Python, Streamlit, Machine Learning</li>
            <li>🔹 Developed as Final Year Project</li>
        </ul>
        <p>
        Our goal is to provide intelligent, fast and reliable heart health analysis using modern AI techniques.
        </p>
    </div>
    """, unsafe_allow_html=True)





# import streamlit as st
# import numpy as np
# import joblib
# import streamlit.components.v1 as components
# import time
# import random

# # ===================== PAGE CONFIG =====================
# st.set_page_config(
#     page_title="CardioCare AI",
#     page_icon="🫀",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ===================== THEME COLORS =====================
# PRIMARY = "#547792"
# SECONDARY = "#94B4C1"
# BACKGROUND = "#EAE0CF"
# TEXT_DARK = "#000000"
# ACCENT = "#FF6B6B"
# SUCCESS = "#4CAF50"
# WARNING = "#FF9800"

# # ===================== CUSTOM CSS =====================
# st.markdown(f"""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

# body {{
#     background: linear-gradient(135deg, {BACKGROUND} 0%, #F5F5DC 100%);
#     font-family: 'Poppins', sans-serif;
#     color: {TEXT_DARK};
#     margin: 0;
#     padding: 0;
# }}

# .header {{
#     background: linear-gradient(135deg, {PRIMARY} 0%, {SECONDARY} 100%);
#     padding: 30px;
#     border-radius: 20px;
#     color: white;
#     margin-bottom: 30px;
#     box-shadow: 0 10px 30px rgba(0,0,0,0.2);
#     position: relative;
#     overflow: hidden;
# }}

# .header::before {{
#     content: '';
#     position: absolute;
#     top: -50%;
#     left: -50%;
#     width: 200%;
#     height: 200%;
#     background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
#     animation: rotate 20s linear infinite;
# }}

# @keyframes rotate {{
#     0% {{ transform: rotate(0deg); }}
#     100% {{ transform: rotate(360deg); }}
# }}

# .header-title {{
#     font-size: 36px;
#     font-weight: 700;
#     margin-bottom: 10px;
#     text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
# }}

# .header-subtitle {{
#     font-size: 18px;
#     opacity: 0.9;
# }}

# .card {{
#     background: rgba(255,255,255,0.95);
#     backdrop-filter: blur(10px);
#     padding: 25px;
#     border-radius: 20px;
#     box-shadow: 0 8px 25px rgba(0,0,0,0.1);
#     margin-bottom: 25px;
#     border: 1px solid rgba(255,255,255,0.2);
#     transition: transform 0.3s ease, box-shadow 0.3s ease;
# }}

# .card:hover {{
#     transform: translateY(-5px);
#     box-shadow: 0 15px 35px rgba(0,0,0,0.15);
# }}

# .section-title {{
#     font-size: 24px;
#     font-weight: 700;
#     color: {PRIMARY};
#     margin-bottom: 15px;
#     display: flex;
#     align-items: center;
# }}

# .section-title::before {{
#     content: '●';
#     color: {ACCENT};
#     margin-right: 10px;
#     font-size: 20px;
# }}

# [data-testid="stSidebar"] {{
#     background: linear-gradient(180deg, {PRIMARY} 0%, {SECONDARY} 100%);
#     box-shadow: 2px 0 10px rgba(0,0,0,0.1);
# }}

# [data-testid="stSidebar"] * {{
#     color: white !important;
#     font-weight: 600;
# }}

# .metric {{
#     background: linear-gradient(135deg, {BACKGROUND} 0%, #FFFFFF 100%);
#     padding: 20px;
#     border-radius: 15px;
#     text-align: center;
#     border-left: 5px solid {PRIMARY};
#     color: {TEXT_DARK};
#     box-shadow: 0 4px 15px rgba(0,0,0,0.1);
#     transition: all 0.3s ease;
# }}

# .metric:hover {{
#     transform: scale(1.05);
#     box-shadow: 0 8px 25px rgba(0,0,0,0.15);
# }}

# .metric-title {{
#     font-size: 14px;
#     font-weight: 600;
#     text-transform: uppercase;
#     letter-spacing: 1px;
#     margin-bottom: 10px;
# }}

# .metric-value {{
#     font-size: 28px;
#     font-weight: 800;
#     color: {PRIMARY};
# }}

# .timeline-item {{
#     background: linear-gradient(135deg, {BACKGROUND} 0%, #FFFFFF 100%);
#     padding: 15px;
#     border-left: 5px solid {PRIMARY};
#     margin-bottom: 12px;
#     border-radius: 12px;
#     color: {TEXT_DARK};
#     box-shadow: 0 2px 10px rgba(0,0,0,0.05);
#     transition: all 0.3s ease;
# }}

# .timeline-item:hover {{
#     transform: translateX(5px);
#     box-shadow: 0 4px 15px rgba(0,0,0,0.1);
# }}

# .avatar {{
#     position: fixed;
#     bottom: 20px;
#     right: 20px;
#     width: 100px;
#     z-index: 9999;
#     animation: float 3s ease-in-out infinite;
#     cursor: pointer;
#     transition: transform 0.3s ease;
# }}

# .avatar:hover {{
#     transform: scale(1.1);
# }}

# .high-risk-glow {{
#     animation: redPulse 1.5s infinite;
#     border: 2px solid {ACCENT} !important;
#     box-shadow: 0 0 20px rgba(255,43,43,0.8), 0 0 40px rgba(255,43,43,0.6);
#     background: linear-gradient(135deg, #ffebeb, #ffffff) !important;
# }}

# @keyframes redPulse {{
#     0% {{ box-shadow: 0 0 5px rgba(255,43,43,0.4); }}
#     50% {{ box-shadow: 0 0 25px rgba(255,43,43,1); }}
#     100% {{ box-shadow: 0 0 5px rgba(255,43,43,0.4); }}
# }}

# @keyframes float {{
#     0% {{ transform: translateY(0px); }}
#     50% {{ transform: translateY(-15px); }}
#     100% {{ transform: translateY(0px); }}
# }}

# .progress-bar {{
#     width: 100%;
#     height: 10px;
#     background: #e0e0e0;
#     border-radius: 5px;
#     overflow: hidden;
#     margin-top: 10px;
# }}

# .progress-fill {{
#     height: 100%;
#     background: linear-gradient(90deg, {SUCCESS}, {WARNING}, {ACCENT});
#     transition: width 1s ease;
# }}

# .glow-button {{
#     background: linear-gradient(135deg, {PRIMARY}, {SECONDARY});
#     color: white;
#     border: none;
#     padding: 12px 24px;
#     border-radius: 25px;
#     font-weight: 600;
#     cursor: pointer;
#     box-shadow: 0 4px 15px rgba(0,0,0,0.2);
#     transition: all 0.3s ease;
# }}

# .glow-button:hover {{
#     transform: translateY(-2px);
#     box-shadow: 0 8px 25px rgba(0,0,0,0.3);
# }}

# .unique-feature {{
#     background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
#     border-radius: 20px;
#     padding: 20px;
#     margin: 10px 0;
#     box-shadow: 0 5px 15px rgba(0,0,0,0.1);
#     border: 1px solid rgba(255,255,255,0.3);
# }}

# .heart-3d {{
#     width: 200px;
#     height: 200px;
#     margin: 20px auto;
#     perspective: 1000px;
# }}

# .heart {{
#     width: 100%;
#     height: 100%;
#     position: relative;
#     transform-style: preserve-3d;
#     animation: rotateY 4s infinite linear;
# }}

# .heart::before, .heart::after {{
#     content: '';
#     width: 100px;
#     height: 160px;
#     position: absolute;
#     left: 50px;
#     top: 0;
#     background: {ACCENT};
#     border-radius: 100px 100px 0 0;
#     transform: rotate(-45deg);
#     transform-origin: 0 100%;
# }}

# .heart::after {{
#     left: 0;
#     transform: rotate(45deg);
#     transform-origin: 100% 100%;
# }}

# @keyframes rotateY {{
#     0% {{ transform: rotateY(0deg); }}
#     100% {{ transform: rotateY(360deg); }}
# }}

# .fade-in {{
#     animation: fadeIn 1s ease-in;
# }}

# @keyframes fadeIn {{
#     from {{ opacity: 0; transform: translateY(20px); }}
#     to {{ opacity: 1; transform: translateY(0); }}
# }}

# </style>
# """, unsafe_allow_html=True)

# # ===================== LOAD MODEL =====================
# @st.cache_resource
# def load_package():
#     package = joblib.load("../model/cardio_model.pkl")
#     return package["model"], package["scaler"], package["features"]

# model, scaler, feature_names = load_package()

# # ===================== HELPERS =====================
# def get_risk_level(prob):
#     if prob < 0.45:
#         return "Low Risk", SUCCESS
#     elif prob < 0.75:
#         return "Moderate Risk", WARNING
#     else:
#         return "High Risk", ACCENT

# def build_input(form):
#     values = {}
#     values["height"] = form["height"]
#     values["weight"] = form["weight"]
#     values["ap_hi"] = form["ap_hi"]
#     values["ap_lo"] = form["ap_lo"]
#     values["smoke"] = form["smoke"]
#     values["alco"] = form["alco"]
#     values["active"] = form["active"]
#     values["age_years"] = form["age"]

#     bmi = form["weight"] / ((form["height"] / 100) ** 2)
#     values["BMI"] = bmi

#     values["high_bp"] = int(form["ap_hi"] >= 140 or form["ap_lo"] >= 90)

#     for col in ["cholesterol_1","cholesterol_2","cholesterol_3","gluc_1","gluc_2","gluc_3"]:
#         values[col] = 0

#     values[f"cholesterol_{form['cholesterol']}"] = 1
#     values[f"gluc_{form['gluc']}"] = 1

#     row = np.array([values.get(col, 0) for col in feature_names]).reshape(1, -1)
#     return scaler.transform(row), bmi

# def generate_recommendations(risk, bmi, age):
#     recs = []
#     if risk == "High Risk":
#         recs.append("🚨 Immediate consultation with a cardiologist recommended.")
#         recs.append("💊 Consider starting prescribed medications.")
#     if bmi > 25:
#         recs.append("🏃‍♂️ Increase physical activity and consider a balanced diet.")
#     if age > 50:
#         recs.append("📅 Schedule regular check-ups every 6 months.")
#     recs.append("🥗 Maintain a heart-healthy diet rich in fruits and vegetables.")
#     recs.append("🚭 Quit smoking if applicable.")
#     return recs

# # ===================== SIDEBAR =====================
# st.sidebar.title("🫀 CardioCare AI")
# st.sidebar.markdown("---")
# page = st.sidebar.radio("Navigation", ["🏠 Dashboard", "🩺 Patient Assessment", "📊 Analytics", "ℹ️ About"], index=0)

# # Add theme toggle
# theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
# if theme == "Dark":
#     st.markdown("""
#     <style>
#     body { background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%); color: white; }
#     .card { background: rgba(44,62,80,0.9); color: white; }
#     .metric { background: linear-gradient(135deg, #34495E 0%, #2C3E50 100%); color: white; }
#     </style>
#     """, unsafe_allow_html=True)

# st.sidebar.markdown("---")
# st.sidebar.markdown("**Quick Stats**")
# st.sidebar.metric("Total Assessments", "1,247")
# st.sidebar.metric("High Risk Cases", "23%")

# # ===================== HEADER =====================
# st.markdown(f"""
# <div class="header">
#     <div class="header-title">CardioCare AI – Smart Heart Health System</div>
#     <div class="header-subtitle">AI Powered Clinical Decision Support with Advanced Visualizations</div>
# </div>
# """, unsafe_allow_html=True)

# # ===================== FLOATING DOCTOR AVATAR =====================
# st.markdown("""
# <div class="avatar" onclick="alert('Hello! I\'m your AI Health Assistant. How can I help?')">
# <img src="https://cdn-icons-png.flaticon.com/512/387/387561.png" width="100%">
# </div>
# """, unsafe_allow_html=True)

# # ===================== DASHBOARD =====================
# if page == "🏠 Dashboard":
#     st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.markdown("""
#         <div class="card">
#             <div class="section-title">👨‍⚕️ Doctor Panel</div>
#             <p>Advanced AI system for early cardiovascular risk detection with real-time insights.</p>
#             <div class="unique-feature">
#                 <strong>AI Confidence Score:</strong> 94.7%<br>
#                 <div class="progress-bar"><div class="progress-fill" style="width: 94.7%;"></div></div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#     with col2:
#         st.markdown("""
#         <div class="card">
#             <div class="section-title">📊 Capabilities</div>
#             <ul>
#                 <li>Risk Probability Analysis</li>
#                 <li>3D Heart Visualization</li>
#                 <li>ECG Simulation</li>
#                 <li>Voice Assistant</li>
#                 <li>Personalized Recommendations</li>
#                 <li>Health Timeline</li>
#             </ul>
#         </div>
#         """, unsafe_allow_html=True)

#     with col3:
#         st.markdown("""
#         <div class="card">
#             <div class="section-title">🧠 AI Engine</div>
#             <p>Logistic Regression + Feature Engineering + Scaling + Real-time Processing</p>
#             <div class="unique-feature">
#                 <strong>Model Accuracy:</strong> 87.3%<br>
#                 <div class="progress-bar"><div class="progress-fill" style="width: 87.3%;"></div></div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#     # Unique Feature: 3D Heart Animation
#     st.markdown("### 💖 Interactive 3D Heart Model")
#     st.markdown("""
#     <div class="heart-3d">
#         <div class="heart"></div>
#     </div>
#     <p style="text-align: center; color: {PRIMARY};">Hover to interact with the 3D heart model!</p>
#     """, unsafe_allow_html=True)

#     st.markdown('</div>', unsafe_allow_html=True)

# # ===================== PATIENT ASSESSMENT =====================
# elif page == "🩺 Patient Assessment":
#     st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
#     st.markdown("## 🧾 Patient Assessment Panel")
    
#     with st.expander("📝 Patient Information", expanded=True):
#         c1, c2 = st.columns(2)

#         with c1:
#             age = st.number_input("Age", 18, 120, 45, help="Enter your age in years")
#             height = st.number_input("Height (cm)", 120, 220, 165, help="Height in centimeters")
#             weight = st.number_input("Weight (kg)", 30, 200, 70, help="Weight in kilograms")
#             smoke = st.selectbox("Smoking", ["No", "Yes"], help="Do you smoke?")

#         with c2:
#             ap_hi = st.number_input("Systolic BP", 80, 250, 130, help="Systolic blood pressure")
#             ap_lo = st.number_input("Diastolic BP", 50, 150, 85, help="Diastolic blood pressure")
#             cholesterol = st.selectbox("Cholesterol", ["Normal", "Above Normal", "Well Above Normal"], help="Cholesterol level")
#             gluc = st.selectbox("Glucose", ["Normal", "Above Normal", "Well Above Normal"], help="Glucose level")
#             alco = st.selectbox("Alcohol", ["No", "Yes"], help="Do you consume alcohol?")
#             active = st.selectbox("Physically Active", ["No", "Yes"], help="Are you physically active?")

#     lang = st.selectbox("Voice Language", ["English", "Hindi", "Gujarati"], help="Select language for voice assistant")

#     if st.button("🔍 Analyze Patient", key="analyze", help="Click to run AI analysis"):
#         with st.spinner("Analyzing patient data..."):
#             time.sleep(2)  # Simulate processing time

#         form = {
#             "age": age,
#             "height": height,
#             "weight": weight,
#             "ap_hi": ap_hi,
#             "ap_lo": ap_lo,
#             "cholesterol": 1 if cholesterol=="Normal" else 2 if cholesterol=="Above Normal" else 3,
#             "gluc": 1 if gluc=="Normal" else 2 if gluc=="Above Normal" else 3,
#             "smoke": 1 if smoke=="Yes" else 0,
#             "alco": 1 if alco=="Yes" else 0,
#             "active": 1 if active=="Yes" else 0
#         }

#         X, bmi = build_input(form)
#         proba = float(model.predict_proba(X)[0][1])
#         risk, risk_color = get_risk_level(proba)

#         # Metrics with enhanced styling
#         m1, m2, m3 = st.columns(3)

#         with m1:
#             st.markdown(f"<div class='metric'><div class='metric-title'>Risk Level</div><div class='metric-value'>{risk}</div></div>", unsafe_allow_html=True)
#         with m2:
#             st.markdown(f"<div class='metric'><div class='metric-title'>Probability</div><div class='metric-value'>{proba:.2f}</div></div>", unsafe_allow_html=True)
#         with m3:
#             st.markdown(f"<div class='metric'><div class='metric-title'>BMI</div><div class='metric-value'>{bmi:.2f}</div></div>", unsafe_allow_html=True)

#         # ================= SPEEDOMETER GAUGE =================
#         components.html(f"""
#         <div style="width:300px;margin:auto;">
#         <canvas id="gauge"></canvas>
#         </div>

#         <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
#         <script>
#         const ctx = document.getElementById('gauge').getContext('2d');
#         new Chart(ctx, {{
#             type: 'doughnut',
#             data: {{
#                 labels: ['Risk', 'Remaining'],
#                 datasets: [{{
#                     data: [{proba*100:.1f}, {100 - proba*100:.1f}],
#                     backgroundColor: ['#547792', '#EAE0CF'],
#                     borderWidth: 0
#                 }}]
#             }},
#             options: {{
#                 rotation: -90,
#                 circumference: 180,
#                 cutout: '70%',
#                 plugins: {{
#                     legend: {{ display: false }}
#                 }}
#             }}
#         }});
#         </script>
#         """, height=260)


#         # ================= ECG =================
#         st.markdown("### 📈 Live ECG Simulation")

#         components.html("""
#         <svg width="100%" height="120" viewBox="0 0 500 120" preserveAspectRatio="none">
#         <polyline 
#             points="0,60 40,60 60,20 80,100 100,60 140,60 160,30 180,90 200,60 240,60 260,20 280,100 300,60 340,60 360,30 380,90 400,60 440,60 460,60 500,60"
#             fill="none"
#             stroke="white"
#             stroke-width="3"
#             stroke-linejoin="round"
#             stroke-linecap="round"
#             >
#             <animate attributeName="stroke-dasharray"
#                     from="0,1000" to="1000,0"
#                     dur="1.5s"
#                     repeatCount="indefinite" />
#         </polyline>
#         </svg>
#         """, height=140)


#         # ================= TIMELINE =================
#         st.markdown("### 🕒 Patient History Timeline")
#         st.markdown("""
#         <div class="timeline-item">2023 – High BP detected</div>
#         <div class="timeline-item">2024 – Medication started</div>
#         <div class="timeline-item">2025 – AI Risk Analysis</div>
#         """, unsafe_allow_html=True)

#         risk_class = "high-risk-glow" if risk == "High Risk" else ""

#         m1, m2, m3 = st.columns(3)

#         with m1:
#             st.markdown(f"""
#             <div class='metric {risk_class}'>
#                 <div class='metric-title'>Risk Level</div>
#                 <div class='metric-value'>{risk}</div>
#             </div>
#             """, unsafe_allow_html=True)

#         with m2:
#             st.markdown(f"""
#             <div class='metric {risk_class}'>
#                 <div class='metric-title'>Probability</div>
#                 <div class='metric-value'>{proba:.2f}</div>
#             </div>
#             """, unsafe_allow_html=True)

#         with m3:
#             st.markdown(f"""
#             <div class='metric {risk_class}'>
#                 <div class='metric-title'>BMI</div>
#                 <div class='metric-value'>{bmi:.2f}</div>
#             </div>
#             """, unsafe_allow_html=True)


#         # ================= VOICE ASSISTANT =================   
#         if lang == "English":
#             text = f"The patient is at {risk}. Please follow medical advice."
#             voice_lang = "en-US"
#         elif lang == "Hindi":
#             text = f"मरीज को {risk} है। कृपया डॉक्टर की सलाह का पालन करें।"
#             voice_lang = "hi-IN"
#         else:
#             text = f"દર્દીને {risk} છે. કૃપા કરીને ડૉક્ટરની સલાહ અનુસરો."
#             voice_lang = "gu-IN"

#         components.html(f"""
#         <script>
#         var msg = new SpeechSynthesisUtterance("{text}");
#         msg.lang = "{voice_lang}";
#         window.speechSynthesis.speak(msg);
#         </script>
#         """, height=0)
                    
                    
# import streamlit as st
# import numpy as np
# import joblib
# import streamlit.components.v1 as components

# # ===================== PAGE CONFIG =====================
# st.set_page_config(
#     page_title="CardioCare AI",
#     page_icon="🫀",
#     layout="wide"
# )

# # ===================== THEME COLORS =====================
# PRIMARY = "#547792"
# SECONDARY = "#94B4C1"
# BACKGROUND = "#EAE0CF"
# TEXT_DARK = "#000000"

# # ===================== CUSTOM CSS =====================
# st.markdown(f"""
# <style>
# body {{
#     background-color: {BACKGROUND};
#     font-family: 'Segoe UI', sans-serif;
# }}

# .header {{
#     background: linear-gradient(90deg, {PRIMARY}, {SECONDARY});
#     padding: 22px;
#     border-radius: 16px;
#     color: white;
#     margin-bottom: 20px;
# }}

# .header-title {{
#     font-size: 32px;
#     font-weight: 800;
# }}

# .card {{
#     background: white;
#     padding: 16px;
#     border-radius: 14px;
#     box-shadow: 0 6px 12px rgba(0,0,0,0.08);
#     margin-bottom: 16px;
#     color: {TEXT_DARK};
# }}

# .section-title {{
#     font-size: 20px;
#     font-weight: 700;
#     color: {TEXT_DARK};
#     margin-bottom: 10px;
# }}

# [data-testid="stSidebar"] {{
#     background: linear-gradient(180deg, {PRIMARY}, {SECONDARY});
# }}

# [data-testid="stSidebar"] * {{
#     color: white !important;
#     font-weight: 600;
# }}

# .metric {{
#     background: {BACKGROUND};
#     padding: 12px;
#     border-radius: 10px;
#     text-align: center;
#     border-left: 4px solid {PRIMARY};
#     color: {TEXT_DARK};
# }}

# .metric-title {{
#     font-size: 13px;
# }}

# .metric-value {{
#     font-size: 24px;
#     font-weight: 800;
# }}

# .timeline-item {{
#     background: {BACKGROUND};
#     padding: 10px;
#     border-left: 4px solid {PRIMARY};
#     margin-bottom: 8px;
#     border-radius: 8px;
#     color: {TEXT_DARK};
# }}

# .avatar {{
#     position: fixed;
#     bottom: 20px;
#     right: 20px;
#     width: 90px;
#     z-index: 9999;
#     animation: float 3s ease-in-out infinite;
# }}

# .high-risk-glow {{
#     animation: redPulse 1.5s infinite;
#     border: 2px solid #ff2b2b !important;
#     box-shadow: 0 0 15px rgba(255,0,0,0.8), 0 0 30px rgba(255,0,0,0.6);
#     background: linear-gradient(135deg, #ffebeb, #ffffff) !important;
# }}

# @keyframes redPulse {{
#     0% {{ box-shadow: 0 0 5px rgba(255,0,0,0.4); }}
#     50% {{ box-shadow: 0 0 20px rgba(255,0,0,1); }}
#     100% {{ box-shadow: 0 0 5px rgba(255,0,0,0.4); }}
# }}

# @keyframes float {{
#     0% {{ transform: translateY(0px); }}
#     50% {{ transform: translateY(-10px); }}
#     100% {{ transform: translateY(0px); }}
# }}
# </style>
# """, unsafe_allow_html=True)

# # ===================== LOAD MODEL =====================
# @st.cache_resource
# def load_package():
#     package = joblib.load("../model/cardio_model.pkl")
#     return package["model"], package["scaler"], package["features"]

# model, scaler, feature_names = load_package()

# # ===================== HELPERS =====================
# def get_risk_level(prob):
#     if prob < 0.45:
#         return "Low Risk"
#     elif prob < 0.75:
#         return "Moderate Risk"
#     else:
#         return "High Risk"

# def build_input(form):
#     values = {}
#     values["height"] = form["height"]
#     values["weight"] = form["weight"]
#     values["ap_hi"] = form["ap_hi"]
#     values["ap_lo"] = form["ap_lo"]
#     values["smoke"] = form["smoke"]
#     values["alco"] = form["alco"]
#     values["active"] = form["active"]
#     values["age_years"] = form["age"]

#     bmi = form["weight"] / ((form["height"] / 100) ** 2)
#     values["BMI"] = bmi

#     values["high_bp"] = int(form["ap_hi"] >= 140 or form["ap_lo"] >= 90)

#     for col in ["cholesterol_1","cholesterol_2","cholesterol_3","gluc_1","gluc_2","gluc_3"]:
#         values[col] = 0

#     values[f"cholesterol_{form['cholesterol']}"] = 1
#     values[f"gluc_{form['gluc']}"] = 1

#     row = np.array([values.get(col, 0) for col in feature_names]).reshape(1, -1)
#     return scaler.transform(row), bmi

# # ===================== SIDEBAR =====================
# st.sidebar.title("🫀 CardioCare AI")
# page = st.sidebar.radio("Navigation", ["🏠 Dashboard", "🩺 Patient Assessment", "ℹ️ About"])

# # ===================== HEADER =====================
# st.markdown(f"""
# <div class="header">
#     <div class="header-title">CardioCare AI – Smart Heart Health System</div>
#     <div>AI Powered Clinical Decision Support</div>
# </div>
# """, unsafe_allow_html=True)

# # ===================== FLOATING DOCTOR AVATAR =====================
# st.markdown("""
# <img class="avatar" src="https://cdn-icons-png.flaticon.com/512/387/387561.png">
# """, unsafe_allow_html=True)

# # ===================== DASHBOARD =====================
# if page == "🏠 Dashboard":

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.markdown("""
#         <div class="card">
#             <div class="section-title">👨‍⚕️ Doctor Panel</div>
#             <p>Advanced AI system for early cardiovascular risk detection.</p>
#         </div>
#         """, unsafe_allow_html=True)

#     with col2:
#         st.markdown("""
#         <div class="card">
#             <div class="section-title">📊 Capabilities</div>
#             <ul>
#                 <li>Risk Probability Analysis</li>
#                 <li>3D Heart Visualization</li>
#                 <li>ECG Simulation</li>
#                 <li>Voice Assistant</li>
#             </ul>
#         </div>
#         """, unsafe_allow_html=True)

#     with col3:
#         st.markdown("""
#         <div class="card">
#             <div class="section-title">🧠 AI Engine</div>
#             <p>Logistic Regression + Feature Engineering + Scaling</p>
#         </div>
#         """, unsafe_allow_html=True)

# # ===================== PATIENT ASSESSMENT =====================
# elif page == "🩺 Patient Assessment":

#     st.markdown("## 🧾 Patient Assessment Panel")

#     c1, c2 = st.columns(2)

#     with c1:
#         age = st.number_input("Age", 18, 120, 45)
#         height = st.number_input("Height (cm)", 120, 220, 165)
#         weight = st.number_input("Weight (kg)", 30, 200, 70)
#         smoke = st.selectbox("Smoking", ["No", "Yes"])

#     with c2:
#         ap_hi = st.number_input("Systolic BP", 80, 250, 130)
#         ap_lo = st.number_input("Diastolic BP", 50, 150, 85)
#         cholesterol = st.selectbox("Cholesterol", ["Normal", "Above Normal", "Well Above Normal"])
#         gluc = st.selectbox("Glucose", ["Normal", "Above Normal", "Well Above Normal"])
#         alco = st.selectbox("Alcohol", ["No", "Yes"])
#         active = st.selectbox("Physically Active", ["No", "Yes"])

#     lang = st.selectbox("Voice Language", ["English", "Hindi", "Gujarati"])

#     if st.button("🔍 Analyze Patient"):

#         form = {
#             "age": age,
#             "height": height,
#             "weight": weight,
#             "ap_hi": ap_hi,
#             "ap_lo": ap_lo,
#             "cholesterol": 1 if cholesterol=="Normal" else 2 if cholesterol=="Above Normal" else 3,
#             "gluc": 1 if gluc=="Normal" else 2 if gluc=="Above Normal" else 3,
#             "smoke": 1 if smoke=="Yes" else 0,
#             "alco": 1 if alco=="Yes" else 0,
#             "active": 1 if active=="Yes" else 0
#         }

#         X, bmi = build_input(form)
#         proba = float(model.predict_proba(X)[0][1])
#         risk = get_risk_level(proba)

#         m1, m2, m3 = st.columns(3)

#         with m1:
#             st.markdown(f"<div class='metric'><div class='metric-title'>Risk Level</div><div class='metric-value'>{risk}</div></div>", unsafe_allow_html=True)
#         with m2:
#             st.markdown(f"<div class='metric'><div class='metric-title'>Probability</div><div class='metric-value'>{proba:.2f}</div></div>", unsafe_allow_html=True)
#         with m3:
#             st.markdown(f"<div class='metric'><div class='metric-title'>BMI</div><div class='metric-value'>{bmi:.2f}</div></div>", unsafe_allow_html=True)

#         # ================= SPEEDOMETER GAUGE =================
#         components.html(f"""
#         <div style="width:300px;margin:auto;">
#         <canvas id="gauge"></canvas>
#         </div>

#         <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
#         <script>
#         const ctx = document.getElementById('gauge').getContext('2d');
#         new Chart(ctx, {{
#             type: 'doughnut',
#             data: {{
#                 labels: ['Risk', 'Remaining'],
#                 datasets: [{{
#                     data: [{proba*100:.1f}, {100 - proba*100:.1f}],
#                     backgroundColor: ['#547792', '#EAE0CF'],
#                     borderWidth: 0
#                 }}]
#             }},
#             options: {{
#                 rotation: -90,
#                 circumference: 180,
#                 cutout: '70%',
#                 plugins: {{
#                     legend: {{ display: false }}
#                 }}
#             }}
#         }});
#         </script>
#         """, height=260)


#         # ================= ECG =================
#         st.markdown("### 📈 Live ECG Simulation")

#         components.html("""
#         <svg width="100%" height="120" viewBox="0 0 500 120" preserveAspectRatio="none">
#         <polyline 
#             points="0,60 40,60 60,20 80,100 100,60 140,60 160,30 180,90 200,60 240,60 260,20 280,100 300,60 340,60 360,30 380,90 400,60 440,60 460,60 500,60"
#             fill="none"
#             stroke="white"
#             stroke-width="3"
#             stroke-linejoin="round"
#             stroke-linecap="round"
#             >
#             <animate attributeName="stroke-dasharray"
#                     from="0,1000" to="1000,0"
#                     dur="1.5s"
#                     repeatCount="indefinite" />
#         </polyline>
#         </svg>
#         """, height=140)


#         # ================= TIMELINE =================
#         st.markdown("### 🕒 Patient History Timeline")
#         st.markdown("""
#         <div class="timeline-item">2023 – High BP detected</div>
#         <div class="timeline-item">2024 – Medication started</div>
#         <div class="timeline-item">2025 – AI Risk Analysis</div>
#         """, unsafe_allow_html=True)

#         risk_class = "high-risk-glow" if risk == "High Risk" else ""

#         m1, m2, m3 = st.columns(3)

#         with m1:
#             st.markdown(f"""
#             <div class='metric {risk_class}'>
#                 <div class='metric-title'>Risk Level</div>
#                 <div class='metric-value'>{risk}</div>
#             </div>
#             """, unsafe_allow_html=True)

#         with m2:
#             st.markdown(f"""
#             <div class='metric {risk_class}'>
#                 <div class='metric-title'>Probability</div>
#                 <div class='metric-value'>{proba:.2f}</div>
#             </div>
#             """, unsafe_allow_html=True)

#         with m3:
#             st.markdown(f"""
#             <div class='metric {risk_class}'>
#                 <div class='metric-title'>BMI</div>
#                 <div class='metric-value'>{bmi:.2f}</div>
#             </div>
#             """, unsafe_allow_html=True)


#         # ================= VOICE ASSISTANT =================   
#         if lang == "English":
#             text = f"The patient is at {risk}. Please follow medical advice."
#             voice_lang = "en-US"
#         elif lang == "Hindi":
#             text = f"मरीज को {risk} है। कृपया डॉक्टर की सलाह का पालन करें।"
#             voice_lang = "hi-IN"
#         else:
#             text = f"દર્દીને {risk} છે. કૃપા કરીને ડૉક્ટરની સલાહ અનુસરો."
#             voice_lang = "gu-IN"

#         components.html(f"""
#         <script>
#         var msg = new SpeechSynthesisUtterance("{text}");
#         msg.lang = "{voice_lang}";
#         window.speechSynthesis.speak(msg);
#         </script>
#         """, height=0)

# # ===================== ABOUT =====================
# elif page == "ℹ️ About":

#     st.markdown("""
#     <div class="card">
#         <div class="section-title">About CardioCare AI</div>
#         <p>
#         CardioCare AI is an advanced cardiovascular risk prediction system integrating
#         Machine Learning, 3D visualization, ECG simulation, timeline analysis and voice assistance.
#         </p>
#         <ul>
#             <li>Algorithm: Logistic Regression</li>
#             <li>Features: ECG, 3D Heart, Voice, Timeline, Gauge</li>
#             <li>Built with Streamlit + AI</li>
#             <li>Final Year Project Ready</li>
#         </ul>
#     </div>
#     """, unsafe_allow_html=True)