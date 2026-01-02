from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import urllib.request
import os

app = FastAPI()

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Google Drive Direct Download Base -----
DRIVE_BASE = "https://drive.google.com/uc?export=download&id="

# ----- Model File IDs -----
MODEL_IDS = {
    "crop_model.pkl": "1AQV3pitp34I1U2d2NUtEASyAbnga5hyb",
    "crop_price_model.pkl": "15sYYLxGv4dsO5c-TI3HEG6xjcA7Yx7FA",
    "pest_cluster_model.pkl": "1773cjoJmsJdcaG4_mPPcetEEgJCuqMfP",
    "pest_risk_model.pkl": "1JYGtfXlvTw8Edn2lQYbdm7dIm_GQOlKf",
    "risk_scaler.pkl": "1vf6Tiqwc4g5ljkhKvkm8Y7jhoR9er3vQ"
}

loaded_models = {}

# ----- Download & Load on Demand -----
def get_model(name):
    if name not in loaded_models:
        file_id = MODEL_IDS[name]
        url = DRIVE_BASE + file_id

        if not os.path.exists(name):
            print(f"📥 Downloading {name}...")
            urllib.request.urlretrieve(url, name)

        loaded_models[name] = joblib.load(name)
        print(f"✅ Loaded: {name}")

    return loaded_models[name]


# ----- Input Schemas -----
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


# ----- ENDPOINTS -----

@app.post("/predict")
def predict(data: PredictInput):
    model = get_model("crop_model.pkl")

    df = pd.DataFrame([data.dict()])
    df.columns = [
        "Area",
        "Annual_Rainfall",
        "Fertilizer",
        "Pesticide",
        "Crop",
        "State",
        "Soil_type",
        "Season",
    ]

    result = model.predict(df)[0]

    return {
        "predicted_yield": float(result),
        "estimated_total_production": float(result * data.area)
    }


@app.post("/predict-price")
def predict_price(data: PriceInput):
    model = get_model("crop_price_model.pkl")

    df = pd.DataFrame([data.dict()])
    df.columns = ["State", "Crop Type", "Season", "Rainfall (mm)"]

    price = model.predict(df)[0]

    return {
        "predicted_price": float(price),
        "unit": "₹ per ton"
    }


@app.post("/pest-risk")
def pest_risk(data: PestInput):
    scaler = get_model("risk_scaler.pkl")
    model = get_model("pest_risk_model.pkl")

    season_temp = {"Kharif": 32, "Rabi": 22, "Zaid": 38}
    temp = season_temp.get(data.season, 30)

    base = 0.5 + (0.2 if temp >= 35 else 0) + (0.2 if data.rainfall < 300 else 0)
    if data.crop in ["Cotton", "Brinjal", "Chilli", "Tomato"]:
        base += 0.1

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

    return {
        "risk_label": {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}[risk],
        "category": risk,
        "pest_index_scaled": float(scaled),
    }


@app.get("/")
def home():
    return {"message": "🚀 API Running with Google Drive Models!"}


# ----- LOCAL RUN ONLY (Railway-safe) -----
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
