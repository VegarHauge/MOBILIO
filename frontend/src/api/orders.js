import axios from "axios";
import { API_BASE_URL } from "../config";

const BASE = `${API_BASE_URL}/orders`;

export const getOrders = async () => {
    const res = await axios.get(BASE);
    return res.data;
};

export const deleteOrder = async (id) => {
    await axios.delete(`${BASE}/${id}`);
};

export const updateOrder = async (id, data) => {
    const res = await axios.put(`${BASE}/${id}`, data);
    return res.data;
};