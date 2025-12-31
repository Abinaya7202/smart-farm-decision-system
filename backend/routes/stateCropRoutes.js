const express = require("express");
const router = express.Router();
const {
  getCropsByState
} = require("../controllers/stateCropController");

router.get("/crops/:state", getCropsByState);

module.exports = router;
