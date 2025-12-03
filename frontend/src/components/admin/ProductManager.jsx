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
import ProductTable from "./ProductTable";
import ProductForm from "./ProductForm";
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from "../../api/products";

export default function ProductManager() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);

  // Filter + Sort
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [sortBy, setSortBy] = useState("id");
  const [sortDirection, setSortDirection] = useState("asc");

  // === load Products ===
  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (err) {
      console.error("❌ Can't load products:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  // === CRUD-Operatios ===
  const handleCreate = async (data) => {
    await createProduct(data);
    setShowForm(false);
    loadProducts();
  };

  const handleUpdate = async (data) => {
    await updateProduct(editing.id, data);
    setEditing(null);
    setShowForm(false);
    loadProducts();
  };

  const handleDelete = async (id) => {
    if (window.confirm("\t\t     ︵\nSure?\t( ͠° ͟  °)")) {
      await deleteProduct(id);
      loadProducts();
    }
  };

  // === Sorter ===
  const handleSortChange = (column, direction) => {
    setSortBy(column);
    setSortDirection(direction);
  };

  // === Filter & Sort ===
  const filteredProducts = useMemo(() => {
    let result = [...products];

    if (search) {
      const s = search.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(s) ||
          p.category?.toLowerCase().includes(s) ||
          p.brand?.toLowerCase().includes(s)
      );
    }

    if (categoryFilter) {
      result = result.filter((p) => p.category === categoryFilter);
    }

    result.sort((a, b) => {
      const valA = a[sortBy];
      const valB = b[sortBy];

      if (typeof valA === "string") {
        return sortDirection === "asc"
          ? valA.localeCompare(valB)
          : valB.localeCompare(valA);
      } else {
        return sortDirection === "asc" ? valA - valB : valB - valA;
      }
    });

    return result;
  }, [products, search, categoryFilter, sortBy, sortDirection]);

  // === Categories for Dropdown dynamic ===
  const categories = Array.from(new Set(products.map((p) => p.category))).filter(Boolean);

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
        Product Manager
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

            <TextField
              select
              label="Category"
              variant="outlined"
              size="small"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              sx={{ width: 200 }}
            >
              <MenuItem value="">All</MenuItem>
              {categories.map((cat) => (
                <MenuItem key={cat} value={cat}>
                  {cat}
                </MenuItem>
              ))}
            </TextField>

            <Button
              variant="contained"
              color="primary"
              onClick={() => setShowForm(true)}
              sx={{ whiteSpace: "nowrap" }}
            >
              New Product
            </Button>
          </Box>

          {/* Table */}
          <ProductTable
            products={filteredProducts}
            onEdit={(p) => {
              setEditing(p);
              setShowForm(true);
            }}
            onDelete={handleDelete}
            sortBy={sortBy}
            sortDirection={sortDirection}
            onSortChange={handleSortChange}
          />
        </>
      ) : (
        <ProductForm
          initialData={editing || {}}
          onSubmit={editing ? handleUpdate : handleCreate}
          onCancel={() => {
            setEditing(null);
            setShowForm(false);
          }}
        />
      )}
    </Box>
  );
}
