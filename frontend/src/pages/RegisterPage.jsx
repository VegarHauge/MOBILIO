// src/pages/RegisterPage.jsx
import React, { useState } from "react";
import MainLayout from "../layouts/MainLayout";
import { Typography, Button, Box, Paper, TextField, Alert } from "@mui/material";
import { API_BASE_URL } from "../config";
import { getImageUrl } from "../utils/s3Utils";
import { useNavigate } from "react-router-dom";

function HeroSection() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate(); // <-- redirect controller

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (password !== repeatPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          password,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || data.message || "Registration failed");
      }

      // success
      setSuccess("Registration successful! Redirecting to login...");
      setName("");
      setEmail("");
      setPassword("");
      setRepeatPassword("");

      // Auto redirect after 1.5 seconds
      setTimeout(() => {
        navigate("/login");
      }, 1500);

    } catch (err) {
      setError(err.message);
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

      {/* Register Box */}
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
          Register
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Box component="form" onSubmit={handleRegister}>
          <TextField
            fullWidth
            label="Name"
            type="text"
            margin="normal"
            variant="outlined"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <TextField
            fullWidth
            label="E-Mail"
            type="email"
            margin="normal"
            variant="outlined"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            margin="normal"
            variant="outlined"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <TextField
            fullWidth
            label="Repeat Password"
            type="password"
            margin="normal"
            variant="outlined"
            value={repeatPassword}
            onChange={(e) => setRepeatPassword(e.target.value)}
            required
          />

          <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
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
              {loading ? "Registering..." : "Register"}
            </Button>

            <Button
              variant="outlined"
              href="/"
              sx={{ flex: 1, borderColor: "#000", color: "#000" }}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}

export default function RegisterPage() {
  return (
    <MainLayout hero={<HeroSection />} navColor="light">
      {/* Optional content */}
    </MainLayout>
  );
}
