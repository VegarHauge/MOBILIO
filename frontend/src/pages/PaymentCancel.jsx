// PaymentCancel.jsx
import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { API_BASE_URL } from "../config"

const PaymentCancel = () => {
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    
    if (sessionId) {
      // Optionally call cancel endpoint
      const userToken = localStorage.getItem("token");
      
      fetch(`${API_BASE_URL}/payment/cancel/${sessionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        }
      }).catch(err => console.error('Cancel notification failed:', err));
    }
  }, [searchParams]);

  return (
    <div>
      <h1>Payment Cancelled</h1>
      <p>Your payment was cancelled. Your cart items are still preserved.</p>
      <a href="/cart">Return to Cart</a>
    </div>
  );
};

export default PaymentCancel;