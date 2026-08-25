import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping


# ==================================================
# 1. LOAD DATASET
# ==================================================

DATA_PATH = "ml/data/west_bengal_flood_prototype_20000_6locations.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)


# ==================================================
# 2. SELECT 8 FEATURES
# ==================================================

features = [
    "rainfall_1h_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "soil_moisture_pct",
    "temperature_c",
    "humidity_pct",
    "pressure_hpa",
    "elevation_m"
]

target = "flood"


# ==================================================
# 3. CHECK REQUIRED COLUMNS
# ==================================================

required_columns = features + [target]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        f"Missing columns: {missing_columns}"
    )


# ==================================================
# 4. PREPARE X AND Y
# ==================================================

X = df[features].copy()
y = df[target].astype(int)


# ==================================================
# 5. HANDLE MISSING VALUES
# ==================================================

X = X.fillna(X.median())


# ==================================================
# 6. SCALE FEATURES
# ==================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ==================================================
# 7. CREATE 6-TIME-STEP SEQUENCES
# ==================================================

TIME_STEPS = 6

X_sequences = []
y_sequences = []


for i in range(
    TIME_STEPS,
    len(X_scaled)
):

    sequence = X_scaled[
        i - TIME_STEPS:i
    ]

    X_sequences.append(sequence)

    y_sequences.append(
        y.iloc[i]
    )


X_sequences = np.array(X_sequences)
y_sequences = np.array(y_sequences)


print(
    "Sequence shape:",
    X_sequences.shape
)


# ==================================================
# 8. TRAIN / TEST SPLIT
# ==================================================

X_train, X_test, y_train, y_test = train_test_split(
    X_sequences,
    y_sequences,
    test_size=0.20,
    random_state=42,
    stratify=y_sequences
)


print(
    "Training samples:",
    len(X_train)
)

print(
    "Testing samples:",
    len(X_test)
)


# ==================================================
# 9. BUILD LSTM MODEL
# ==================================================

model = Sequential([

    LSTM(
        64,
        input_shape=(
            TIME_STEPS,
            len(features)
        ),
        return_sequences=False
    ),

    Dropout(0.2),

    Dense(
        32,
        activation="relu"
    ),

    Dropout(0.2),

    Dense(
        1,
        activation="sigmoid"
    )

])


# ==================================================
# 10. COMPILE MODEL
# ==================================================

model.compile(

    optimizer="adam",

    loss="binary_crossentropy",

    metrics=["accuracy"]

)


# ==================================================
# 11. TRAIN MODEL
# ==================================================

early_stopping = EarlyStopping(

    monitor="val_loss",

    patience=5,

    restore_best_weights=True

)


print("")
print("==============================")
print("STARTING LSTM TRAINING")
print("==============================")


history = model.fit(

    X_train,
    y_train,

    validation_split=0.20,

    epochs=30,

    batch_size=32,

    callbacks=[
        early_stopping
    ],

    verbose=1

)


# ==================================================
# 12. EVALUATE MODEL
# ==================================================

test_loss, test_accuracy = model.evaluate(

    X_test,
    y_test,

    verbose=0

)


print("")
print("==============================")
print("LSTM MODEL RESULTS")
print("==============================")

print(
    "Test Loss:",
    test_loss
)

print(
    "Test Accuracy:",
    test_accuracy
)


# ==================================================
# 13. SAVE MODEL
# ==================================================

model.save(
    "ml/lstm_flood_model.keras"
)


# ==================================================
# 14. SAVE SCALER
# ==================================================

joblib.dump(

    scaler,

    "ml/lstm_scaler.pkl"

)


print("")
print(
    "Model saved as: ml/lstm_flood_model.keras"
)

print(
    "Scaler saved as: ml/lstm_scaler.pkl"
)

print("")
print(
    "Training completed successfully!"
)