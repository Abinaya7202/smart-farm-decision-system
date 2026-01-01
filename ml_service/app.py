

# UPDATED FOR RENDER v1.0
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import urllib.request
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
# 📌 GitHub Release Model Loader (Lazy Loading)
# ==================================================
BASE_URL = "https://github.com/Abinaya7202/smart-farm-decision-system/releases/download/v1.0/"

models = {}

def get_model(filename):
    """Lazy download + load"""
    if filename not in models:
        url = BASE_URL + filename
        if not os.path.exists(filename):
            print(f"📥 Downloading {filename} ...")
            urllib.request.urlretrieve(url, filename)
        print(f"✅ Loading {filename}")
        models[filename] = joblib.load(filename)
    return models[filename]


# ==================================================
# 📌 Request Body Schemas
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
# 🌾 MODULE 1: Crop Yield Prediction
# ==================================================
@app.post("/predict")
def predict(data: PredictInput):
    yield_model = get_model("crop_model.pkl")

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

    prediction = yield_model.predict(df)[0]
    return {
        "predicted_yield": round(float(prediction), 2),
        "total_production": round(float(prediction * data.area), 2)
    }


# ==================================================
# 💰 MODULE 2: Price Prediction
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
        "unit": "₹ per ton"
    }


# ==================================================
# 🐛 MODULE 3: Pest Risk Detection
# ==================================================
@app.post("/pest-risk")
def pest_risk(data: PestInput):
    scaler = get_model("risk_scaler.pkl")
    pest_model = get_model("pest_risk_model.pkl")

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

    risk = pest_model.predict(df)[0]
    label = {"Low":"🟢 Low", "Medium":"🟡 Medium", "High":"🔴 High"}[risk]

    return {
        "ai_label": label,
        "pest_risk": risk,
        "temperature_used": temp,
        "scaled_index": round(float(scaled), 2)
    }


# ==================================================
# 🚦 Health Check Endpoint (Optional)
# ==================================================
@app.get("/")
def home():
    return {"message": "🚀 API running successfully!"}


# ==================================================
# 🚀 Run Server (Local)
# ==================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
