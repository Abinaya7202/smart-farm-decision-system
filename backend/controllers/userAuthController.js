const User = require("../models/userModel");

// ---------------- REGISTER USER ----------------
const registerUser = async (req, res) => {
  try {
    const { username, email, password } = req.body;

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: "User already exists" });
    }

    const newUser = new User({
      username,
      email,
      password
    });

    await newUser.save();

    res.json({ message: "User registered successfully" });
  } catch (error) {
    res.status(500).json({ message: "Registration failed" });
  }
};

// ---------------- LOGIN USER ----------------
const loginUser = async (req, res) => {
  try {
    const { username, password } = req.body;

    const user = await User.findOne({ username, password });

    if (!user) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    if (user.status === "Inactive") {
      return res.status(403).json({ message: "Account is inactive" });
    }

    user.lastLogin = new Date();
    await user.save();

    res.json({
      message: "Login successful",
      user
    });
  } catch (error) {
    res.status(500).json({ message: "Login failed" });
  }
};

module.exports = {
  registerUser,
  loginUser
};
