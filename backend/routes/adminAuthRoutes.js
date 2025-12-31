const express = require("express");
const router = express.Router();

const {
  adminLogin,
  getAllUsers,
  updateUserStatus
} = require("../controllers/adminAuthController");

// Admin login
router.post("/login", adminLogin);

// Get all users
router.get("/users", getAllUsers);

// Activate / Deactivate user
router.put("/user/status/:id", updateUserStatus);

module.exports = router;
