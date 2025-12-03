import React, { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext"; // Importiere AuthContext
import MainLayout from "../layouts/MainLayout";
import { Typography, Button, Box, Paper, TextField } from "@mui/material";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";
import { getImageUrl } from "../utils/s3Utils";

function HeroSection() {
  const { login } = useContext(AuthContext);
  const [form, setForm] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      axios.defaults.headers.common.Authorization = `Bearer ${storedToken}`;
    }
  }, []);

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Simple validation
    if (!form.email || !form.password) {
      setErrors({ general: "Please enter E-Mail and Password" });
      return;
    }

    setErrors({});
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email: form.email,
        password: form.password,
      });

      const { access_token, user } = response.data;
      if (!access_token) {
        throw new Error("No access token returned by server");
      }

      const { role } = user; // Extrahiere role aus user
      console.log("Login Response:", { access_token, role }); // Debugging

      login(access_token, role.toLowerCase());

      // Reroute based on role
      navigate(role.toLowerCase() === "admin" ? "/admin/dashboard" : "/");
    } catch (err) {
      console.error("Login failed:", err);
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Login failed. Please check your information.";
      setErrors({ general: message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        height: "100vh",
        backgroundImage: `url(${getImageUrl("login_hero.png", true)})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "white",
        px: 6,
        position: "relative",
      }}
    >
      {/* Overlay */}
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          bgcolor: "rgba(0,0,0,0.4)",
        }}
      />

      {/* Login-Box */}
      <Paper
        elevation={6}
        sx={{
          position: "relative",
          zIndex: 1,
          p: 4,
          borderRadius: 3,
          width: "100%",
          maxWidth: 400,
          bgcolor: "rgba(255,255,255,0.9)",
        }}
      >
        <Typography variant="h5" mb={2} align="center" color="black">
          Login
        </Typography>

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="E-Mail"
            name="email"
            type="email"
            margin="normal"
            variant="outlined"
            value={form.email}
            onChange={handleChange}
          />
          <TextField
            fullWidth
            label="Password"
            name="password"
            type="password"
            margin="normal"
            variant="outlined"
            value={form.password}
            onChange={handleChange}
          />

          {errors.general && (
            <Typography color="error" variant="body2" mt={1}>
              {errors.general}
            </Typography>
          )}

          <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
            <Button
              variant="outlined"
              href="/register"
              sx={{ flex: 1, borderColor: "#303030", color: "#303030" }}
            >
              Register
            </Button>

            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              sx={{
                flex: 1,
                backgroundColor: "#000",
                "&:hover": { backgroundColor: "#333" },
              }}
            >
              {loading ? "Loading..." : "Login"}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}

export default function LoginPage() {
  return (
    <MainLayout hero={<HeroSection />} navColor="light">
      {/* Content below Hero */}
    </MainLayout>
  );
}