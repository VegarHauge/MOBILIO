import React from "react";
import {
  Card,
  CardMedia,
  CardContent,
  Typography,
  Box,
} from "@mui/material";
import { Link } from "react-router-dom";
import { getImageUrl } from "../utils/s3Utils";

export default function ProductCard({ product }) {
  const productId = product.id || product.product_id || product._id;
  
  return (
    <Card
      component={Link}
      to={`/product/${productId}`}
      sx={{
        width: 300, // Fixed width
        height: "360px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        textDecoration: "none",
        borderRadius: 2,
        boxShadow: 0,
        overflow: "hidden",
        transition: "transform 0.2s ease, box-shadow 0.2s ease",
        "&:hover": {
          transform: "translateY(-4px)",
          boxShadow: 3,
        },
      }}
    >
      <Box
        sx={{
          flexShrink: 0,
          height: "200px", // Fixed height for image
          bgcolor: "#FAFAFA",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden",
        }}
      >
        <CardMedia
          component="img"
          image={getImageUrl(product.image || product.picture) || "/placeholder.png"}
          alt={product.name}
          sx={{
            maxHeight: "100%",
            maxWidth: "100%",
            objectFit: "contain",
            display: "block",
          }}
        />
      </Box>
      <CardContent
        sx={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          flexGrow: 1,
          overflow: "hidden",
          minHeight: 120,
        }}
      >
        <Typography
          variant="subtitle1"
          fontWeight="bold"
          sx={{
            mb: 0.5,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {product.name}
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            flexGrow: 1,
            overflow: "hidden",
            textOverflow: "ellipsis",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
          }}
        >
          {product.description}
        </Typography>
        <Typography
          variant="subtitle1"
          fontWeight="bold"
          sx={{
            mt: 1,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          NOK {Number(product.price).toFixed(2)}
        </Typography>
      </CardContent>
    </Card>
  );
}
