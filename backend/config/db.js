const mongoose = require("mongoose");

// AUTH DB (unchanged)
const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log("✅ Auth DB connected");
  } catch (err) {
    console.error("Auth DB error:", err.message);
    process.exit(1);
  }
};

// FARM DB (second cluster)
const mapDB = mongoose.createConnection(process.env.MONGO_MAP_URI);

mapDB.on("connected", () => {
  console.log("✅ Farm DB connected");
});

mapDB.on("error", (err) => {
  console.error("Farm DB error:", err.message);
});

module.exports = { connectDB, mapDB };
