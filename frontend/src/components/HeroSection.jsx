import React from "react";
import { Typography, Button, Box } from "@mui/material";

export default function HeroSection({
  title = "Welcome",
  subtitle = "Discover our products.",
  buttonText,
  buttonLink,
  backgroundImage = "/default_hero.png",
  height = "100vh", // Neue Prop für Höhe
}) {
  return (
    <Box
      sx={{
        height, // Dynamische Höhe
        backgroundImage: `url('${backgroundImage}')`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-start",
        color: "white",
        px: { xs: 2, sm: 6 }, // Reduziertes Padding auf Mobile
        position: "relative",
      }}
    >
      {/* Overlay */}
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          bgcolor: "rgba(0,0,0,0.4)",
        }}
      />

      {/* Hero-Inhalt */}
      <Box
        sx={{
          position: "relative",
          zIndex: 1,
          maxWidth: { xs: "90%", sm: "600px" }, // Responsive Breite
        }}
      >
        <Typography
          variant="h2"
          fontWeight="bold"
          gutterBottom
          sx={{
            fontSize: { xs: "2rem", sm: "3rem", md: "4rem" }, // Responsive Schriftgröße
          }}
        >
          {title}
        </Typography>
        <Typography
          variant="h6"
          paragraph
          sx={{
            fontSize: { xs: "1rem", sm: "1.25rem" }, // Responsive Schriftgröße
          }}
        >
          {subtitle}
        </Typography>
        {buttonText && buttonLink && (
          <Button
            variant="contained"
            href={buttonLink}
            sx={{
              backgroundColor: "#000",
              "&:hover": { backgroundColor: "#333" },
              fontSize: { xs: "0.875rem", sm: "1rem" }, // Responsive Button-Text
              px: { xs: 2, sm: 3 }, // Responsive Padding
            }}
          >
            {buttonText}
          </Button>
        )}
      </Box>
    </Box>
  );
}