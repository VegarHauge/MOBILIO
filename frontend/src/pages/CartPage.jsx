import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Remove as RemoveIcon,
  ShoppingCart as ShoppingCartIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  CircularProgress,
  Container,
  Divider,
  IconButton,
  Typography,
} from "@mui/material";
import axios from "axios";
import React, { useEffect, useState } from "react";
import { API_BASE_URL } from "../config";
import MainLayout from "../layouts/MainLayout";
import { getImageUrl } from "../utils/s3Utils";


export default function CartPage() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [checkingOut, setCheckingOut] = useState(false);

  const fetchCart = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/cart/`);
      setCart(response.data);
    } catch (err) {
      const message = err.response?.data?.detail || "Unable to load cart.";
      setError(message);
      setCart(null);
    } finally {
      setLoading(false);
    }
  };


  const incrementItem = async (id) => {
    await axios.patch(`${API_BASE_URL}/cart/items/${id}/increment`);
    fetchCart();
  };

  const decrementItem = async (id) => {
    
    await axios.patch(`${API_BASE_URL}/cart/items/${id}/decrement`);
    fetchCart();
  };

  const removeItem = async (id) => {
    await axios.delete(`${API_BASE_URL}/cart/items/${id}`);
    fetchCart();
  };

const handleCheckout = async () => {
  setCheckingOut(true);
  try {
    const userToken = localStorage.getItem("token");
    
    // Create checkout session
    const response = await fetch(`${API_BASE_URL}/payment/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        success_url: `${window.location.origin}/payment/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${window.location.origin}/payment/cancel?session_id={CHECKOUT_SESSION_ID}`
      })
    });

    const { checkout_url } = await response.json();
    // Redirect user to Stripe
    window.location.href = checkout_url;
  } catch (error) {
    console.error('Checkout failed:', error);
    setError('Failed to process checkout. Please try again.');
  } finally {
    setCheckingOut(false);
  }
};

  useEffect(() => {
    fetchCart();
  }, []);

  if (loading) {
    return (
      <MainLayout navColor="dark">
        <Box sx={{ display: "flex", justifyContent: "center", mt: 10 }}>
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <MainLayout navColor="dark">
        <Container maxWidth="lg" sx={{ py: 6, textAlign: "center" }}>
          <Typography variant="h4">Your cart is empty.</Typography>
        </Container>
      </MainLayout>
    );
  }

  return (
    <MainLayout navColor="dark">
      <Container maxWidth="lg" sx={{ py: 4, px: { xs: 2, sm: 3, md: 4 } }}>
        <Typography variant="h4" gutterBottom>
          Your Cart
        </Typography>

        {/* Produktzeilen */}
        {cart.items.map((item) => (
          <Box
            key={item.id}
            sx={{
              display: "flex",
              flexDirection: { xs: "column", sm: "row" },
              alignItems: { xs: "flex-start", sm: "center" },
              justifyContent: "space-between",
              gap: 2,
              width: "100%",
              p: 2,
              mb: 2,
              borderRadius: 2,
              boxShadow: 1,
              bgcolor: "background.paper",
            }}
          >
            <Box
              component="img"
              src={getImageUrl(item.product.picture)}
              alt={item.product.name}
              sx={{
                width: { xs: "100%", sm: 100 },
                height: 100,
                objectFit: "cover",
                borderRadius: 1,
              }}
            />

            <Box
              sx={{
                display: "flex",
                flexDirection: { xs: "column", sm: "row" },
                alignItems: { xs: "flex-start", sm: "center" },
                justifyContent: "space-between",
                flex: 1,
                gap: 2,
                width: "100%",
              }}
            >
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6">{item.product.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  NOK {item.product.price.toFixed(2)} / unit
                </Typography>
              </Box>

              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  flexShrink: 0,
                }}
              >
                <IconButton size="small" onClick={() => decrementItem(item.id)}>
                  <RemoveIcon />
                </IconButton>
                <Typography>{item.quantity}</Typography>
                <IconButton size="small" onClick={() => incrementItem(item.id)}>
                  <AddIcon />
                </IconButton>
                <IconButton
                  color="error"
                  onClick={() => removeItem(item.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </Box>

              <Typography
                variant="h6"
                sx={{
                  minWidth: 80,
                  textAlign: { xs: "left", sm: "right" },
                  flexShrink: 0,
                }}
              >
                NOK {(item.price * item.quantity).toFixed(2)}
              </Typography>
            </Box>
          </Box>
        ))}

        <Divider sx={{ my: 4 }} />

        {/* Footer */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "flex-end",
            alignItems: "center",
            gap: 2,
          }}
        >
          <Typography variant="h5">
            Total: NOK {cart.total_price.toFixed(2)}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={checkingOut ? <CircularProgress size={20} color="inherit" /> : <ShoppingCartIcon />}
            onClick={handleCheckout}
            disabled={checkingOut}
            sx={{ px: 4 }}
          >
            {checkingOut ? 'Processing...' : 'Proceed to Checkout'}
          </Button>
        </Box>
      </Container>
    </MainLayout>
  );
}
