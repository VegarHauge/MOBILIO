import axios from "axios";
import { API_BASE_URL, RECOMMENDATION_API_BASE_URL } from "../config";

const BASE = `${API_BASE_URL}/products`;

export const getProducts = async () => {
  const res = await axios.get(BASE);
  return res.data;
};

export const createProduct = async (data) => {
  const token = localStorage.getItem("token");
  const config = {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  };
  
  // Don't manually set Content-Type for FormData - axios will handle it with boundary
  
  const res = await axios.post(BASE, data, config);
  return res.data;
};

export const updateProduct = async (id, data) => {
  const token = localStorage.getItem("token");
  const config = {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  };
  
  // Don't manually set Content-Type for FormData - axios will handle it with boundary
  
  const res = await axios.put(`${BASE}/${id}`, data, config);
  return res.data;
};

export const deleteProduct = async (id) => {
  const token = localStorage.getItem("token");
  const config = {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  };
  
  await axios.delete(`${BASE}/${id}`, config);
};

export const getSimilarProducts = async (productId, limit = 8) => {
  const res = await axios.get(`${RECOMMENDATION_API_BASE_URL}/similar/${productId}?limit=${limit}`);
  return res.data;
};

export const getCoPurchasedProducts = async (productId, limit = 8) => {
  const res = await axios.get(`${RECOMMENDATION_API_BASE_URL}/copurchase/${productId}?limit=${limit}`);
  return res.data;
};
