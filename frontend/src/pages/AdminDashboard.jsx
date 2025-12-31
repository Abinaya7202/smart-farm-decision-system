const BASE_URL = import.meta.env.VITE_API_URL;

import React, { useEffect, useState } from "react";
import axios from "axios";

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);

  const backendURL = "http://localhost:5000";

  const fetchUsers = async () => {
    try {
      const res = await axios.get(`${backendURL}/admin/users`);
      setUsers(res.data);
    } catch (error) {
      alert("Failed to fetch users");
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div className="container mt-4">
      <h3 className="mb-4 text-success">👨‍💼 Admin Dashboard</h3>

      <div className="table-responsive">
        <table className="table table-bordered table-striped">
          <thead className="table-success">
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Registered Date</th>
              <th>Last Login</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center">
                  No users found
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user._id}>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td>{user.role}</td>
                  <td>
                    {new Date(user.createdAt).toLocaleDateString()}
                  </td>
                  <td>
                    {user.lastLogin
                      ? new Date(user.lastLogin).toLocaleString()
                      : "Never"}
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        user.status === "Active"
                          ? "bg-success"
                          : "bg-danger"
                      }`}
                    >
                      {user.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminDashboard;
