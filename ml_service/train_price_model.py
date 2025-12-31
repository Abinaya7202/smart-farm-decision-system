import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

# Load dataset
df = pd.read_csv("datasets/dataset_indian_crop_price.csv")


# KEEP ONLY COLUMNS YOU HAVE IN FRONTEND
df = df[[
    "State",
    "Crop Type",
    "Season",
    "Rainfall (mm)",
    "Price (₹/ton)"
]]

# Features & Target
X = df.drop("Price (₹/ton)", axis=1)
y = df["Price (₹/ton)"]

# Column groups
categorical = ["State", "Crop Type", "Season"]
numerical = ["Rainfall (mm)"]

# Preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", "passthrough", numerical)
    ]
)

# Model
model = RandomForestRegressor(n_estimators=250, random_state=42)

# Pipeline
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

# Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pipeline.fit(X_train, y_train)

# Save model
joblib.dump(pipeline, "crop_price_model.pkl")
print("🎉 Price Prediction Model Trained Successfully (No Input Change)")
