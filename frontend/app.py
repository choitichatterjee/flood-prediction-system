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

# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://localhost:5000"

# ============================================================
# LOCATION DATA
# ============================================================

LOCATIONS = {
    "Jalpaiguri": {
        "id": "jalpaiguri",
        "district": "Jalpaiguri",
        "station": "IMD Jalpaiguri",
        "lat": 26.5167,
        "lon": 88.7333,
    },
    "Cooch Behar": {
        "id": "cooch-behar",
        "district": "Cooch Behar",
        "station": "IMD Cooch Behar",
        "lat": 26.3452,
        "lon": 89.4482,
    },
    "Alipurduar": {
        "id": "alipurduar",
        "district": "Alipurduar",
        "station": "IMD Alipurduar",
        "lat": 26.4919,
        "lon": 89.5271,
    },
    "Kalimpong": {
        "id": "kalimpong",
        "district": "Kalimpong",
        "station": "IMD Kalimpong",
        "lat": 27.0667,
        "lon": 88.4667,
    },
    "Malda": {
        "id": "malda",
        "district": "Malda",
        "station": "IMD Malda",
        "lat": 25.0108,
        "lon": 88.1411,
    },
    "Kolkata": {
        "id": "kolkata",
        "district": "Kolkata",
        "station": "IMD Kolkata",
        "lat": 22.5726,
        "lon": 88.3639,
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if "environmental_data" not in st.session_state:
    st.session_state.environmental_data = None

if "prediction" not in st.session_state:
    st.session_state.prediction = None

# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at 90% 0%, rgba(0, 188, 212, 0.12), transparent 30%), #07141d;
        color: white;
    }

    header {
        visibility: hidden;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
    }

    [data-testid="stSidebar"] {
        background: #061019;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 30px;
    }

    .logo {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        background: linear-gradient(135deg, #00bcd4, #216cff);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 27px;
    }

    .brand-title {
        font-size: 25px;
        font-weight: 800;
    }

    .brand-subtitle {
        color: #78909c;
        font-size: 11px;
    }

    .hero {
        padding: 45px;
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.14), rgba(33, 108, 255, 0.05));
        border: 1px solid rgba(255, 255, 255, 0.07);
        margin-bottom: 30px;
    }

    .hero-label {
        color: #00c9df;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
    }

    .hero-title {
        font-size: 50px;
        font-weight: 800;
        line-height: 1.05;
        margin-top: 15px;
    }

    .hero-title span {
        color: #00c9df;
    }

    .hero-text {
        color: #8da5b1;
        max-width: 720px;
        line-height: 1.7;
        margin-top: 15px;
    }

    .section {
        font-size: 22px;
        font-weight: 800;
        margin-top: 35px;
        margin-bottom: 18px;
    }

    .card {
        background: rgba(13, 31, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 22px;
        min-height: 135px;
        margin-bottom: 15px;
    }

    .card-icon {
        font-size: 27px;
    }

    .card-label {
        color: #78909c;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-top: 8px;
    }

    .card-value {
        font-size: 25px;
        font-weight: 800;
        margin-top: 7px;
    }

    .prediction {
        text-align: center;
        padding: 35px;
        border-radius: 25px;
        background: rgba(13, 31, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        min-height: 250px;
    }

    .probability {
        font-size: 60px;
        font-weight: 900;
    }

    .high { color: #ff5c5c; font-weight: 800; }
    .medium { color: #f2b84b; font-weight: 800; }
    .low { color: #55d69a; font-weight: 800; }

    .footer {
        margin-top: 50px;
        padding-top: 25px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        color: #526a76;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# BACKEND FUNCTIONS
# ============================================================

def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Node.js backend. Start server.js first."}
    except requests.exceptions.RequestException as error:
        return {"error": str(error)}

def fetch_live_data(location_id):
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/data",
            params={"location": location_id},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        try:
            details = response.json()
        except ValueError:
            details = response.text
        return {
            "error": f"Backend returned HTTP {response.status_code}",
            "details": details,
        }
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Node.js backend. Make sure server.js is running."}
    except requests.exceptions.RequestException as error:
        return {"error": str(error)}

def run_prediction(payload):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/predict",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        try:
            details = response.json()
        except ValueError:
            details = response.text
        return {
            "error": f"Prediction failed with HTTP {response.status_code}",
            "details": details,
        }
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Node.js backend. Ensure server.js is running."}
    except requests.exceptions.RequestException as error:
        return {"error": str(error)}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_value(data, possible_keys):
    if not isinstance(data, dict):
        return None
    for key in possible_keys:
        if key in data and data[key] is not None:
            return data[key]
    return None

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def format_value(data, unit=""):
    if data is None:
        return "--"
    try:
        return f"{float(data):.2f} {unit}"
    except (ValueError, TypeError):
        return f"{data} {unit}"

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """<div class="brand">
            <div class="logo">🌊</div>
            <div>
                <div class="brand-title">FloodGuard</div>
                <div class="brand-subtitle">AI FLOOD INTELLIGENCE</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### 📍 Select Location")
    selected_name = st.selectbox("District", list(LOCATIONS.keys()))
    location = LOCATIONS[selected_name]

    st.divider()
    st.markdown("### System")
    st.code(BACKEND_URL, language="text")
    st.caption("Node.js backend connection")

    st.divider()

    if st.button("🔌 Test Backend Connection"):
        result = check_backend()
        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Backend connected")
            st.json(result)

# ============================================================
# HERO & HEADER
# ============================================================

st.markdown(
    """<div class="brand">
        <div class="logo">🌊</div>
        <div>
            <div class="brand-title">FloodGuard AI</div>
            <div class="brand-subtitle">WEST BENGAL FLOOD MONITORING SYSTEM</div>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    """<div class="hero">
        <div class="hero-label">AI-POWERED ENVIRONMENTAL INTELLIGENCE</div>
        <div class="hero-title">West Bengal<br><span>Flood Risk Intelligence</span></div>
        <div class="hero-text">
            Monitor rainfall, weather conditions, river information
            and machine-learning predictions for selected locations across West Bengal.
        </div>
    </div>""",
    unsafe_allow_html=True,
)

# ============================================================
# LOCATION OVERVIEW
# ============================================================

st.markdown('<div class="section">📍 Location Overview</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""<div class="card">
            <div class="card-icon">📍</div>
            <div class="card-label">DISTRICT</div>
            <div class="card-value">{location['district']}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""<div class="card">
            <div class="card-icon">🛰️</div>
            <div class="card-label">WEATHER STATION</div>
            <div class="card-value">{location['station']}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""<div class="card">
            <div class="card-icon">🗺️</div>
            <div class="card-label">COORDINATES</div>
            <div class="card-value">{location['lat']:.4f}, {location['lon']:.4f}</div>
        </div>""",
        unsafe_allow_html=True,
    )

# ============================================================
# FETCH ENVIRONMENTAL DATA
# ============================================================

st.markdown('<div class="section">🌧️ Environmental Monitoring</div>', unsafe_allow_html=True)

if st.button("🔄 Fetch Latest Data", use_container_width=True):
    location_id = location["id"]
    with st.spinner("Fetching weather, river and prediction data..."):
        result = fetch_live_data(location_id)

    if "error" in result:
        st.error(result["error"])
        if "details" in result:
            st.json(result["details"])
    else:
        st.session_state.environmental_data = result
        environmental_data = result.get("environmentalData", {})
        st.session_state.prediction = environmental_data.get("floodPrediction")
        st.success("Latest environmental data received")
        st.rerun()

# ============================================================
# EXTRACT BACKEND RESPONSE
# ============================================================

api_response = st.session_state.environmental_data
environmental_data = api_response.get("environmentalData", {}) if isinstance(api_response, dict) else {}

rainfall_1h = get_value(environmental_data, ["rainfall", "rainfall_1h_mm"])
rainfall_6h = get_value(environmental_data, ["rainfallLast6Hours", "rainfall_6h_mm"])
rainfall_24h = get_value(environmental_data, ["rainfallLast24Hours", "rainfall_24h_mm"])
temperature = get_value(environmental_data, ["temperature", "temperature_c"])
humidity = get_value(environmental_data, ["humidity", "humidity_pct"])
pressure = get_value(environmental_data, ["atmosphericPressure", "pressure_hpa"])
soil_moisture = get_value(environmental_data, ["soilMoisture", "soil_moisture_pct"])
elevation = get_value(environmental_data, ["elevation", "elevation_m"])
water_level = get_value(environmental_data, ["waterLevel", "water_level_m"])

# ============================================================
# WEATHER CARDS
# ============================================================

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

columns = st.columns(4)

for index, card in enumerate(weather_cards):
    icon, label, data, unit = card
    display = format_value(data, unit)
    with columns[index % 4]:
        st.markdown(
            f"""<div class="card">
                <div class="card-icon">{icon}</div>
                <div class="card-label">{label}</div>
                <div class="card-value">{display}</div>
            </div>""",
            unsafe_allow_html=True,
        )

# ============================================================
# RIVER MONITORING
# ============================================================

st.markdown('<div class="section">🌊 River Monitoring</div>', unsafe_allow_html=True)

river_col, river_info_col = st.columns(2)

river_name = environmental_data.get("waterLevelRiver", "Unknown")
river_station = environmental_data.get("waterLevelStation", "Unknown")
river_source = environmental_data.get("waterLevelSource", "Not available")
display_water_level = format_value(water_level, "m")

with river_col:
    if api_response:
        st.markdown(
            f"""<div class="card">
                <div class="card-icon">🌊</div>
                <div class="card-label">RIVER</div>
                <div class="card-value">{river_name}</div>
                <br>
                <div class="card-label">WATER LEVEL</div>
                <div class="card-value">{display_water_level}</div>
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

# ============================================================
# FLOOD PREDICTION
# ============================================================

st.markdown('<div class="section">🤖 AI Flood Prediction</div>', unsafe_allow_html=True)

prediction_col, input_col = st.columns([1, 1])

# MODEL INPUTS
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

# PREDICTION DISPLAY
with prediction_col:
    prediction = st.session_state.prediction

    if isinstance(prediction, dict):
        probability = prediction.get("floodProbability", prediction.get("probability", 0))
        risk = str(prediction.get("riskLevel", "UNKNOWN")).upper()

        try:
            probability = float(probability)
        except (ValueError, TypeError):
            probability = 0.0

        percentage = probability * 100 if probability <= 1.0 else probability

        if risk == "HIGH":
            css_class, icon = "high", "🔴"
        elif risk == "MEDIUM":
            css_class, icon = "medium", "🟡"
        else:
            css_class, icon = "low", "🟢"

        st.markdown(
            f"""<div class="prediction">
                <div class="card-label">FLOOD PROBABILITY</div>
                <div class="probability">{percentage:.2f}%</div>
                <div class="{css_class}">{icon} {risk} RISK</div>
                <br>
                <p style="color:#78909c;">LSTM model prediction</p>
            </div>""",
            unsafe_allow_html=True,
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
            "rainfall_1h_mm": input_rain_1h,
            "rainfall_6h_mm": input_rain_6h,
            "rainfall_24h_mm": input_rain_24h,
            "soil_moisture_pct": input_soil,
            "temperature_c": input_temperature,
            "humidity_pct": input_humidity,
            "pressure_hpa": input_pressure,
            "water_level_m": input_water_level,
            "elevation_m": input_elevation,
        }

        with st.spinner("Running LSTM model..."):
            result = run_prediction(payload)

        if "error" in result:
            st.error(result["error"])
            if "details" in result:
                st.json(result["details"])
        else:
            st.session_state.prediction = result.get("prediction")
            st.success("Prediction completed")
            st.rerun()

# ============================================================
# MAP
# ============================================================

st.markdown('<div class="section">🗺️ Monitoring Location</div>', unsafe_allow_html=True)

map_data = pd.DataFrame(
    {
        "latitude": [location["lat"]],
        "longitude": [location["lon"]],
    }
)

st.map(map_data, latitude="latitude", longitude="longitude", zoom=7)

# ============================================================
# MODEL INFORMATION
# ============================================================

st.markdown('<div class="section">🧠 About the Model</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

model_info = [
    ("MODEL", "LSTM"),
    ("FEATURES", "9"),
    ("TIME STEPS", "6"),
    ("OUTPUT", "Flood Probability"),
]

for column, item in zip([m1, m2, m3, m4], model_info):
    title, result = item
    with column:
        st.markdown(
            f"""<div class="card">
                <div class="card-label">{title}</div>
                <div class="card-value">{result}</div>
            </div>""",
            unsafe_allow_html=True,
        )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """<div class="footer">
        <b>FloodGuard AI</b><br>
        West Bengal Flood Prediction & Environmental Intelligence System
        <br><br>
        ⚠️ Predictions are model estimates and should not be treated as official flood warnings.
    </div>""",
    unsafe_allow_html=True,
)