import numpy as np
import joblib

from tensorflow.keras.models import load_model


# =========================
# 1. LOAD MODEL AND SCALER
# =========================

model = load_model("ml/lstm_flood_model.keras")

scaler = joblib.load("ml/lstm_scaler.pkl")

print("LSTM model loaded successfully!")
print("Scaler loaded successfully!")


# =========================
# 2. SAMPLE DATA
# =========================
#
# 8 features — exactly the same
# features used during training.
#

current_data = [
    25.0,    # rainfall_1h_mm
    65.0,    # rainfall_6h_mm
    120.0,   # rainfall_24h_mm
    72.0,    # soil_moisture_pct
    27.5,    # temperature_c
    88.0,    # humidity_pct
    1002.0,  # pressure_hpa
    80.0     # elevation_m
]


# =========================
# 3. SCALE DATA
# =========================

current_data = np.array(
    current_data
).reshape(1, -1)

scaled_data = scaler.transform(
    current_data
)


# =========================
# 4. CREATE 6-TIME-STEP SEQUENCE
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
# 5. PREDICT
# =========================

prediction = model.predict(
    sequence,
    verbose=0
)

flood_probability = float(
    prediction[0][0]
)


# =========================
# 6. DETERMINE RISK
# =========================

if flood_probability >= 0.70:

    risk_level = "HIGH"

elif flood_probability >= 0.40:

    risk_level = "MEDIUM"

else:

    risk_level = "LOW"


# =========================
# 7. DISPLAY RESULT
# =========================

print("")
print("==============================")
print("FLOOD PREDICTION")
print("==============================")

print(
    f"Flood Probability: "
    f"{flood_probability * 100:.2f}%"
)

print(
    f"Risk Level: {risk_level}"
)