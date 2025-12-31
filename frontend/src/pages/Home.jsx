import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="container mt-5">
      <h2 className="text-success">
        🌱 Welcome to Crop Yield Prediction & Farm Decision Support System
      </h2>

      <p className="mt-3">
        Use this system to:
      </p>

      <ul>
        <li>Predict crop yield</li>
        <li>Get crop recommendations</li>
        <li>Identify pest & disease risks</li>
        <li>Estimate profit</li>
      </ul>

      {/* ✅ Navigate to Crop Yield page */}
      <Link to="/crop-yield">
        <button className="btn btn-success w-100 mt-3">
          🌾 Predict Yield
        </button>
      </Link>
    </div>
  );
};

export default Home;
