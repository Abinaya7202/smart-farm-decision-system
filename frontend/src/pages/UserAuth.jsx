import React, { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";

const UserAuth = () => {
  const [isLogin, setIsLogin] = useState(true);

  const {
    username,
    setUsername,
    email,
    setEmail,
    password,
    setPassword,
    loginUsername,
    setLoginUsername,
    loginPassword,
    setLoginPassword,
    registerUser,
    loginUser
  } = useContext(AuthContext);

  return (
    <div className="card shadow p-4 mt-5" style={{ width: "380px" }}>
      <h4 className="text-center mb-3">
        {isLogin ? "User Login" : "User Registration"}
      </h4>

      {isLogin ? (
        <form onSubmit={loginUser}>
          <input
            className="form-control mb-2"
            placeholder="Username"
            value={loginUsername}
            onChange={(e) => setLoginUsername(e.target.value)}
            required
          />

          <input
            type="password"
            className="form-control mb-3"
            placeholder="Password"
            value={loginPassword}
            onChange={(e) => setLoginPassword(e.target.value)}
            required
          />

          <button className="btn btn-primary w-100 mb-2">
            Login
          </button>

          <p className="text-center">
            New user?{" "}
            <span
              className="text-primary"
              style={{ cursor: "pointer" }}
              onClick={() => setIsLogin(false)}
            >
              Register
            </span>
          </p>
        </form>
      ) : (
        <form onSubmit={(e) => registerUser(e, () => setIsLogin(true))}>
          <input
            className="form-control mb-2"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <input
            className="form-control mb-2"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            className="form-control mb-3"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button className="btn btn-success w-100 mb-2">
            Register
          </button>

          <p className="text-center">
            Already have an account?{" "}
            <span
              className="text-success"
              style={{ cursor: "pointer" }}
              onClick={() => setIsLogin(true)}
            >
              Login
            </span>
          </p>
        </form>
      )}
    </div>
  );
};

export default UserAuth;
