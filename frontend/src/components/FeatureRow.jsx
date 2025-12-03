// src/components/FeatureRow.jsx
import { Grid, Box, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";
import React from "react";

export default function FeatureRow({ title, text, image, link, reverse = false }) {
  return (
    <Grid
      container
      spacing={4}
      alignItems="center"
      sx={{
        py: 8,
        px: { xs: 2, md: 6 },
        flexDirection: reverse ? "row-reverse" : "row",
      }}
    >
      {/* Bild mit Link */}
      <Grid item xs={6} md={6}>
        <Box
          component={Link}
          to={link}
          sx={{
            display: "block",
            borderRadius: 3,
            boxShadow: 3,
            overflow: "hidden",
            cursor: "pointer",
          }}
        >
          <Box
            component="img"
            src={image}
            alt={title}
            sx={{
              width: "100%",
              height: "auto",
              maxHeight: "400px",
              transition: "transform 0.3s ease",
              "&:hover": { transform: "scale(1.05)" },
              display: "block",
            }}
          />
        </Box>
      </Grid>

      {/* Text area */}
      <Grid item xs={6} md={6}>
        <Typography variant="h4" gutterBottom>
          {title}
        </Typography>
        <Typography paragraph sx={{ mb: 3 }}>
          {text}
        </Typography>
        <Button
          component={Link}
          to={link}
          variant="contained"
          sx={{
            backgroundColor: "#000",
            "&:hover": { backgroundColor: "#333" },
          }}
        >
          Oppdag {title}
        </Button>
      </Grid>
    </Grid>
  );
}
