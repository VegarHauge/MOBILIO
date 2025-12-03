// src/components/ProductsButton.jsx
import { Button } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

export default function ProductsButton({ textColor = "#FFFFFF", hoverColor = "#1e7a1e" }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleClick = () => {
    if (location.pathname === "/") {
      window.scrollTo({
        top: window.innerHeight,
        behavior: "smooth",
      });
    } else {
      navigate("/products");
    }
  };

  return (
    <Button
      variant="text"
      onClick={handleClick}
      sx={{ color: textColor, "&:hover": { color: hoverColor } }}
    >
      Produkter
    </Button>
  );
}
