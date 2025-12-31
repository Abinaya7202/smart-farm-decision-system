from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load models
yield_model = joblib.load("crop_model.pkl")
recommend_model = joblib.load("crop_recommend_model.pkl")
price_model = joblib.load("crop_price_model.pkl") 
pest_model = joblib.load("pest_risk_model.pkl")
 # ⭐ NEW

# ----------------- INPUT SCHEMAS -----------------
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



# ----------------- MODULE 1: YIELD -----------------
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


# ----------------- MODULE 2: RECOMMENDATION -----------------
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
    selected_conf = prob_map.get(data.crop, 0.0)

    response = {
        "selected_crop": data.crop,
        "selected_crop_confidence": round(selected_conf * 100, 2),
        "best_crop_suggestion": best_crop,
        "best_crop_confidence": round(best_conf * 100, 2),
        "ranking": [
            {"crop": c, "confidence": round(p * 100, 2)}
            for c, p in ranked[:5]
        ]
    }

    # AI Decision Logic
    if selected_conf >= best_conf * 0.75:
        response["ai_decision"] = f"✔ {data.crop} is suitable."
    elif selected_conf >= 0.25:
        response["ai_decision"] = f"⚠ {data.crop} is moderately suitable."
    else:
        response["ai_decision"] = f"❌ Low suitability. Try **{best_crop}**."

    # Data-based explanations
    response["soil_evidence"] = (
        f"Observed training match confidence: {round(probabilities.mean()*100, 2)}% for soil type {data.soil_type}."
    )
    response["rainfall_evidence"] = (
        f"Rainfall {data.rainfall}mm aligns closest with crop patterns of {best_crop}."
    )

    return response


# ----------------- MODULE 3: PRICE PREDICTION -----------------
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
        "unit": "₹ per ton",
        "message": "Price prediction based on historical trend patterns."
    }

# Load model at the top with other models

@app.post("/pest-risk")
def pest_risk(data: PestInput):
    season_temp = {"Kharif": 32, "Rabi": 22, "Zaid": 38}
    auto_temp = season_temp.get(data.season, 30)

    # 🧠 B3-based automatic pest index scoring
    base = 0.5

    if auto_temp >= 35: base += 0.2
    elif auto_temp <= 20: base -= 0.1

    if data.rainfall > 800: base += 0.15
    elif data.rainfall < 300: base += 0.2

    if data.season == "Zaid": base += 0.1
    if data.season == "Kharif": base += 0.05
    if data.season == "Rabi": base -= 0.1

    high_risk_crops = ["Cotton","Brinjal","Chilli","Tomato"]
    if data.crop in high_risk_crops:
        base += 0.1

    pest_index = max(0, min(1, base))

    df = pd.DataFrame([{
        "State": data.state,
        "Crop Type": data.crop,
        "Season": data.season,
        "Temperature (°C)": auto_temp,
        "Rainfall (mm)": data.rainfall,
        "Auto_Pest_Index": pest_index
    }])

    risk = pest_model.predict(df)[0]

    label = {"Low":"🟢 Low", "Medium":"🟡 Medium", "High":"🔴 High"}[risk]

    return {
        "pest_risk": risk,
        "ai_label": label,
        "temperature_used": auto_temp,
        "pest_index_used": round(pest_index, 2),
        "message": f"Pest risk is {risk} for {data.crop} in {data.state} during {data.season}."
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
