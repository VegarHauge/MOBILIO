import { API_BASE_URL } from "../config"
import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const processingRef = useRef(false); // Prevent multiple calls

  useEffect(() => {
    const processPayment = async () => {
      const sessionId = searchParams.get('session_id');
      
      if (!sessionId) {
        setError('No session ID found');
        setLoading(false);
        return;
      }

      // Prevent multiple simultaneous calls
      if (processingRef.current) {
        return;
      }
      processingRef.current = true;

      try {
        const userToken = localStorage.getItem("token");
        
        // Call backend to complete the order
        const response = await fetch(`${API_BASE_URL}/payment/success/${sessionId}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${userToken}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to process payment');
        }

        const result = await response.json();
        setOrder(result);
      } catch (err) {
        console.error('Error processing payment:', err);
        setError('Failed to process payment completion');
      } finally {
        setLoading(false);
        processingRef.current = false;
      }
    };

    processPayment();
  }, [searchParams]);

  if (loading) return <div>Processing your payment...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Payment Successful!</h1>
      {order && (
        <div>
          <p>Order ID: {order.order_id}</p>
          <p>Total: ${order.total_amount}</p>
          <p>Your cart has been cleared and order created successfully!</p>
          <a href="/">back to page</a>
        </div>
      )}
    </div>
  );
};

export default PaymentSuccess;