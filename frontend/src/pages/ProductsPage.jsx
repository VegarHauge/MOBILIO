import React, { useEffect, useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import ProductCard from "../components/ProductCard";
import HeroSection from "../components/HeroSection";
import {
  Box,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  TextField,
  InputAdornment,
  Button,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { getProducts } from "../api/products";
import { getImageUrl } from "../utils/s3Utils";

export default function ProductsPage() {
  const { category } = useParams();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter states
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState(category || "all");
  const [selectedBrand, setSelectedBrand] = useState("all");
  const [sortBy, setSortBy] = useState("rating");
  const [sortDirection, setSortDirection] = useState("desc");

  // Dynamic Lists
  const [categories, setCategories] = useState(["all"]);
  const [brands, setBrands] = useState(["all"]);

  // Hero-Config
  const heroImages = {
    phones: "smartphones_hero.png",
    headphones: "headphones_hero.png",
    accessories: "accessories_hero.png",
    all: "products_hero.png",
  };

  const heroTitles = {
    phones: "Smartphones",
    headphones: "Headphones",
    accessories: "Accessories",
    all: "Products",
  };

  // load products
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getProducts();
        setProducts(data);

        const cats = Array.from(new Set(data.map((p) => p.category))).filter(Boolean);
        const brands = Array.from(new Set(data.map((p) => p.brand))).filter(Boolean);
        setCategories(["all", ...cats]);
        setBrands(["all", ...brands]);
      } catch (err) {
        const message = err.response?.data?.detail || "Unable to load products.";
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  // Filter reset
  const handleResetFilters = () => {
    setSearch("");
    setSelectedCategory("all");
    setSelectedBrand("all");
    setSortBy("rating");
    setSortDirection("desc");
  };

  // Filter + Sort (clientseitig)
  const filteredProducts = useMemo(() => {
    let result = [...products];

    // searchfilter
    if (search.trim()) {
      const s = search.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(s) ||
          p.category?.toLowerCase().includes(s) ||
          p.brand?.toLowerCase().includes(s)
      );
    }

    // categorie-Filter
    if (selectedCategory !== "all") {
      result = result.filter((p) => p.category === selectedCategory);
    }

    // brand filter
    if (selectedBrand !== "all") {
      result = result.filter((p) => p.brand === selectedBrand);
    }

    // Sorting
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
  }, [products, search, selectedCategory, selectedBrand, sortBy, sortDirection]);

  return (
    <MainLayout
      hero={
        <HeroSection
          title={heroTitles[selectedCategory] || "Produkter"}
          subtitle="Oppdag våre Produkter"
          backgroundImage={getImageUrl(heroImages[selectedCategory], true) || getImageUrl("products_hero.png", true)}
          height="60vh"
        />
      }
      navColor="light"
    >
      {loading ? (
        <Box sx={{ p: 4, display: "flex", justifyContent: "center" }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Typography sx={{ p: 4, color: "error.main" }}>Error: {error}</Typography>
      ) : (
        <Grid sx={{ p: 4 }}>
          {/* Filter Section */}
          <Box
            sx={{
              mb: 4,
              display: "flex",
              gap: 2,
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >
            <TextField
              label="Suche"
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

            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Categorie</InputLabel>
              <Select
                value={selectedCategory}
                label="Categorie"
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map((cat) => (
                  <MenuItem key={cat} value={cat}>
                    {cat === "all" ? "All" : heroTitles[cat] || cat}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Brand</InputLabel>
              <Select
                value={selectedBrand}
                label="Brand"
                onChange={(e) => setSelectedBrand(e.target.value)}
              >
                {brands.map((brand) => (
                  <MenuItem key={brand} value={brand}>
                    {brand === "all" ? "All" : brand}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Sort</InputLabel>
              <Select
                value={sortBy}
                label="Sort"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="name">Name</MenuItem>
                <MenuItem value="price">Price</MenuItem>
                <MenuItem value="stock">Stock</MenuItem>
                <MenuItem value="rating">Rating</MenuItem>
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Direction</InputLabel>
              <Select
                value={sortDirection}
                label="Direction"
                onChange={(e) => setSortDirection(e.target.value)}
              >
                <MenuItem value="asc">ascending</MenuItem>
                <MenuItem value="desc">descending</MenuItem>
              </Select>
            </FormControl>

            {/* 🔹 Reset Button */}
            <Button
              variant="outlined"
              color="danger"
              onClick={handleResetFilters}
              sx={{ height: 40 }}
            >
              Reset
            </Button>
          </Box>

          {/* Product Grid */}
          {filteredProducts.length === 0 ? (
            <Typography sx={{ p: 4 }}>No products found</Typography>
          ) : (
            <Grid container spacing={2} justifyContent="center" sx={{ my: 4 }}>
              {filteredProducts.map((product) => (
                <Grid item xs={12} sm={6} md={3} key={product.id}>
                  <ProductCard product={product} />
                </Grid>
              ))}
            </Grid>
          )}
        </Grid>
      )}
    </MainLayout>
  );
}
