import pandas as pd
import requests
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="FloodGuard AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://localhost:5000"
LOGIN_BG_URL = "https://t4.ftcdn.net/jpg/20/84/78/43/360_F_2084784353_zIzvolI5TGX9BbgYHDOHYkL9GnvYUOQH.jpg"

LOCATIONS = {
    "Jalpaiguri": {"id": "jalpaiguri", "district": "Jalpaiguri", "station": "IMD Jalpaiguri", "lat": 26.5167, "lon": 88.7333},
    "Cooch Behar": {"id": "cooch-behar", "district": "Cooch Behar", "station": "IMD Cooch Behar", "lat": 26.3452, "lon": 89.4482},
    "Alipurduar": {"id": "alipurduar", "district": "Alipurduar", "station": "IMD Alipurduar", "lat": 26.4919, "lon": 89.5271},
    "Kalimpong": {"id": "kalimpong", "district": "Kalimpong", "station": "IMD Kalimpong", "lat": 27.0667, "lon": 88.4667},
    "Malda": {"id": "malda", "district": "Malda", "station": "IMD Malda", "lat": 25.0108, "lon": 88.1411},
    "Kolkata": {"id": "kolkata", "district": "Kolkata", "station": "IMD Kolkata", "lat": 22.5726, "lon": 88.3639},
}

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "selected_district" not in st.session_state:
    st.session_state.selected_district = "Jalpaiguri"
if "environmental_data" not in st.session_state:
    st.session_state.environmental_data = None
if "prediction" not in st.session_state:
    st.session_state.prediction = None

# Mock Database
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "admin@floodguard.ai": {"password": "adminpassword", "name": "System Admin", "district": "Jalpaiguri"}
    }

