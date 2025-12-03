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


export default function OrderTable({
    orders, 
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
                { key: "customer_id", label: "Name" },
                { key: "total_amount", label: "Price" },
                { key: "created_at", label: "Category" },
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
            {orders.map((o) => (
            <TableRow key={o.id}>
                <TableCell>{o.id}</TableCell>
                <TableCell>{o.customer_id}</TableCell>
                <TableCell>{o.total_amount.toFixed(2)} €</TableCell>
                <TableCell>{o.created_at}</TableCell>
                <TableCell>
                <Tooltip title="Edit">
                    <IconButton onClick={() => onEdit(o)}>
                    <EditIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                    <IconButton color="error" onClick={() => onDelete(o.id)}>
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