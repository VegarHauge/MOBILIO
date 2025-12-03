import React from "react";
import { Box, Typography } from "@mui/material";
import ProductCard from "./ProductCard";

export default function ProductRow({ title, products, loading = false }) {
  if (loading) {
    return (
      <Box sx={{ mb: 6 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          {title}
        </Typography>
        <Box
          sx={{
            display: "flex",
            overflowX: "auto",
            gap: 2,
            pb: 2,
            "&::-webkit-scrollbar": {
              height: 8,
            },
            "&::-webkit-scrollbar-track": {
              backgroundColor: "#f1f1f1",
              borderRadius: 4,
            },
            "&::-webkit-scrollbar-thumb": {
              backgroundColor: "#888",
              borderRadius: 4,
              "&:hover": {
                backgroundColor: "#555",
              },
            },
          }}
        >
          {[...Array(4)].map((_, index) => (
            <Box
              key={index}
              sx={{
                minWidth: 300,
                height: 360,
                backgroundColor: "#f5f5f5",
                borderRadius: 2,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Loading...
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    );
  }

  if (!products || products.length === 0) {
    return (
      <Box sx={{ mb: 6 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          {title}
        </Typography>
        <Typography color="text.secondary" sx={{ py: 4 }}>
          No recommendations available at the moment.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 6 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        {title}
      </Typography>
      <Box
        sx={{
          display: "flex",
          overflowX: "auto",
          gap: 2,
          pb: 2,
          "&::-webkit-scrollbar": {
            height: 8,
          },
          "&::-webkit-scrollbar-track": {
            backgroundColor: "#f1f1f1",
            borderRadius: 4,
          },
          "&::-webkit-scrollbar-thumb": {
            backgroundColor: "#888",
            borderRadius: 4,
            "&:hover": {
              backgroundColor: "#555",
            },
          },
        }}
      >
        {products.map((product) => (
          <Box key={product.id} sx={{ minWidth: 300, flexShrink: 0 }}>
            <ProductCard product={product} />
          </Box>
        ))}
      </Box>
    </Box>
  );
}