from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import gdown
import os

app = FastAPI()

# ==================================================
# CORS
# ==================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# 📌 Google Drive File IDs (your models)
# ==================================================
MODEL_FILES = {
    "crop_model.pkl": "1AQV3pitp34I1U2d2NUtEASyAbnga5hyb",
    "crop_price_model.pkl": "15sYYLxGv4dsO5c-TI3HEG6xjcA7Yx7FA",
    "pest_cluster_model.pkl": "1773cjoJmsJdcaG4_mPPcetEEgJCuqMfP",
    "pest_risk_model.pkl": "1JYGtfXlvTw8Edn2lQYbdm7dIm_GQOlKf",
    "risk_scaler.pkl": "1vf6Tiqwc4g5ljkhKvkm8Y7jhoR9er3vQ"
}

# Hold loaded models in memory
models_cache = {}

# ==================================================
# 📌 Lazy Model Loader
# ==================================================
def get_model(filename):
    file_id = MODEL_FILES[filename]

    # Download if not available locally
    if not os.path.exists(filename):
        print(f"📥 Downloading {filename}...")
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        gdown.download(url, filename, quiet=False)

    # Cache in memory
    if filename not in models_cache:
        print(f"🔄 Loading {filename} into memory...")
        models_cache[filename] = joblib.load(filename)

    return models_cache[filename]


# ==================================================
# 📌 Request Schemas
# ==================================================
class PredictInput(BaseModel):
    area: float
    rainfall: float
    fertilizer: float
    pesticide: float
    crop: str
    state: str
    soil_type: str
    season: str

class PriceInput(BaseModel):
    state: str
    crop: str
    season: str
    rainfall: float

class PestInput(BaseModel):
    state: str
    crop: str
    season: str
    rainfall: float


# ==================================================
# 🌾 1️⃣ Crop Yield Prediction
# ==================================================
@app.post("/predict")
def predict(data: PredictInput):
    model = get_model("crop_model.pkl")

    df = pd.DataFrame([{
        "Area": data.area,
        "Annual_Rainfall": data.rainfall,
        "Fertilizer": data.fertilizer,
        "Pesticide": data.pesticide,
        "Crop": data.crop,
        "State": data.state,
        "Soil_type": data.soil_type,
        "Season": data.season
    }])

    pred = model.predict(df)[0]
    return {
        "predicted_yield": round(float(pred), 2),
        "total_production": round(float(pred * data.area), 2)
    }


# ==================================================
# 💰 2️⃣ Price Prediction
# ==================================================
@app.post("/predict-price")
def predict_price(data: PriceInput):
    model = get_model("crop_price_model.pkl")

    df = pd.DataFrame([{
        "State": data.state,
        "Crop Type": data.crop,
        "Season": data.season,
        "Rainfall (mm)": data.rainfall
    }])

    price = model.predict(df)[0]
    return {
        "predicted_price": round(float(price), 2),
        "unit": "₹ per ton",
        "message": "Based on historical price trends."
    }


# ==================================================
# 🐛 3️⃣ Pest Risk Detection
# ==================================================
@app.post("/pest-risk")
def pest_risk(data: PestInput):
    scaler = get_model("risk_scaler.pkl")
    model = get_model("pest_risk_model.pkl")

    temp_map = {"Kharif": 32, "Rabi": 22, "Zaid": 38}
    temp = temp_map.get(data.season, 30)

    base = 0.5
    if temp >= 35: base += 0.2
    if data.rainfall < 300: base += 0.2
    if data.crop in ["Cotton", "Brinjal", "Chilli", "Tomato"]: base += 0.1

    scaled = scaler.transform([[base]])[0][0]

    df = pd.DataFrame([{
        "State": data.state,
        "Crop Type": data.crop,
        "Season": data.season,
        "Temperature (°C)": temp,
        "Rainfall (mm)": data.rainfall,
        "Auto_Pest_Index": scaled
    }])

    risk = model.predict(df)[0]
    labels = {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}

    return {
        "risk_level": labels[risk],
        "temperature_used": temp,
        "scaled_index": round(float(scaled), 2)
    }


# ==================================================
# 🚦 Health Check
# ==================================================
@app.get("/")
def home():
    return {"message": "🚀 API is running with Google Drive ML models!"}


# ==================================================
# LOCAL RUN
# ==================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
