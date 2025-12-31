import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import UserAuth from "./pages/UserAuth";
import AdminLogin from "./pages/AdminLogin";
import Home from "./pages/Home";
import AdminDashboard from "./pages/AdminDashboard";
import CropYield from "./pages/CropYield";


const App = () => {
  const [showAdmin, setShowAdmin] = useState(false);

  return (
    <>
      {/* Navbar */}
      <Navbar
        showAdmin={showAdmin}
        toggleAdmin={() => setShowAdmin(!showAdmin)}
      />

      {/* Routes */}
      <Routes>
        {/* AUTH PAGE (CENTERED) */}
        <Route
          path="/"
          element={
            <div
              className="d-flex justify-content-center align-items-center"
              style={{ minHeight: "calc(100vh - 70px)" }}
            >
              {showAdmin ? <AdminLogin /> : <UserAuth />}
            </div>
          }
        />

        {/* HOME PAGE (NORMAL LAYOUT) */}
        <Route path="/home" element={<Home />} />
        <Route path="/crop-yield" element={<CropYield />} />
        <Route path="/admin-dashboard" element={<AdminDashboard />} />

      </Routes>
    </>
  );
};

export default App;
