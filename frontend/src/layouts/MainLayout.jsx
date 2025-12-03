// src/layouts/MainLayout.jsx
import React, { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Typography,
  Box,
  Button,
  IconButton,
  Menu,
  MenuItem,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import ProductsButton from "../components/ProductsButton";
import { AuthContext } from "../context/AuthContext";

export default function MainLayout({ children, hero, navColor = "light" }) {
  // Farben
  const isLight = navColor === "light";
  const textColor = isLight ? "#FFFFFF" : "#000000";
  const hoverColor = isLight ? "#1e7a1e" : "#555555";
  const borderColor = isLight ? "#AAA" : "#333";
  const menuTextColor = "#000000";

  // Auth Context
  const { isAuthenticated, isAdmin, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  // Mobile-Menu
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (e) => setAnchorEl(e.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const handleLogout = () => {
    logout();           
    handleClose();
    navigate("/login");
  };

  return (
    <>
      {/* Header + Hero */}
      <div style={{ position: "relative", top: 0, zIndex: 20 }}>
        {/* Header */}
        <Box
          sx={{
            height: "100px",
            display: "flex",
            justifyContent: "space-between",
            background: "transparent",
            alignItems: "center",
            px: { xs: 1, sm: 3 },
            position: "absolute",
            width: "100%",
            top: 0,
            color: textColor,
            zIndex: 30,
            boxSizing: "border-box",
            overflowX: "hidden",
          }}
        >
          <Button
            component={Link}
            to="/"
            sx={{
              m: 0,
              color: textColor,
              textTransform: "none",
              fontSize: { xs: "1.5rem", sm: "2rem" },
              fontWeight: 700,
              "&:hover": { color: hoverColor, background: "none" },
              textDecoration: "none",
            }}
          >
            Mobilio
          </Button>

          {/* Navigation */}
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            {/* Desktop */}
            <Box
              sx={{
                display: { xs: "none", sm: "flex" },
                gap: { xs: 0.5, sm: 2 },
                alignItems: "center",
              }}
            >
              {isAdmin && (
                <Button
                  component={Link}
                  to="/admin/dashboard"
                  variant="text"
                  sx={{ color: textColor, "&:hover": { color: hoverColor } }}
                >
                  Admin
                </Button>
              )}

              {/*<ProductsButton textColor={textColor} hoverColor={hoverColor} />*/}

              <Button
                component={Link}
                to="/products"
                variant="text"
                sx={{ color: textColor, "&:hover": { color: hoverColor } }}
              >
                Produkter
              </Button>

              <Button
                component={Link}
                to="/cart"
                variant="text"
                sx={{ color: textColor, "&:hover": { color: hoverColor } }}
              >
                Handlekurv
              </Button>

              {isAuthenticated ? (
                <Button
                  variant="outlined"
                  onClick={handleLogout}
                  sx={{
                    borderColor,
                    color: borderColor,
                    "&:hover": {
                      backgroundColor: isLight ? "#FFFFFF" : "#000000",
                      color: isLight ? "#000000" : "#FFFFFF",
                      borderColor: isLight ? "#FFFFFF" : "#000000",
                    },
                  }}
                >
                  Logout
                </Button>
              ) : (
                <Button
                  component={Link}
                  to="/login"
                  variant="outlined"
                  sx={{
                    borderColor,
                    color: borderColor,
                    "&:hover": {
                      backgroundColor: isLight ? "#FFFFFF" : "#000000",
                      color: isLight ? "#000000" : "#FFFFFF",
                      borderColor: isLight ? "#FFFFFF" : "#000000",
                    },
                  }}
                >
                  Login
                </Button>
              )}
            </Box>

            {/* Mobile-Menü-Icon */}
            <IconButton
              sx={{ display: { xs: "block", sm: "none" }, color: textColor }}
              onClick={handleClick}
            >
              <MenuIcon />
            </IconButton>

            {/* Mobile-Menü */}
            <Menu
              anchorEl={anchorEl}
              open={open}
              onClose={handleClose}
              anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
              transformOrigin={{ vertical: "top", horizontal: "right" }}
              PaperProps={{ sx: { mt: 1, width: { xs: "auto", minWidth: 200 } } }}
            >
              {isAdmin && (
                <MenuItem onClick={handleClose}>
                  <Button
                    component={Link}
                    to="/admin/dashboard"
                    fullWidth
                    sx={{ color: menuTextColor, justifyContent: "flex-start" }}
                  >
                    Admin
                  </Button>
                </MenuItem>
              )}

              <MenuItem onClick={handleClose}>
                <ProductsButton
                  textColor={menuTextColor}
                  hoverColor={hoverColor}
                  fullWidth
                />
              </MenuItem>

              <MenuItem onClick={handleClose}>
                <Button
                  component={Link}
                  to="/cart"
                  fullWidth
                  sx={{ color: menuTextColor, justifyContent: "flex-start" }}
                >
                  Handlekurv
                </Button>
              </MenuItem>

              {isAuthenticated ? (
                <MenuItem onClick={handleLogout}>
                  <Button
                    fullWidth
                    sx={{
                      borderColor,
                      color: menuTextColor,
                      justifyContent: "flex-start",
                      "&:hover": {
                        backgroundColor: isLight ? "#FFFFFF" : "#000000",
                        color: isLight ? "#000000" : "#FFFFFF",
                        borderColor: isLight ? "#FFFFFF" : "#000000",
                      },
                    }}
                  >
                    Logout
                  </Button>
                </MenuItem>
              ) : (
                <MenuItem onClick={handleClose}>
                  <Button
                    component={Link}
                    to="/login"
                    fullWidth
                    sx={{
                      borderColor,
                      color: menuTextColor,
                      justifyContent: "flex-start",
                      "&:hover": {
                        backgroundColor: isLight ? "#FFFFFF" : "#000000",
                        color: isLight ? "#000000" : "#FFFFFF",
                        borderColor: isLight ? "#FFFFFF" : "#000000",
                      },
                    }}
                  >
                    Login
                  </Button>
                </MenuItem>
              )}
            </Menu>
          </Box>
        </Box>

        {/* Hero */}
        {hero && <div>{hero}</div>}
      </div>

      {/* Inhalt */}
      <Box sx={{ flex: "1 0 auto", pt: hero ? 0 : "100px" }}>{children}</Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{ mt: "auto", py: 2, textAlign: "center", bgcolor: "grey.200" }}
      >
        <Typography variant="body2">© 2025 Mobilio</Typography>
      </Box>
    </>
  );
}
