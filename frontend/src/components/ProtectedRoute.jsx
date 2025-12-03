import React, { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";



 
const ProtectedRoute = ({ children, admin = false }) => {
  const { isAuthenticated, isAdmin } = useContext(AuthContext);
  
  // DEV-BYPASS
  if(false) {
    console.warn("DEV MODE: Auth-Check deactivated")
    return children;
  }
  
  // Check loggin
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check admin
  if (admin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  // Zugriff erlaubt
  return children;
};

export default ProtectedRoute;
