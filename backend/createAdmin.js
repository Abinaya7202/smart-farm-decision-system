const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const Admin = require("./models/adminModel");
require("dotenv").config();

const createAdmin = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log("MongoDB connected");

    const hashedPassword = await bcrypt.hash("admin123", 10);

    await Admin.create({
      email: "admin@gmail.com",
      password: hashedPassword
    });

    console.log("✅ Admin created successfully");
    process.exit();
  } catch (error) {
    console.error("❌ Error creating admin:", error.message);
    process.exit(1);
  }
};

createAdmin();
