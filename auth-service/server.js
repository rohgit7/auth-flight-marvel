const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const path = require("path");

const authRoutes = require("./routes/auth");

const app = express();
app.use(express.json());
app.use(cors());

// MongoDB
mongoose.connect(
  process.env.MONGO_URL || "mongodb://mongo_container:27017/auth_demo"
)
.then(() => console.log("MongoDB connected"))
.catch(err => console.error(err));

// API routes
app.use("/api/auth", authRoutes);

// Basic health route (from jenkins project)
app.get("/api/message", (req, res) => {
  res.json({ message: "Backend + Auth running successfully 🚀" });
});

// Frontend
app.use(express.static(path.join(__dirname, "public")));

const PORT = process.env.PORT || 3000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});
