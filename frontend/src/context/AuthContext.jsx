import React, { createContext, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const backendURL = "http://localhost:5000";
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
      await axios.post(`${backendURL}/user/register`, {
        username,
        email,
        password
      });

      alert("User registered successfully");

      setUsername("");
      setEmail("");
      setPassword("");

      // move to login after registration
      if (switchToLogin) switchToLogin();
    } catch (error) {
      alert(error.response?.data?.message || "Registration failed");
    }
  };

  // ================= USER LOGIN =================
  const loginUser = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${backendURL}/user/login`, {
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

      // ✅ redirect user to home
      navigate("/home");
    } catch (error) {
      alert(error.response?.data?.message || "Invalid username or password");
    }
  };

  // ================= ADMIN LOGIN =================
  const loginAdmin = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${backendURL}/admin/login`, {
        email: adminEmail,
        password: adminPassword
      });

      alert("Admin login successful");

      setAdminEmail("");
      setAdminPassword("");

      // ✅ redirect admin to dashboard
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
        // register
        username,
        setUsername,
        email,
        setEmail,
        password,
        setPassword,

        // user login
        loginUsername,
        setLoginUsername,
        loginPassword,
        setLoginPassword,

        // admin login
        adminEmail,
        setAdminEmail,
        adminPassword,
        setAdminPassword,

        // logged user
        loggedUser,

        // functions
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
