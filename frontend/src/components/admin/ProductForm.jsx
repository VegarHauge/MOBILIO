import { Box, Button, TextField, Typography } from "@mui/material";
import React, { useState } from "react";

export default function ProductForm({ initialData = {}, onSubmit, onCancel }) {
  const [form, setForm] = useState({
    name: initialData.name || "",
    price: initialData.price || "",
    description: initialData.description || "",
    brand: initialData.brand || "",
    category: initialData.category || "",
    stock: initialData.stock || 0,
    picture: initialData.picture || ""
  });

  const [file, setFile] = useState(null);

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Use FormData to properly handle file uploads
    const formData = new FormData();
    
    // Only add fields that have values (for update to work properly)
    // FormData will send as strings, FastAPI will parse them based on Form() type hints
    if (form.name && form.name.trim()) {
      formData.append('name', form.name.trim());
    }
    if (form.price) {
      formData.append('price', form.price);
    }
    if (form.description && form.description.trim()) {
      formData.append('description', form.description.trim());
    }
    if (form.brand && form.brand.trim()) {
      formData.append('brand', form.brand.trim());
    }
    if (form.category && form.category.trim()) {
      formData.append('category', form.category.trim());
    }
    if (form.stock !== undefined && form.stock !== null && form.stock !== '') {
      formData.append('stock', form.stock);
    }
    
    // Add the actual file if one was selected
    if (file) {
      formData.append('image', file);
    }
    
    onSubmit(formData);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <Typography variant="h6">
        {initialData.id ? "Edit Product" : "New Product"}
      </Typography>

      <TextField label="Name" name="name" value={form.name} onChange={handleChange} fullWidth margin="normal" />
      <TextField label="Price" name="price" type="number" value={form.price} onChange={handleChange} fullWidth margin="normal" />
      <TextField label="Description" name="description" value={form.description} onChange={handleChange} fullWidth margin="normal" multiline rows={3} />
      <TextField label="Brand" name="brand" value={form.brand} onChange={handleChange} fullWidth margin="normal" />
      <TextField label="Category" name="category" value={form.category} onChange={handleChange} fullWidth margin="normal" />
      <TextField label="Stock" name="stock" type="number" value={form.stock} onChange={handleChange} fullWidth margin="normal" />
      <Button variant="contained" component="label" sx={{ mt: 1 }}>
        Upload picture
        <input type="file" hidden onChange={handleFileChange} />
      </Button>

      <Box sx={{ mt: 3, display: "flex", gap: 2 }}>
        <Button variant="contained" type="submit" color="primary">
          Safe
        </Button>
        <Button variant="outlined" onClick={onCancel}>
          Cancel
        </Button>
      </Box>
    </Box>
  );
}
