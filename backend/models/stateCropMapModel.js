const mongoose = require("mongoose");
const { mapDB } = require("../config/db");

const stateCropSchema = new mongoose.Schema(
  {
    State: { type: String, required: true },
    Crop: { type: String, required: true }
  },
  {
    collection: "state_crop_map" // EXACT collection name
  }
);

module.exports = mapDB.model("StateCropMap", stateCropSchema);
