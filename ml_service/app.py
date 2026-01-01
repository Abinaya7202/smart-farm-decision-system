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
# 📌 GitHub Release Model Loader
# ==================================================
BASE_URL = "https://github.com/Abinaya7202/smart-farm-decision-system/releases/download/v1.0/"

def load_model(filename):
    url = BASE_URL + filename
    local_file = filename

    if not os.path.exists(local_file):
        print(f"📥 Downloading {filename} ...")
        urllib.request.urlretrieve(url, local_file)

    print(f"✅ Loaded {filename}")
    return joblib.load(local_file)

# 📌 Load all models on startup
yield_model           = load_model("crop_model.pkl")
recommend_model       = load_model("crop_recommend_model.pkl")
price_model           = load_model("crop_price_model.pkl")
pest_model            = load_model("pest_risk_model.pkl")
cluster_model         = load_model("pest_cluster_model.pkl")   # ⭐ ADDED
risk_scaler           = load_model("risk_scaler.pkl")          # ⭐ ADDED

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

class RecommendInput(BaseModel):
    crop: str
    state: str
    soil_type: str
    rainfall: float
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
# 🔥 MODULE 1: Yield Prediction
# ==================================================
@app.post("/predict")
def predict(data: PredictInput):
    input_df = pd.DataFrame([{
        "Area": data.area,
        "Annual_Rainfall": data.rainfall,
        "Fertilizer": data.fertilizer,
        "Pesticide": data.pesticide,
        "Crop": data.crop,
        "State": data.state,
        "Soil_type": data.soil_type,
        "Season": data.season
    }])

    prediction = yield_model.predict(input_df)[0]
    return {
        "predicted_yield": round(float(prediction), 2),
        "total_production": round(float(prediction * data.area), 2)
    }

# ==================================================
# 🔥 MODULE 2: Crop Recommendation
# ==================================================
@app.post("/recommend")
def recommend(data: RecommendInput):
    input_df = pd.DataFrame([{
        "State": data.state,
        "Soil_type": data.soil_type,
        "Annual_Rainfall": data.rainfall,
        "Season": data.season
    }])

    probabilities = recommend_model.predict_proba(input_df)[0]
    crops = recommend_model.classes_
    prob_map = dict(zip(crops, probabilities))
    ranked = sorted(prob_map.items(), key=lambda x: x[1], reverse=True)

    best_crop, best_conf = ranked[0]
    selected_conf = prob_map.get(data.crop, 0)

    return {
        "selected_crop": data.crop,
        "selected_crop_confidence": round(selected_conf * 100, 2),
        "best_crop_suggestion": best_crop,
        "best_crop_confidence": round(best_conf * 100, 2),
        "ranking": [{"crop": c, "confidence": round(p * 100, 2)} for c, p in ranked[:5]],
        "ai_decision":
            f"✔ {data.crop} is suitable." if selected_conf >= best_conf * 0.75 else
            f"⚠ {data.crop} is moderately suitable." if selected_conf >= 0.25 else
            f"❌ Low suitability. Try **{best_crop}**."
    }

# ==================================================
# 🔥 MODULE 3: Price Prediction
# ==================================================
@app.post("/predict-price")
def predict_price(data: PriceInput):
    df = pd.DataFrame([{
        "State": data.state,
        "Crop Type": data.crop,
        "Season": data.season,
        "Rainfall (mm)": data.rainfall
    }])

    price = price_model.predict(df)[0]
    return {
        "predicted_price": round(float(price), 2),
        "unit": "₹ per ton"
    }

# ==================================================
# 🔥 MODULE 4: Pest Risk Assessment
# ==================================================
@app.post("/pest-risk")
def pest_risk(data: PestInput):
    season_temp = {"Kharif": 32, "Rabi": 22, "Zaid": 38}
    temp = season_temp.get(data.season, 30)

    base_index = 0.5
    if temp >= 35: base_index += 0.2
    if data.rainfall < 300: base_index += 0.2
    if data.crop in ["Cotton","Brinjal","Chilli","Tomato"]: base_index += 0.1

    pest_index = risk_scaler.transform([[base_index]])[0][0]  # ⭐ Using scaler
    df = pd.DataFrame([{
        "State": data.state,
        "Crop Type": data.crop,
        "Season": data.season,
        "Temperature (°C)": temp,
        "Rainfall (mm)": data.rainfall,
        "Auto_Pest_Index": pest_index
    }])

    risk = pest_model.predict(df)[0]
    label = {"Low":"🟢 Low", "Medium":"🟡 Medium", "High":"🔴 High"}[risk]

    return {
        "ai_label": label,
        "pest_risk": risk,
        "temperature_used": temp,
        "scaled_pest_index": round(float(pest_index), 2)
    }

# ==================================================
# 🚀 Run Server (Local Only)
# ==================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
