const Admin = require("../models/adminModel");
const User = require("../models/userModel");

// ---------------- ADMIN LOGIN ----------------
const adminLogin = async (req, res) => {
  try {
    const { email, password } = req.body;

    const admin = await Admin.findOne({ email, password });

    if (!admin) {
      return res.status(401).json({ message: "Invalid admin credentials" });
    }

    res.json({ message: "Admin login successful" });
  } catch (error) {
    res.status(500).json({ message: "Admin login failed" });
  }
};

// ---------------- GET ALL USERS ----------------
const getAllUsers = async (req, res) => {
  const users = await User.find().select("-password");
  res.json(users);
};

// ---------------- UPDATE USER STATUS ----------------
const updateUserStatus = async (req, res) => {
  const { status } = req.body;
  await User.findByIdAndUpdate(req.params.id, { status });
  res.json({ message: "User status updated" });
};

module.exports = {
  adminLogin,
  getAllUsers,
  updateUserStatus
};
