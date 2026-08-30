import json
import os
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / "backend" / ".env")

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

BACKEND_URL = "https://flood-prediction-system-ew0d.onrender.com"
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

```python
def fetch_live_data(location_id):
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/data",
            params={"location": location_id},
            timeout=120
        )

        if response.status_code != 200:
            return {
                "error": f"Backend returned HTTP {response.status_code}",
                "details": response.text[:1000]
            }

        try:
            return response.json()

        except ValueError:
            return {
                "error": "Backend returned a non-JSON response.",
                "details": response.text[:1000]
            }

        except requests.exceptions.RequestException as e:
            return {
            "error": "Could not connect to backend.",
            "details": str(e)
            }
```


def run_prediction(payload):
    try: return requests.post(f"{BACKEND_URL}/api/predict", json=payload, timeout=120).json()
    except Exception as e: return {"error": str(e)}

def get_value(data, possible_keys):
    if not isinstance(data, dict): return None
    for key in possible_keys:
        if key in data and data[key] is not None: return data[key]
    return None

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 21914)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl_disabled=False
        )
    except mysql.connector.Error as error:
        st.error(f"Database connection failed: {error}")
        return None

def safe_float(value, default=0.0):
    try: return float(value) if value is not None else default
    except (ValueError, TypeError): return default

def format_value(data, unit=""):
    if data is None: return "--"
    try: return f"{float(data):.2f} {unit}"
    except (ValueError, TypeError): return f"{data} {unit}"

