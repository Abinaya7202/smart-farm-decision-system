const express = require("express");
const axios = require("axios");
const router = express.Router();

const ML_URL = "http://127.0.0.1:8000";

router.post("/predict-yield", async (req, res) => {
  try {
    const response = await axios.post(`${ML_URL}/predict`, req.body);
    res.json(response.data);
  } catch {
    res.status(500).json({ message: "Prediction failed" });
  }
});

router.post("/recommend", async (req, res) => {
  try {
    const response = await axios.post(`${ML_URL}/recommend`, req.body);
    res.json(response.data);
  } catch {
    res.status(500).json({ message: "Recommendation failed" });
  }
});
router.post("/predict-price", async (req, res) => {
  try {
    const { data } = await axios.post(`${ML_URL}/predict-price`, req.body);
    res.json(data);
  } catch (err) {
    console.error("❌ Price Error:", err.message);
    return res.status(500).json({ message: "Price prediction failed" });
  }
});

module.exports = router;
