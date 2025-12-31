const axios = require("axios");

// Yield prediction
exports.predictYield = async (req, res) => {
  try {
    const response = await axios.post(
      "http://127.0.0.1:8000/predict",
      {
        area: Number(req.body.area),
        rainfall: Number(req.body.rainfall),
        fertilizer: Number(req.body.fertilizer),
        pesticide: Number(req.body.pesticide),
        crop: req.body.crop,
        state: req.body.state,
        soil_type: req.body.soil_type   // 🔴 exact key
      }
    );

    res.json(response.data);
  } catch (err) {
    console.error(err.response?.data || err.message);
    res.status(400).json({ message: "Yield prediction failed" });
  }
};

// Crop recommendation

const axios = require("axios");

exports.recommendCrop = async (req, res) => {
  try {
    const { state, crop, soil_type, rainfall } = req.body;

    const response = await axios.post("http://127.0.0.1:8000/recommend", {
      state: state, // Required by the new RecommendInput schema
      crop: crop,   // Required to check confidence for this specific crop
      soil_type: soil_type,
      rainfall: Number(rainfall)
    });

    res.json(response.data);
  } catch (err) {
    console.error("ML Error:", err.response?.data || err.message);
    res.status(500).json({ message: "AI recommendation failed" });
  }
};