def register_user(name, email, password, district):
    """Store a newly registered user permanently in MySQL."""
    connection = get_db_connection()

    if connection is None:
        return False, "Could not connect to database."

    try:
        cursor = connection.cursor()

        # Check whether the email already exists
        cursor.execute(
            "SELECT email FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return False, "Email already registered."

        # Insert the new user
        cursor.execute(
            """
            INSERT INTO users (name, email, password, district)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, password, district)
        )

        connection.commit()

        return True, "Account created successfully."

    except mysql.connector.Error as error:
        return False, f"Registration failed: {error}"

    finally:
        cursor.close()
        connection.close()
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
            login_pass = st.text_input(
                "Password",
                type="password",
                key="login_pass"
            )
            selected_district = st.selectbox(
                "📍 Select Initial Location",
                list(LOCATIONS.keys()),
                key="login_district"
            )

            if st.button("Login", use_container_width=True):

                connection = get_db_connection()

                if connection is None:
                    st.error("Unable to connect to database.")

                else:
                    cursor = None

                    try:
                        cursor = connection.cursor(dictionary=True)

                        # Find the registered user by email
                        cursor.execute(
                            """
                            SELECT id, name, email, district, password
                            FROM users
                            WHERE email = %s
                            """,
                            (login_email.strip(),)
                        )

                        user = cursor.fetchone()

                        if user and user["password"] == login_pass:

                            st.session_state.logged_in = True

                            # Use the district stored in MySQL
                            st.session_state.selected_district = user["district"]

                            st.session_state.user_info = {
                                "email": user["email"],
                                "name": user["name"],
                                "district": user["district"]
                            }

                            st.rerun()

                        else:
                            st.error("Invalid email or password.")

                    except mysql.connector.Error as error:
                        st.error(f"Login failed: {error}")

                    finally:
                        if cursor:
                            cursor.close()

                        connection.close()

        with tab_signup:
            signup_name = st.text_input(
                "Full Name",
                key="signup_name"
            )

            signup_email = st.text_input(
                "Email",
                key="signup_email"
            )

            signup_pass = st.text_input(
                "Password",
                type="password",
                key="signup_pass"
            )

            signup_dist = st.selectbox(
                "📍 Select Location",
                list(LOCATIONS.keys()),
                key="signup_dist"
            )

            if st.button("Register", use_container_width=True):

                if not signup_name.strip():
                    st.error("Please enter your name.")

                elif not signup_email.strip():
                    st.error("Please enter your email.")

                elif not signup_pass:
                    st.error("Please enter a password.")

                else:

                    success, message = register_user(
                        signup_name.strip(),
                        signup_email.strip(),
                        signup_pass,
                        signup_dist
                    )

                    if success:
                        st.success(
                            "Account created! Switch to the Login tab."
                        )

                    else:
                        st.error(message)

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
        st.markdown("### 📍 Select Location")
        selected_name = st.selectbox("District", district_list, index=default_index, key="dash_location")
        st.session_state.selected_district = selected_name
        location = LOCATIONS[selected_name]

    # HERO
    st.markdown(
        f"""<div class="hero">
            <div class="hero-label">AI-POWERED ENVIRONMENTAL INTELLIGENCE</div>
            <div class="hero-title">West Bengal<br><span>{location['district']} Risk Intelligence</span></div>
            <div class="hero-text">
                Monitor rainfall, weather conditions, river information 
                and machine-learning predictions for selected locations across West Bengal.
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # LOCATION OVERVIEW
    st.markdown('<div class="section">📍 Location Overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="card"><div class="card-icon">📍</div><div class="card-label">DISTRICT</div><div class="card-value">{location["district"]}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><div class="card-icon">🛰️</div><div class="card-label">STATION</div><div class="card-value">{location["station"]}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><div class="card-icon">🗺️</div><div class="card-label">COORDS</div><div class="card-value">{location["lat"]:.4f}, {location["lon"]:.4f}</div></div>', unsafe_allow_html=True)

    # DATA FETCHING
    st.markdown('<div class="section">🌧️ Environmental Monitoring</div>', unsafe_allow_html=True)
    if st.button("🔄 Fetch Latest Data", use_container_width=True):
        with st.spinner("Fetching weather, river and prediction data..."):
            result = fetch_live_data(location["id"])
            if "error" not in result:
                st.session_state.environmental_data = result
                st.session_state.prediction = result.get("environmentalData", {}).get("floodPrediction")
                st.success("Latest environmental data received")
                st.rerun()
            else:
                st.error(result["error"])

    # EXTRACT DATA
    api_response = st.session_state.environmental_data or {}
    env_data = api_response.get("environmentalData", {}) if isinstance(api_response, dict) else {}
    
    rainfall_1h = get_value(env_data, ["rainfall", "rainfall_1h_mm"])
    rainfall_6h = get_value(env_data, ["rainfallLast6Hours", "rainfall_6h_mm"])
    rainfall_24h = get_value(env_data, ["rainfallLast24Hours", "rainfall_24h_mm"])
    temperature = get_value(env_data, ["temperature", "temperature_c"])
    humidity = get_value(env_data, ["humidity", "humidity_pct"])
    pressure = get_value(env_data, ["atmosphericPressure", "pressure_hpa"])
    soil_moisture = get_value(env_data, ["soilMoisture", "soil_moisture_pct"])
    elevation = get_value(env_data, ["elevation", "elevation_m"])
    water_level = get_value(env_data, ["waterLevel", "water_level_m"])
    
    # 8 WEATHER CARDS
    st.markdown('<div class="section">🌦️ Weather Conditions</div>', unsafe_allow_html=True)
    weather_cards = [
        ("🌧️", "RAINFALL 1H", rainfall_1h, "mm"),
        ("🌧️", "RAINFALL 6H", rainfall_6h, "mm"),
        ("🌧️", "RAINFALL 24H", rainfall_24h, "mm"),
        ("🌡️", "TEMPERATURE", temperature, "°C"),
        ("💧", "HUMIDITY", humidity, "%"),
        ("🌬️", "PRESSURE", pressure, "hPa"),
        ("🌱", "SOIL MOISTURE", soil_moisture, "%"),
        ("⛰️", "ELEVATION", elevation, "m"),
    ]
    cols = st.columns(4)
    for idx, (icon, label, val, unit) in enumerate(weather_cards):
        with cols[idx % 4]:
            st.markdown(f'<div class="card"><div class="card-icon">{icon}</div><div class="card-label">{label}</div><div class="card-value">{format_value(val, unit)}</div></div>', unsafe_allow_html=True)

    # RIVER MONITORING
    st.markdown('<div class="section">🌊 River Monitoring</div>', unsafe_allow_html=True)
    river_col, river_info_col = st.columns(2)
    river_name = env_data.get("waterLevelRiver", "Unknown")
    river_station = env_data.get("waterLevelStation", "Unknown")
    river_source = env_data.get("waterLevelSource", "Not available")
    
    with river_col:
        if env_data:
            st.markdown(
                f"""<div class="card">
                    <div class="card-icon">🌊</div>
                    <div class="card-label">RIVER</div>
                    <div class="card-value">{river_name}</div>
                    <br>
                    <div class="card-label">WATER LEVEL</div>
                    <div class="card-value">{format_value(water_level, "m")}</div>
                    <p style="color:#78909c;">Station: {river_station}</p>
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.info("Fetch data to view river information.")

    with river_info_col:
        st.markdown(
            f"""<div class="card">
                <div class="card-icon">🛰️</div>
                <div class="card-label">RIVER DATA SOURCE</div>
                <div class="card-value">{river_source}</div>
                <br>
                <div style="color:#f2b84b; padding:12px; border-radius:10px; background:rgba(242,184,75,0.08);">
                    🟡 River information is provided by the Node.js backend.
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    # FLOOD PREDICTION (WITH MANUAL INPUTS)
    st.markdown('<div class="section">🤖 AI Flood Prediction</div>', unsafe_allow_html=True)
    prediction_col, input_col = st.columns([1, 1])

    with input_col:
        st.markdown(
            """<div class="card">
                <div class="card-label">LSTM MODEL</div>
                <h2 style="margin:0;">Model Inputs</h2>
                <p style="color:#78909c;">The model uses 9 environmental features.</p>
            </div>""",
            unsafe_allow_html=True,
        )
        input_rain_1h = st.number_input("Rainfall 1h (mm)", value=safe_float(rainfall_1h))
        input_rain_6h = st.number_input("Rainfall 6h (mm)", value=safe_float(rainfall_6h))
        input_rain_24h = st.number_input("Rainfall 24h (mm)", value=safe_float(rainfall_24h))
        input_soil = st.number_input("Soil Moisture (%)", value=safe_float(soil_moisture))
        input_temperature = st.number_input("Temperature (°C)", value=safe_float(temperature))
        input_humidity = st.number_input("Humidity (%)", value=safe_float(humidity))
        input_pressure = st.number_input("Pressure (hPa)", value=safe_float(pressure))
        input_water_level = st.number_input("Water Level (m)", value=safe_float(water_level))
        input_elevation = st.number_input("Elevation (m)", value=safe_float(elevation))

    with prediction_col:
        prediction = st.session_state.prediction
        if isinstance(prediction, dict):
            probability = prediction.get("floodProbability", prediction.get("probability", 0))
            risk = str(prediction.get("riskLevel", "UNKNOWN")).upper()
            try: probability = float(probability)
            except (ValueError, TypeError): probability = 0.0
            
            percentage = probability * 100 if probability <= 1.0 else probability
            css_class, icon = ("high", "🔴") if risk == "HIGH" else ("medium", "🟡") if risk == "MEDIUM" else ("low", "🟢")
            
            st.markdown(
                f"""<div class="prediction">
                    <div class="card-label">FLOOD PROBABILITY</div>
                    <div class="probability">{percentage:.2f}%</div>
                    <div class="{css_class}">{icon} {risk} RISK</div>
                    <br>
                    <p style="color:#78909c;">LSTM model prediction</p>
                </div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """<div class="prediction">
                    <div style="font-size:60px;">🛡️</div>
                    <h2>Flood Risk</h2>
                    <p style="color:#78909c;">Fetch data or run the model to see a prediction.</p>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🤖 RUN LSTM PREDICTION", use_container_width=True):
        payload = {
            "rainfall_1h_mm": input_rain_1h, "rainfall_6h_mm": input_rain_6h, "rainfall_24h_mm": input_rain_24h,
            "soil_moisture_pct": input_soil, "temperature_c": input_temperature, "humidity_pct": input_humidity,
            "pressure_hpa": input_pressure, "water_level_m": input_water_level, "elevation_m": input_elevation,"district": st.session_state.selected_district,
        }
        with st.spinner("Running LSTM model..."):
            result = run_prediction(payload)
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.prediction = result.get("prediction")
                st.success("Prediction completed")
                st.rerun()

    # MAP VISUALIZATION
    st.markdown('<div class="section">🗺️ Monitoring Location</div>', unsafe_allow_html=True)
    map_data = pd.DataFrame({"latitude": [location["lat"]], "longitude": [location["lon"]]})
    st.map(map_data, latitude="latitude", longitude="longitude", zoom=7)

    # MODEL INFORMATION
    st.markdown('<div class="section">🧠 About the Model</div>', unsafe_allow_html=True)
    model_info = [("MODEL", "LSTM"), ("FEATURES", "9"), ("TIME STEPS", "6"), ("OUTPUT", "Flood Probability")]
    model_cols = st.columns(4)
    for col, (title, val) in zip(model_cols, model_info):
        col.markdown(f'<div class="card"><div class="card-label">{title}</div><div class="card-value">{val}</div></div>', unsafe_allow_html=True)

    # FOOTER
    st.markdown(
        """<div class="footer">
            <b>FloodGuard AI</b><br>
            West Bengal Flood Prediction & Environmental Intelligence System
            <br><br>
            ⚠️ Predictions are model estimates and should not be treated as official flood warnings.
        </div>""",
        unsafe_allow_html=True,
    )

# ============================================================
# APP ROUTER (Main Execution)
# ============================================================
if not st.session_state.logged_in:
    login_page()
else:
    dashboard_page()