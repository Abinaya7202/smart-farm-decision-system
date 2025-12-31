import React, { createContext, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const BASE_URL = import.meta.env.VITE_API_URL; // 👈 correct API base URL
  const navigate = useNavigate();

  // ================= USER REGISTER =================
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // ================= USER LOGIN =================
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // ================= ADMIN LOGIN =================
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPassword, setAdminPassword] = useState("");

  // ================= LOGGED USER =================
  const [loggedUser, setLoggedUser] = useState(
    JSON.parse(localStorage.getItem("user")) || null
  );

  // ================= REGISTER USER =================
  const registerUser = async (e, switchToLogin) => {
    e.preventDefault();
    try {
      await axios.post(`${BASE_URL}user/register`, {
        username,
        email,
        password
      });

      alert("User registered successfully");
      setUsername("");
      setEmail("");
      setPassword("");

      if (switchToLogin) switchToLogin();
    } catch (error) {
      alert(error.response?.data?.message || "Registration failed");
    }
  };

  // ================= USER LOGIN =================
  const loginUser = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${BASE_URL}user/login`, {
        username: loginUsername,
        password: loginPassword
      });

      const userData = {
        username: res.data.user.username,
        email: res.data.user.email
      };

      localStorage.setItem("user", JSON.stringify(userData));
      setLoggedUser(userData);

      setLoginUsername("");
      setLoginPassword("");

      navigate("/home");
    } catch (error) {
      alert(error.response?.data?.message || "Invalid username or password");
    }
  };

  // ================= ADMIN LOGIN =================
  const loginAdmin = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${BASE_URL}admin/login`, {
        email: adminEmail,
        password: adminPassword
      });

      alert("Admin login successful");
      setAdminEmail("");
      setAdminPassword("");

      navigate("/admin-dashboard");
    } catch (error) {
      alert(error.response?.data?.message || "Invalid admin credentials");
    }
  };

  // ================= LOGOUT =================
  const logout = () => {
    localStorage.removeItem("user");
    setLoggedUser(null);
    navigate("/");
  };

  return (
    <AuthContext.Provider
      value={{
        username, setUsername,
        email, setEmail,
        password, setPassword,

        loginUsername, setLoginUsername,
        loginPassword, setLoginPassword,

        adminEmail, setAdminEmail,
        adminPassword, setAdminPassword,

        loggedUser,

        registerUser,
        loginUser,
        loginAdmin,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
