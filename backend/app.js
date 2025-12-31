const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;
const AUTH_DB = process.env.MONGO_URI;
const MAP_DB = process.env.MONGO_MAP_URI;

// Auth DB
mongoose
  .connect(AUTH_DB)
  .then(() => console.log("✅ Auth DB connected"))
  .catch(err => console.error("❌ Auth DB error", err));

// State–Crop DB
const mapConn = mongoose.createConnection(MAP_DB);

mapConn.once("open", () => {
  console.log("✅ State–Crop Map DB connected");
});

const StateCropMap = mapConn.model(
  "StateCropMap",
  new mongoose.Schema(
    { State: String, Crop: String },
    { collection: "state_crop_map" }
  )
);

// Auth routes
app.use("/user", require("./routes/userAuthRoutes"));
app.use("/admin", require("./routes/adminAuthRoutes"));
app.use("/ml", require("./routes/mlRoutes"));



// State → Crop routes
app.get("/map/crops/:state", async (req, res) => {
  try {
    const crops = await StateCropMap.find(
      { State: req.params.state },
      { _id: 0, Crop: 1 }
    );
    res.json(crops.map(c => c.Crop));
  } catch {
    res.status(500).json({ message: "Failed to fetch crops" });
  }
});

// ✅ ML ROUTES (YIELD + RECOMMEND)
const mlRoutes = require("./routes/mlRoutes");
app.use("/ml", mlRoutes);

app.get("/", (req, res) => {
  res.send("🚀 Backend running");
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
