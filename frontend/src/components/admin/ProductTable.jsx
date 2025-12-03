import React from "react";
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableSortLabel,
  IconButton,
  Tooltip,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

export default function ProductTable({
  products,
  onEdit,
  onDelete,
  sortBy,
  sortDirection,
  onSortChange,
}) {
  const handleSort = (column) => {
    if (sortBy === column) {
      onSortChange(column, sortDirection === "asc" ? "desc" : "asc");
    } else {
      onSortChange(column, "asc");
    }
  };

  return (
    <Table>
      <TableHead>
        <TableRow>
          {[
            { key: "id", label: "ID" },
            { key: "name", label: "Name" },
            { key: "price", label: "Price" },
            { key: "category", label: "Category" },
            { key: "stock", label: "Stock" },
          ].map((col) => (
            <TableCell key={col.key}>
              <TableSortLabel
                active={sortBy === col.key}
                direction={sortBy === col.key ? sortDirection : "asc"}
                onClick={() => handleSort(col.key)}
              >
                {col.label}
              </TableSortLabel>
            </TableCell>
          ))}
          <TableCell>Actions</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {products.map((p) => (
          <TableRow key={p.id}>
            <TableCell>{p.id}</TableCell>
            <TableCell>{p.name}</TableCell>
            <TableCell>NOK {p.price.toFixed(2)}</TableCell>
            <TableCell>{p.category}</TableCell>
            <TableCell>{p.stock}</TableCell>
            <TableCell>
              <Tooltip title="Edit">
                <IconButton onClick={() => onEdit(p)}>
                  <EditIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete">
                <IconButton color="error" onClick={() => onDelete(p.id)}>
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
