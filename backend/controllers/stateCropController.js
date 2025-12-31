const StateCropMap = require("../models/stateCropMapModel");

const getCropsByState = async (req, res) => {
  try {
    const state = req.params.state.trim();

    const crops = await StateCropMap.find({
      State: { $regex: `^${state}$`, $options: "i" }
    }).select("Crop -_id");

    res.json(crops.map(c => c.Crop));
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Failed to fetch crops" });
  }
};

module.exports = { getCropsByState };