# ============================================================
# GLOBAL CSS
# ============================================================
def load_global_css():
    st.markdown(
        """
        <style>
        .stApp { background: radial-gradient(circle at 90% 0%, rgba(0, 188, 212, 0.12), transparent 30%), #07141d; color: white; }
        header { visibility: hidden; }
        .block-container { max-width: 1250px; padding-top: 2rem; }
        [data-testid="stSidebar"] { background: #061019; }
        .brand { display: flex; align-items: center; gap: 14px; margin-bottom: 30px; }
        .logo { width: 52px; height: 52px; border-radius: 16px; background: linear-gradient(135deg, #00bcd4, #216cff); display: flex; align-items: center; justify-content: center; font-size: 27px; }
        .brand-title { font-size: 25px; font-weight: 800; }
        .brand-subtitle { color: #78909c; font-size: 11px; }
        .hero { padding: 45px; border-radius: 28px; background: linear-gradient(135deg, rgba(0, 188, 212, 0.14), rgba(33, 108, 255, 0.05)); border: 1px solid rgba(255, 255, 255, 0.07); margin-bottom: 30px; }
        .hero-label { color: #00c9df; font-size: 11px; font-weight: 800; letter-spacing: 2px; }
        .hero-title { font-size: 50px; font-weight: 800; line-height: 1.05; margin-top: 15px; }
        .hero-title span { color: #00c9df; }
        .hero-text { color: #8da5b1; max-width: 720px; line-height: 1.7; margin-top: 15px; }
        .section { font-size: 22px; font-weight: 800; margin-top: 35px; margin-bottom: 18px; }
        .card { background: rgba(13, 31, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 20px; padding: 22px; min-height: 135px; margin-bottom: 15px; }
        .card-icon { font-size: 27px; }
        .card-label { color: #78909c; font-size: 11px; font-weight: 700; letter-spacing: 1px; margin-top: 8px; }
        .card-value { font-size: 25px; font-weight: 800; margin-top: 7px; }
        .prediction { text-align: center; padding: 35px; border-radius: 25px; background: rgba(13, 31, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); min-height: 250px; }
        .probability { font-size: 60px; font-weight: 900; }
        .high { color: #ff5c5c; font-weight: 800; }
        .medium { color: #f2b84b; font-weight: 800; }
        .low { color: #55d69a; font-weight: 800; }
        .footer { margin-top: 50px; padding-top: 25px; border-top: 1px solid rgba(255, 255, 255, 0.06); color: #526a76; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# BACKEND & HELPER FUNCTIONS
# ============================================================
def check_backend():
    try: return requests.get(f"{BACKEND_URL}/", timeout=10).json()
    except Exception as e: return {"error": str(e)}

def fetch_live_data(location_id):
    try: return requests.get(f"{BACKEND_URL}/api/data", params={"location": location_id}, timeout=120).json()
    except Exception as e: return {"error": str(e)}

def run_prediction(payload):
    try: return requests.post(f"{BACKEND_URL}/api/predict", json=payload, timeout=120).json()
    except Exception as e: return {"error": str(e)}

def get_value(data, possible_keys):
    if not isinstance(data, dict): return None
    for key in possible_keys:
        if key in data and data[key] is not None: return data[key]
    return None

def safe_float(value, default=0.0):
    try: return float(value) if value is not None else default
    except (ValueError, TypeError): return default

def format_value(data, unit=""):
    if data is None: return "--"
    try: return f"{float(data):.2f} {unit}"
    except (ValueError, TypeError): return f"{data} {unit}"

# ============================================================
# LOGIN PAGE COMPONENT
# ============================================================
def login_page():
    st.markdown(
        f"""
        <style>
        .stApp {{ background: linear-gradient(135deg, rgba(20, 10, 40, 0.65), rgba(45, 10, 75, 0.75)), url("{LOGIN_BG_URL}"); background-size: cover; background-position: center; }}
        [data-testid="stVerticalBlock"] > div:has(div.stTabs) {{ background: rgba(125, 60, 180, 0.25); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px); border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 28px; padding: 35px; }}
        .stTextInput > div > div > input, .stSelectbox > div > div {{ background-color: rgba(255, 255, 255, 0.1) !important; color: #ffffff !important; border-radius: 12px !important; }}
        .stButton > button {{ border-radius: 12px !important; background: linear-gradient(135deg, #ffffff, #e0e0e0) !important; color: #2e0854 !important; font-weight: 700 !important; border: none !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, col2, _ = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-bottom: 10px; color: white;'>🌊 FloodGuard AI</h1>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:
            login_email = st.text_input("Email", key="login_email")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            selected_district = st.selectbox("📍 Select Initial Location", list(LOCATIONS.keys()), key="login_district")

            if st.button("Login", use_container_width=True):
                user_db = st.session_state.user_db
                if login_email in user_db and user_db[login_email]["password"] == login_pass:
                    # Update state and instantly redirect
                    st.session_state.logged_in = True
                    st.session_state.selected_district = selected_district
                    st.session_state.user_info = {
                        "email": login_email,
                        "name": user_db[login_email]["name"]
                    }
                    st.rerun() # This reloads the script and jumps to dashboard_page()
                else:
                    st.error("Invalid email or password.")

        with tab_signup:
            signup_name = st.text_input("Full Name", key="signup_name")
            signup_email = st.text_input("Email", key="signup_email")
            signup_pass = st.text_input("Password", type="password", key="signup_pass")
            signup_dist = st.selectbox("📍 Select Location", list(LOCATIONS.keys()), key="signup_dist")

            if st.button("Register", use_container_width=True):
                if signup_email in st.session_state.user_db:
                    st.error("Email already registered.")
                else:
                    st.session_state.user_db[signup_email] = {"password": signup_pass, "name": signup_name, "district": signup_dist}
                    st.success("Account created! Switch tabs to login.")

# ============================================================
# DASHBOARD PAGE COMPONENT
# ============================================================
def dashboard_page():
    load_global_css()
    
    district_list = list(LOCATIONS.keys())
    default_index = district_list.index(st.session_state.selected_district) if st.session_state.selected_district in district_list else 0

    # SIDEBAR
    with st.sidebar:
        st.markdown("""<div class="brand"><div class="logo">🌊</div><div><div class="brand-title">FloodGuard</div></div></div>""", unsafe_allow_html=True)
        st.write(f"👤 **{st.session_state.user_info['name']}**")
        
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

        st.divider()
        selected_name = st.selectbox("📍 Switch Location", district_list, index=default_index, key="dash_location")
        st.session_state.selected_district = selected_name
        location = LOCATIONS[selected_name]

    # HERO
    st.markdown(
        f"""<div class="hero">
            <div class="hero-label">AI-POWERED ENVIRONMENTAL INTELLIGENCE</div>
            <div class="hero-title">West Bengal<br><span>{location['district']} Risk Intelligence</span></div>
        </div>""",
        unsafe_allow_html=True,
    )

    # LOCATION CARDS
    st.markdown('<div class="section">📍 Location Overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="card"><div class="card-icon">📍</div><div class="card-label">DISTRICT</div><div class="card-value">{location["district"]}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><div class="card-icon">🛰️</div><div class="card-label">STATION</div><div class="card-value">{location["station"]}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><div class="card-icon">🗺️</div><div class="card-label">COORDS</div><div class="card-value">{location["lat"]}, {location["lon"]}</div></div>', unsafe_allow_html=True)

    # DATA FETCHING
    st.markdown('<div class="section">🌧️ Environmental Monitoring</div>', unsafe_allow_html=True)
    if st.button("🔄 Fetch Latest Data", use_container_width=True):
        with st.spinner("Fetching data..."):
            result = fetch_live_data(location["id"])
            if "error" not in result:
                st.session_state.environmental_data = result
                st.session_state.prediction = result.get("environmentalData", {}).get("floodPrediction")
                st.rerun()
            else:
                st.error(result["error"])

    env_data = st.session_state.environmental_data.get("environmentalData", {}) if st.session_state.environmental_data else {}
    
    # METRICS
    st.markdown('<div class="section">🌦️ Weather Conditions</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    metrics = [
        ("🌧️", "RAIN 1H", get_value(env_data, ["rainfall", "rainfall_1h_mm"]), "mm"),
        ("🌡️", "TEMP", get_value(env_data, ["temperature", "temperature_c"]), "°C"),
        ("💧", "HUMIDITY", get_value(env_data, ["humidity", "humidity_pct"]), "%"),
        ("🌱", "SOIL", get_value(env_data, ["soilMoisture", "soil_moisture_pct"]), "%")
    ]
    for idx, (icon, label, val, unit) in enumerate(metrics):
        with cols[idx]:
            st.markdown(f'<div class="card"><div class="card-icon">{icon}</div><div class="card-label">{label}</div><div class="card-value">{format_value(val, unit)}</div></div>', unsafe_allow_html=True)

    # PREDICTION
    st.markdown('<div class="section">🤖 AI Flood Prediction</div>', unsafe_allow_html=True)
    prediction = st.session_state.prediction
    if isinstance(prediction, dict):
        risk = str(prediction.get("riskLevel", "UNKNOWN")).upper()
        prob = float(prediction.get("floodProbability", prediction.get("probability", 0))) * 100
        css = "high" if risk == "HIGH" else "medium" if risk == "MEDIUM" else "low"
        icon = "🔴" if risk == "HIGH" else "🟡" if risk == "MEDIUM" else "🟢"
        
        st.markdown(
            f"""<div class="prediction">
                <div class="card-label">FLOOD PROBABILITY</div>
                <div class="probability">{prob:.2f}%</div>
                <div class="{css}">{icon} {risk} RISK</div>
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.info("Run model or fetch data to see predictions.")

# ============================================================
# APP ROUTER (Main Execution)
# ============================================================
if not st.session_state.logged_in:
    login_page()
else:
    dashboard_page()