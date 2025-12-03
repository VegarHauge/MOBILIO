import {
  Box,
  Divider,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import React, { useState } from "react";
import MonitoringManager from "./MonitoringManager";
import OrderManager from "./OrderManager";
import ProductManager from "./ProductManager";

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function AdminDashboard() {
  const [tab, setTab] = useState(0);

  const handleChange = (event, newValue) => setTab(newValue);

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      <Divider sx={{ mb: 3 }} />

      {/* Tabs */}
      <Tabs
        value={tab}
        onChange={handleChange}
        textColor="primary"
        indicatorColor="primary"
        sx={{ mb: 3 }}
      >
        <Tab label="Products" />
        <Tab label="Orders" />
        <Tab label="Monitoring" />
      </Tabs>

      {/* Inhalt je nach Tab */}
      <TabPanel value={tab} index={0}>
        <ProductManager />
      </TabPanel>

      <TabPanel value={tab} index={1}>
        <OrderManager />
      </TabPanel>

      <TabPanel value={tab} index={2}>
        <MonitoringManager />
      </TabPanel>
    </Box>
  );
}
