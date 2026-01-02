from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import urllib.request
import os
import traceback

# ==========================
# 🚀 FASTAPI APP
# ==========================
app = FastAPI(title="Smart Farm Decision Support API")

# ==========================
# 🌐 CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# ☁️ GOOGLE DRIVE SETUP
# ==========================
DRIVE_BASE = "https://drive.google.com/uc?export=download&id="

MODEL_IDS = {
    "crop_model.pkl": "1AQV3pitp34I1U2d2NUtEASyAbnga5hyb",
    "crop_price_model.pkl": "15sYYLxGv4dsO5c-TI3HEG6xjcA7Yx7FA",
    "pest_risk_model.pkl": "1JYGtfXlvTw8Edn2lQYbdm7dIm_GQOlKf",
    "risk_scaler.pkl": "1vf6Tiqwc4g5ljkhKvkm8Y7jhoR9er3vQ",
}

loaded_models = {}

def get_model(name: str):
    try:
        if name not in loaded_models:
            file_id = MODEL_IDS[name]
            url = DRIVE_BASE + file_id

            if not os.path.exists(name):
                print(f"📥 Downloading {name}")
                urllib.request.urlretrieve(url, name)

            loaded_models[name] = joblib.load(name)
            print(f"✅ Loaded {name}")

        return loaded_models[name]

    except Exception as e:
        print("❌ MODEL LOAD ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Model loading failed")


# ==========================
# 📥 INPUT SCHEMAS
# ==========================
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


# ==========================
# 🌾 CROP YIELD PREDICTION
# ==========================
@app.post("/predict")
def predict_crop_yield(data: PredictInput):
    try:
        model = get_model("crop_model.pkl")

        # EXACT FEATURES USED DURING TRAINING
        df = pd.DataFrame([{
            "State": data.state,
            "Crop Type": data.crop,
            "Season": data.season,
            "Rainfall (mm)": data.rainfall
        }])

        prediction = model.predict(df)[0]

        return {
            "predicted_yield": float(prediction),
            "estimated_total_production": float(prediction * data.area)
        }

    except Exception as e:
        print("❌ PREDICT ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# 💰 PRICE PREDICTION
# ==========================
@app.post("/predict-price")
def predict_price(data: PriceInput):
    try:
        model = get_model("crop_price_model.pkl")

        df = pd.DataFrame([{
            "State": data.state,
            "Crop Type": data.crop,
            "Season": data.season,
            "Rainfall (mm)": data.rainfall
        }])

        price = model.predict(df)[0]

        return {
            "predicted_price": float(price),
            "unit": "₹ per ton"
        }

    except Exception as e:
        print("❌ PRICE ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# 🐛 PEST RISK PREDICTION
# ==========================
@app.post("/pest-risk")
def pest_risk(data: PestInput):
    try:
        scaler = get_model("risk_scaler.pkl")
        model = get_model("pest_risk_model.pkl")

        season_temp = {
            "Kharif": 32,
            "Rabi": 22,
            "Zaid": 38
        }

        temperature = season_temp.get(data.season, 30)

        # AUTO PEST INDEX (same logic as training)
        pest_index = 0.5
        if temperature >= 35:
            pest_index += 0.2
        if data.rainfall < 300:
            pest_index += 0.2
        if data.crop in ["Cotton", "Brinjal", "Chilli", "Tomato"]:
            pest_index += 0.1

        pest_index = min(max(pest_index, 0), 1)

        scaled_index = scaler.transform([[pest_index]])[0][0]

        df = pd.DataFrame([{
            "State": data.state,
            "Crop Type": data.crop,
            "Season": data.season,
            "Temperature (°C)": temperature,
            "Rainfall (mm)": data.rainfall,
            "Auto_Pest_Index": scaled_index
        }])

        risk = model.predict(df)[0]

        return {
            "risk_label": {
                "Low": "🟢 Low",
                "Medium": "🟡 Medium",
                "High": "🔴 High"
            }[risk],
            "category": risk,
            "pest_index_scaled": float(scaled_index)
        }

    except Exception as e:
        print("❌ PEST ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# 🏠 HEALTH CHECK
# ==========================
@app.get("/")
def home():
    return {"message": "🚀 Smart Farm API Running Successfully"}


# ==========================
# ▶ LOCAL RUN (Railway-safe)
# ==========================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
