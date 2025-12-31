import React, { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

const Navbar = ({ showAdmin, toggleAdmin }) => {
  const { loggedUser, logout } = useContext(AuthContext);

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-success px-4">
      {/* LEFT SIDE */}
      <span className="navbar-brand fw-bold">
        {loggedUser
          ? `Hi, ${loggedUser.username}`
          : "🌱 Multi-Module Crop Yield Prediction & Farm Decision Support System"}
      </span>

      {/* RIGHT SIDE */}
      <div className="ms-auto">
        {loggedUser ? (
          <button className="btn btn-outline-light" onClick={logout}>
            Logout
          </button>
        ) : (
          <button
            className="btn btn-outline-light"
            onClick={toggleAdmin}
          >
            {showAdmin ? "User Login" : "Admin Login"}
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
