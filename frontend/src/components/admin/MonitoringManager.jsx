import { Box, Typography } from "@mui/material";
import React from "react";

export default function MonitoringPanel() {
  // URL from Grafana "Share" → "Embed" → copy the iframe URL
  const grafanaURL =
    `${window.location.origin}/grafana/d/fastapi_metrics/fastapi-custom-metrics?orgId=1&from=now-15m&to=now&timezone=browser&refresh=10s&kiosk`;

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom>
        System Monitoring
      </Typography>
      <iframe
        src={grafanaURL}
        width="100%"
        height="800"
        frameBorder="0"
        title="Grafana Monitoring"
      ></iframe>
    </Box>
  );
}
