import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axios from "axios";
import MainLayout from "../layouts/MainLayout";
import ProductCard from "../components/ProductCard";
import ProductRow from "../components/ProductRow";
import { Box, Typography, CircularProgress, Button, Grid, Alert } from "@mui/material";
import { API_BASE_URL } from "../config";
import { getImageUrl } from "../utils/s3Utils";
import { getSimilarProducts, getCoPurchasedProducts } from "../api/products";


export default function ProductPage({ isLoggedIn = false }) {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(() =>
    Boolean(localStorage.getItem("token"))
  );
  const [addingToCart, setAddingToCart] = useState(false);
  const [cartFeedback, setCartFeedback] = useState(null);
  const [similarProducts, setSimilarProducts] = useState([]);
  const [coPurchasedProducts, setCoPurchasedProducts] = useState([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [loadingCoPurchased, setLoadingCoPurchased] = useState(false);
  useEffect(() => {
    setLoading(true);
    setError(null);

    const fetchProduct = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/products/${id}`);
        setProduct(response.data);
      } catch (err) {
        const message = err.response?.data?.detail || "Unable to load product details.";
        setError(message);
        setProduct(null);
      } finally {
        setLoading(false);
      }
    };

    const fetchRecommendations = async () => {
      // Fetch similar products
      setLoadingSimilar(true);
      try {
        const similarData = await getSimilarProducts(id);
        setSimilarProducts(similarData);
      } catch (err) {
        console.error("Failed to fetch similar products:", err);
        setSimilarProducts([]);
      } finally {
        setLoadingSimilar(false);
      }

      // Fetch co-purchased products
      setLoadingCoPurchased(true);
      try {
        const coPurchasedData = await getCoPurchasedProducts(id);
        setCoPurchasedProducts(coPurchasedData);
      } catch (err) {
        console.error("Failed to fetch co-purchased products:", err);
        setCoPurchasedProducts([]);
      } finally {
        setLoadingCoPurchased(false);
      }
    };

    fetchProduct();
    fetchRecommendations();
  }, [id]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(Boolean(token));

    if (token) {
      axios.defaults.headers.common.Authorization = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common.Authorization;
    }

    const handleStorageChange = () => {
      const updatedToken = localStorage.getItem("token");
      setIsAuthenticated(Boolean(updatedToken));
      if (updatedToken) {
        axios.defaults.headers.common.Authorization = `Bearer ${updatedToken}`;
      } else {
        delete axios.defaults.headers.common.Authorization;
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const handleAddToCart = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      setIsAuthenticated(false);
      setCartFeedback({
        type: "error",
        message: "Please log in to add products to your cart.",
      });
      return;
    }

    setAddingToCart(true);
    setCartFeedback(null);

    try {
      await axios.post(`${API_BASE_URL}/cart/items`, {
        product_id: product.id,
        quantity: 1,
      });

      setCartFeedback({
        type: "success",
        message: `${product.name} was added to your cart.`,
      });
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("token_type");
        setIsAuthenticated(false);
        setCartFeedback({
          type: "error",
          message: "Your session expired. Please log in again to continue shopping.",
        });
        return;
      }

      const message =
        err.response?.data?.detail ||
        "Couldn't add this product to your cart. Please try again.";
      setCartFeedback({
        type: "error",
        message,
      });
    } finally {
      setAddingToCart(false);
    }
  };

  return (
    <MainLayout navColor="dark">
      {loading ? (
        <Box sx={{ p: 4, display: "flex", justifyContent: "center" }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Typography sx={{ p: 4, color: "error.main" }}>
          Error: {error}
        </Typography>
      ) : !product ? (
        <Typography sx={{ p: 4 }}>Product not found</Typography>
      ) : (
        <>
          <Grid
            container
            spacing={4}
            alignItems="center"
            justifyContent="center"
            sx={{
              py: 8,
              px: { xs: 2, md: 6 },
            }}
          >
            {/* Bild */}
            <Grid item xs={12} md={6}>
              <Box
                sx={{
                  display: "block",
                  borderRadius: 0,
                  boxShadow: 0,
                  overflow: "hidden",
                }}
              >
                <Box
                  component="img"
                  src={getImageUrl(product.picture)}
                  alt={product.name}
                  sx={{
                    width: "100%",
                    height: "auto",
                    maxHeight: "400px",
                    /*maxHeight: "80vh",*/
                    objectFit: "contain",
                    display: "block",
                  }}
                />
              </Box>
            </Grid>

            {/* Textbereich */}
            <Grid item xs={12} md={6}>
              <Typography
                variant="h4"
                gutterBottom
                sx={{
                  wordBreak: "break-word",
                  overflowWrap: "anywhere",
                }}
              >
                {product.name}
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                {product.brand}
              </Typography>
              <Typography variant="h5" sx={{ mb: 2 }}>
                NOK {product.price}
              </Typography>
              <Typography paragraph color="text.secondary">
                {product.description}
              </Typography>
              {isAuthenticated ? (
                <Button
                  variant="contained"
                  fullWidth
                  onClick={handleAddToCart}
                  disabled={addingToCart}
                  sx={{
                    backgroundColor: "#000000",
                    color: "#FFFFFF",
                    "&:hover": { borderColor: "#333", color: "#333" },
                  }}
                >
                  {addingToCart ? "Adding..." : "Add to Cart"}
                </Button>
              ) : (
                <Button
                  component={Link}
                  to="/login"
                  variant="outlined"
                  fullWidth
                  sx={{
                    borderColor: "#000000",
                    color: "#000000",
                    "&:hover": {
                      backgroundColor: "#000000",
                      color: "#FFFFFF",
                    },
                  }}
                >
                  Login to buy
                </Button>
              )}
              {cartFeedback && (
                <Alert severity={cartFeedback.type} sx={{ mt: 2 }}>
                  {cartFeedback.message}
                </Alert>
              )}
            </Grid>
          </Grid>

          {/* Recommended Products Section */}
          <Box sx={{ py: 4, px: { xs: 2, md: 6 } }}>
            <ProductRow
              title="Similar Products"
              products={similarProducts}
              loading={loadingSimilar}
            />
            <ProductRow
              title="Others Also Purchased"
              products={coPurchasedProducts}
              loading={loadingCoPurchased}
            />
          </Box>
        </>
      )}
    </MainLayout>
  );
}