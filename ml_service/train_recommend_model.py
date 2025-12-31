import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Load dataset
df = pd.read_csv("datasets/crop_yield.csv")

# Keep only required columns
df = df[["State", "Soil_type", "Annual_Rainfall", "Crop"]]

# Drop missing values
df = df.dropna()

# Features & target
X = df[["State", "Soil_type", "Annual_Rainfall"]]
y = df["Crop"]

# Categorical & numeric columns
categorical_cols = ["State", "Soil_type"]
numeric_cols = ["Annual_Rainfall"]

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("num", "passthrough", numeric_cols)
    ]
)

# Model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

# Pipeline
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

# Train
pipeline.fit(X, y)

# Save model
joblib.dump(pipeline, "crop_recommend_model.pkl")

print("✅ Crop recommendation model trained successfully")
