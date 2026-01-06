const express = require("express");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const User = require("../models/User");

const router = express.Router();

// Register
router.post("/register", async (req, res) => {
  try {
    const { username, password } = req.body;

    const hashed = await bcrypt.hash(password, 10);
    await User.create({ username, password: hashed });

    res.status(201).json({ message: "User registered" });
  } catch (err) {
    res.status(400).json({ error: "User already exists" });
  }
});

// Login


router.post("/login", async (req, res) => {
  const { username, password } = req.body;

  const user = await User.findOne({ username });
  if (!user) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  const match = await bcrypt.compare(password, user.password);
  if (!match) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  // ✅ Generate JWT
  const token = jwt.sign(
    { username },
    "ROH_MARV",
    { expiresIn: "10m" }
  );

  // ✅ Send redirect URL
  res.json({
    redirectUrl: `http://localhost:5000/?token=${token}`
  });
});


module.exports = router;

