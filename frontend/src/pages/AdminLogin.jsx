import React, { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

const AdminLogin = () => {
  const {
    adminEmail,
    setAdminEmail,
    adminPassword,
    setAdminPassword,
    loginAdmin
  } = useContext(AuthContext);

  return (
    <div className="card shadow p-4" style={{ width: "380px" }}>
      <h4 className="text-center mb-3">Admin Login</h4>

      <form onSubmit={loginAdmin}>
        <input
          className="form-control mb-2"
          placeholder="Admin Email"
          value={adminEmail}
          onChange={e => setAdminEmail(e.target.value)}
        />

        <input
          type="password"
          className="form-control mb-3"
          placeholder="Password"
          value={adminPassword}
          onChange={e => setAdminPassword(e.target.value)}
        />

        <button className="btn btn-dark w-100">
          Login as Admin
        </button>
      </form>
    </div>
  );
};

export default AdminLogin;
