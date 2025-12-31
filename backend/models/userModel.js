const mongoose = require("mongoose");

const userSchema = new mongoose.Schema(
  {
    username: {
      type: String,
      required: true
    },

    email: {
      type: String,
      required: true,
      unique: true
    },

    password: {
      type: String,
      required: true
    },

    role: {
      type: String,
      default: "user"   // user / admin
    },

    status: {
      type: String,
      default: "Active" // Active / Inactive
    },

    lastLogin: {
      type: Date
    }
  },
  {
    timestamps: true   // adds createdAt & updatedAt
  }
);

module.exports = mongoose.model("User", userSchema);
