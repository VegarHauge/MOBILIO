// src/components/admin/HealthMonitor.jsx
import React, { useEffect, useState } from "react";
import { Card, CardContent, Typography, Box } from "@mui/material";
import axios from "axios";
import { API_BASE_URL } from "../../config";

export default function HealthMonitor() {
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  const fetchHealth = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/health`);
      setStatus(res.data);
      setLogs((prev) => [
        `[${new Date().toLocaleTimeString()}] OK`,
        ...prev.slice(0, 19),
      ]);
    } catch (err) {
      setError("Health check failed");
      setLogs((prev) => [
        `[${new Date().toLocaleTimeString()}] ❌ Error`,
        ...prev.slice(0, 19),
      ]);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card sx={{ height: 300, overflow: "hidden", mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          System Health
        </Typography>
        {error && (
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        )}

        {status ? (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2">API: {status.api}</Typography>
            <Typography variant="body2">DB: {String(status.db)}</Typography>
            <Typography variant="caption" color="text.secondary">
              {status.timestamp}
            </Typography>
          </Box>
        ) : (
          <Typography variant="body2">Loading status…</Typography>
        )}

        <Box
          sx={{
            bgcolor: "#000",
            color: "#0f0",
            fontFamily: "monospace",
            fontSize: 12,
            p: 1,
            height: 150,
            overflowY: "auto",
          }}
        >
          {logs.map((line, idx) => (
            <div key={idx}>{line}</div>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}
