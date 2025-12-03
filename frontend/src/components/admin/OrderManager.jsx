import React, { useState, useEffect, useMemo } from "react";
import {
  Box,
  Button,
  TextField,
  MenuItem,
  InputAdornment,
  Typography,
  Divider,
  CircularProgress,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import OrderTable from "./OrderTable";
import OrderForm from "./OrderForm";
import {
  getOrders,
  updateOrder,
  deleteOrder,
} from "../../api/orders";

export default function OrderManager() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);

  // Filters
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("id");
  const [sortDirection, setSortDirection] = useState("asc");
  // Neue Filter für Datum und Preis
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");

  // === Load Orders ===
  const loadOrders = async () => {
    setLoading(true);
    try {
      const data = await getOrders();
      setOrders(data);
    } catch (err) {
      console.error("❌ Can't load orders:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  // === UD-Operations ===
  const handleUpdate = async (data) => {
    await updateOrder(editing.id, data);
    setEditing(null);
    setShowForm(false);
    loadOrders();
  };

  const handleDelete = async (id) => {
    if (window.confirm("\t\t     ︵\nSure?\t( ͠° ͟  °)")) {
      await deleteOrder(id);
      loadOrders();
    }
  };

  // === Sorter ===
  const handleSortChange = (column, direction) => {
    setSortBy(column);
    setSortDirection(direction);
  };

  // === Filter & Sort ===
  const filteredOrders = useMemo(() => {
    let result = [...orders];

    if (search) {
      result = result.filter((order) =>
        Object.values(order).some(
          (value) =>
            value &&
            value.toString().toLowerCase().includes(search.toLowerCase())
        )
      );
    }

    // Date filter
    if (dateFrom || dateTo) {
      result = result.filter((order) => {
        const orderDate = new Date(order.date);
        const from = dateFrom ? new Date(dateFrom) : null;
        const to = dateTo ? new Date(dateTo) : null;

        if (from && to) {
          return orderDate >= from && orderDate <= to;
        } else if (from) {
          return orderDate >= from;
        } else if (to) {
          return orderDate <= to;
        }
        return true;
      });
    }

    // Preisspannenfilter
    if (priceMin || priceMax) {
      result = result.filter((order) => {
        const price = parseFloat(order.price); // Annahme: order.price ist der Preis
        const min = priceMin ? parseFloat(priceMin) : null;
        const max = priceMax ? parseFloat(priceMax) : null;

        if (min && max) {
          return price >= min && price <= max;
        } else if (min) {
          return price >= min;
        } else if (max) {
          return price <= max;
        }
        return true;
      });
    }

    // Sortierung
    result.sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      if (sortDirection === "asc") {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return result;
  }, [orders, search, sortBy, sortDirection, dateFrom, dateTo, priceMin, priceMax]);

  // === Return of the ~~King~~ Manager ===
  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom>
        Order Manager
      </Typography>
      <Divider sx={{ mb: 3 }} />

      {!showForm ? (
        <>
          {/* Filter bar */}
          <Box
            sx={{
              display: "flex",
              gap: 2,
              mb: 3,
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >
            <TextField
              label="Search"
              variant="outlined"
              size="small"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ flex: 1, minWidth: 200 }}
            />
            {/* Date filter */}
            <TextField
              label="Datum von"
              type="date"
              size="small"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: 150 }}
            />
            <TextField
              label="Datum bis"
              type="date"
              size="small"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: 150 }}
            />
            {/* Price range filter */}
            <TextField
              label="Preis min"
              type="number"
              size="small"
              value={priceMin}
              onChange={(e) => setPriceMin(e.target.value)}
              InputProps={{
                startAdornment: <InputAdornment position="start">€</InputAdornment>,
              }}
              sx={{ minWidth: 120 }}
            />
            <TextField
              label="Preis max"
              type="number"
              size="small"
              value={priceMax}
              onChange={(e) => setPriceMax(e.target.value)}
              InputProps={{
                startAdornment: <InputAdornment position="start">€</InputAdornment>,
              }}
              sx={{ minWidth: 120 }}
            />
            <Button
                variant="outlined"
                onClick={() => {
                    setSearch("");
                    setDateFrom("");
                    setDateTo("");
                    setPriceMin("");
                    setPriceMax("");
                }}
                >
                Reset
            </Button>
          </Box>

          {/* Table */}
          <OrderTable
            orders={filteredOrders}
            onEdit={(o) => {
              setEditing(o);
              setShowForm(true);
            }}
            onDelete={handleDelete}
            sortBy={sortBy}
            sortDirection={sortDirection}
            onSortChange={handleSortChange}
          />
        </>
      ) : (
        <OrderForm
          initialData={editing || {}}
          onSubmit={handleUpdate}
          onCancel={() => {
            setEditing(null);
            setShowForm(false);
          }}
        />
      )}
    </Box>
  );
}