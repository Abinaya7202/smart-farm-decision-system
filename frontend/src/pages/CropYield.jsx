import React, { useEffect, useState } from "react";
import axios from "axios";

const BACKEND_URL = "http://localhost:5000";

/* =========================
   ALL INDIAN STATES
========================= */
const INDIAN_STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
  "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka",
  "Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya",
  "Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim",
  "Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand",
  "West Bengal","Andaman and Nicobar Islands","Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu","Delhi","Jammu and Kashmir",
  "Ladakh","Lakshadweep","Puducherry"
];

/* =========================
   SOIL TYPES
========================= */
const SOIL_TYPES = [
  "alluvial","black","red","laterite","desert","mountain"
];

const CropYield = () => {
  const [state, setState] = useState("");
  const [crop, setCrop] = useState("");
  const [soilType, setSoilType] = useState("");
  const [season, setSeason] = useState(""); // ⭐ ADDED
  const [crops, setCrops] = useState([]);

  const [area, setArea] = useState("");
  const [rainfall, setRainfall] = useState("");
  const [fertilizer, setFertilizer] = useState("");
  const [pesticide, setPesticide] = useState("");

  const [yieldResult, setYieldResult] = useState(null);
  const [recommendation, setRecommendation] = useState(null);

  const [priceResult, setPriceResult] = useState(null);

  const [pestRisk, setPestRisk] = useState(null);



  /* =========================
     FETCH CROPS BY STATE
  ========================= */
  useEffect(() => {
    if (!state) {
      setCrops([]);
      setCrop("");
      return;
    }

    axios.get(`${BACKEND_URL}/map/crops/${state}`)
      .then(res => setCrops(res.data || []))
      .catch(() => setCrops([]));
  }, [state]);

  /* =========================
     PREDICT YIELD
  ========================= */
  const predictYield = async () => {
    if (!state || !crop || !soilType || !area || !rainfall || !season) {
      alert("Please fill all fields including Season.");
      return;
    }

    try {
      const res = await axios.post(`${BACKEND_URL}/ml/predict-yield`, {
        state,
        crop,
        soil_type: soilType,
        season, // ⭐ ADDED
        area: Number(area),
        rainfall: Number(rainfall),
        fertilizer: Number(fertilizer || 0),
        pesticide: Number(pesticide || 0)
      });

      setYieldResult(res.data);
    } catch (err) {
      alert("Yield prediction failed");
      console.error(err);
    }
  };

  /* =========================
     GET RECOMMENDATION
  ========================= */
  const getRecommendation = async () => {
    if (!state || !crop || !soilType || !rainfall || !season) {
      alert("Select State, Crop, Soil, Season & Rainfall");
      return;
    }

    try {
      const res = await axios.post(`${BACKEND_URL}/ml/recommend`, {
        state,
        crop,
        soil_type: soilType,
        season, // ⭐ ADDED
        rainfall: Number(rainfall),
        fertilizer: Number(fertilizer || 0),
        pesticide: Number(pesticide || 0),
      });

      setRecommendation(res.data);
    } catch (err) {
      console.error("Frontend Error:", err);
      alert("Recommendation service unavailable.");
    }
  };
  const predictPrice = async () => {
  if (!state || !crop || !season || !rainfall) {
    alert("State, Crop, Season & Rainfall are required for price prediction");
    return;
  }

  try {
    const res = await axios.post(`${BACKEND_URL}/ml/predict-price`, {
      state,
      crop,
      season,
      rainfall: Number(rainfall)
    });

    setPriceResult(res.data);
  } catch (err) {
    alert("Price prediction service unavailable");
    console.error(err);
  }
};

const checkPestRisk = async () => {
  if (!state || !crop || !season || !rainfall) {
    alert("Please select State, Crop, Season and Rainfall first!");
    return;
  }

  try {
    const res = await axios.post("http://127.0.0.1:8000/pest-risk", {
      state,
      crop,
      season,
      rainfall: Number(rainfall)
    });

    // 🟢 Store response, so UI can show it instead of alert()
    setPestRisk(res.data);

  } catch (err) {
    console.error("❌ Pest Risk Error:", err);
    alert("❌ Pest risk service unavailable. Please check backend.");
  }
};

  return (
    <div className="container mt-4" style={{ maxWidth: "560px" }}>
      <h3 className="text-success text-center mb-3">
        🌾 Crop Yield Prediction & Recommendation
      </h3>

      {/* STATE */}
      <select className="form-control mb-2" value={state} onChange={e => setState(e.target.value)}>
        <option value="">Select State</option>
        {INDIAN_STATES.map((s, i) => (
          <option key={i} value={s}>{s}</option>
        ))}
      </select>

      {/* SEASON ⭐ ADDED */}
      <select className="form-control mb-2" value={season} onChange={e => setSeason(e.target.value)}>
        <option value="">Select Season</option>
        <option value="Kharif">Kharif (Rainy / Monsoon)</option>
        <option value="Rabi">Rabi (Winter)</option>
        <option value="Zaid">Zaid (Summer)</option>
      </select>

      {/* CROP */}
      <select
        className="form-control mb-2"
        value={crop}
        onChange={e => setCrop(e.target.value)}
        disabled={!state || crops.length === 0}
      >
        <option value="">Select Crop</option>
        {crops.map((c, i) => (
          <option key={i} value={c}>{c}</option>
        ))}
      </select>

      {/* SOIL */}
      <select className="form-control mb-2" value={soilType} onChange={e => setSoilType(e.target.value)}>
        <option value="">Select Soil Type</option>
        {SOIL_TYPES.map((s, i) => (
          <option key={i} value={s}>{s}</option>
        ))}
      </select>

      {/* NUMERIC INPUTS */}
      <input className="form-control mb-2" placeholder="Area (hectares)" value={area} onChange={e => setArea(e.target.value)} />
      <input className="form-control mb-2" placeholder="Rainfall (mm)" value={rainfall} onChange={e => setRainfall(e.target.value)} />
      <input className="form-control mb-2" placeholder="Fertilizer (kg)" value={fertilizer} onChange={e => setFertilizer(e.target.value)} />
      <input className="form-control mb-3" placeholder="Pesticide (kg)" value={pesticide} onChange={e => setPesticide(e.target.value)} />

      <button className="btn btn-success w-100 mb-2" onClick={predictYield}>
        Predict Yield
      </button>
      {/* YIELD RESULT */}
      {yieldResult && (
        <div className="alert alert-success mt-3">
          <p><strong>Yield:</strong> {yieldResult.predicted_yield} tons/hectare</p>
          <p><strong>Total Production:</strong> {yieldResult.total_production} tons</p>
        </div>
      )}

      {/* <button className="btn btn-outline-primary w-100" onClick={getRecommendation}>
        Get Crop Recommendation
      </button> */}
        
      {/* {recommendation && (
        <div className="alert alert-warning mt-3">
          <p><strong>Decision:</strong> {recommendation.ai_decision}</p>
          <p><strong>Selected Confidence:</strong> {recommendation.selected_crop_confidence}%</p>
          <p><strong>Better Option:</strong> {recommendation.best_crop_suggestion} ({recommendation.best_crop_confidence}%)</p>
          <p><strong>Soil Insight:</strong> {recommendation.soil_evidence}</p>
          <p><strong>Rainfall Insight:</strong> {recommendation.rainfall_evidence}</p>
        </div>
      )}  */}

      <button className="btn btn-info w-100 mt-2" onClick={predictPrice}>
  Predict Market Price
</button>
 {yieldResult && priceResult && (
  <div className="alert alert-info mt-3">
    
    <p>
      <strong>Estimated Market Price:</strong> ₹ {priceResult.predicted_price} / ton
      <br />
    
    </p>
    <p>
      <strong>💰 Total Profit:</strong> ₹{" "}
      {(yieldResult.total_production * priceResult.predicted_price).toFixed(2)}
    </p>
  </div>
)}

<button className="btn btn-danger w-100 mt-2" onClick={checkPestRisk}>
  Check Pest Risk 🚨
</button>

 {pestRisk && (
  <div className="alert alert-danger mt-3">
    <strong>🐛 Pest Risk:</strong> {pestRisk.pest_risk} <br />
    <small>🌡️ Auto Temp Used: {pestRisk.temperature_used || pestRisk.auto_temperature_used}°C</small><br/>
    <small>ℹ️ {pestRisk.reason || pestRisk.message}</small>
  </div>
)}

    </div>
  );
};

export default CropYield;
