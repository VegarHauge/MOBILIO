import React from "react";
import AdminDashboard from "../components/admin/AdminDashboard";
import MainLayout from "../layouts/MainLayout";

export default function AdminPage() {
  return (
    <MainLayout navColor="dark">
      <AdminDashboard />
    </MainLayout>
  );
}
