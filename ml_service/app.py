from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import gdown
import traceback
import gc

# =========================
# 🚀 FASTAPI APP
# =========================
app = FastAPI(title="Smart Farm Decision Support API")

# =========================
# 🌐 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ☁️ GOOGLE DRIVE MODEL IDS
# =========================
MODEL_IDS = {
    "crop_model.pkl": "1AQV3pitp34I1U2d2NUtEASyAbnga5hyb",
    "crop_price_model.pkl": "15sYYLxGv4dsO5c-TI3HEG6xjcA7Yx7FA",
    "pest_risk_model.pkl": "1JYGtfXlvTw8Edn2lQYbdm7dIm_GQOlKf",
    "risk_scaler.pkl": "1vf6Tiqwc4g5ljkhKvkm8Y7jhoR9er3vQ",
}

# =========================
# 🧠 MODEL CACHE (IMPORTANT)
# =========================
loaded_models = {}

# Heavy models that must NEVER be in memory together
HEAVY_MODELS = {
    "crop_model.pkl",
    "crop_price_model.pkl"
}

def clear_other_heavy_models(current_model):
    """
    Remove other heavy models from memory
    to avoid Railway OOM crash.
    """
    for name in list(loaded_models.keys()):
        if name != current_model and name in HEAVY_MODELS:
            print(f"🧹 Unloading {name} from memory")
            del loaded_models[name]
            gc.collect()

def get_model(name: str):
    try:
        if name in HEAVY_MODELS:
            clear_other_heavy_models(name)

        # Remove corrupted or HTML files
        if os.path.exists(name) and os.path.getsize(name) < 100_000:
            print(f"🗑️ Removing corrupted {name}")
            os.remove(name)

        if name not in loaded_models:
            file_id = MODEL_IDS[name]
            url = f"https://drive.google.com/uc?id={file_id}"

            print(f"📥 Downloading {name} from Google Drive")
            gdown.download(
                url,
                name,
                quiet=False,
                fuzzy=True,
                use_cookies=False
            )

            # Validate real model file
            if not os.path.exists(name) or os.path.getsize(name) < 100_000:
                raise Exception("Invalid model file downloaded")

            loaded_models[name] = joblib.load(name)
            print(f"✅ Loaded model: {name}")

        return loaded_models[name]

    except Exception as e:
        print("❌ MODEL LOAD ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Model loading failed")

# =========================
# 📥 INPUT SCHEMAS
# =========================
class PredictInput(BaseModel):
    state: str
    crop: str
    season: str
    rainfall: float
    area: float
    fertilizer: float
    pesticide: float
    soil_type: str

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

# =========================
# 🌾 CROP YIELD PREDICTION
# =========================
@app.post("/predict")
def predict_crop_yield(data: PredictInput):
    model = get_model("crop_model.pkl")

    df = pd.DataFrame([{
        "State": data.state,
        "Crop Type": data.crop,
        "Season": data.season,
        "Rainfall (mm)": data.rainfall
    }])

    result = model.predict(df)[0]

    return {
        "predicted_yield": float(result),
        "estimated_total_production": float(result * data.area)
    }

# =========================
# 💰 PRICE PREDICTION
# =========================
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
        "predicted_price": float(price),
        "unit": "₹ per ton"
    }

# =========================
# 🐛 PEST RISK PREDICTION
# =========================
@app.post("/pest-risk")
def pest_risk(data: PestInput):
    scaler = get_model("risk_scaler.pkl")
    model = get_model("pest_risk_model.pkl")

    season_temp = {
        "Kharif": 32,
        "Rabi": 22,
        "Zaid": 38
    }
    temperature = season_temp.get(data.season, 30)

    pest_index = 0.5
    if temperature >= 35:
        pest_index += 0.2
    if data.rainfall < 300:
        pest_index += 0.2
    if data.crop in ["Cotton", "Brinjal", "Chilli", "Tomato"]:
        pest_index += 0.1

    pest_index = max(0, min(1, pest_index))
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

# =========================
# 🏠 HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"message": "🚀 Smart Farm API Running Successfully"}

# =========================
# ▶ LOCAL RUN (Railway Safe)
# =========================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
