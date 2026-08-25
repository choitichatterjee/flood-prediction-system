import sys
import json
import numpy as np
import joblib

from tensorflow.keras.models import load_model


# =========================
# LOAD MODEL AND SCALER
# =========================

model = load_model("ml/lstm_flood_model.keras")

scaler = joblib.load("ml/lstm_scaler.pkl")


# =========================
# READ DATA FROM NODE.JS
# =========================

input_data = json.loads(sys.stdin.read())


# =========================
# GET 8 MODEL INPUTS
# =========================

current_data = [

    float(input_data["rainfall_1h_mm"]),

    float(input_data["rainfall_6h_mm"]),

    float(input_data["rainfall_24h_mm"]),

    float(input_data["soil_moisture_pct"]),

    float(input_data["temperature_c"]),

    float(input_data["humidity_pct"]),

    float(input_data["pressure_hpa"]),

    float(input_data["elevation_m"])

]


# =========================
# SCALE DATA
# =========================

current_data = np.array(
    current_data
).reshape(1, -1)

scaled_data = scaler.transform(
    current_data
)


# =========================
# CREATE 6-TIME-STEP SEQUENCE
# =========================

sequence = np.repeat(
    scaled_data,
    6,
    axis=0
)

sequence = sequence.reshape(
    1,
    6,
    8
)


# =========================
# PREDICT
# =========================

prediction = model.predict(
    sequence,
    verbose=0
)

flood_probability = float(
    prediction[0][0]
)


# =========================
# DETERMINE RISK LEVEL
# =========================

if flood_probability >= 0.70:

    risk_level = "HIGH"

elif flood_probability >= 0.40:

    risk_level = "MEDIUM"

else:

    risk_level = "LOW"


# =========================
# RETURN JSON TO NODE.JS
# =========================

result = {

    "floodProbability":
        flood_probability,

    "riskLevel":
        risk_level

}


print(
    json.dumps(result)
)