import React, { useEffect } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const Dashboard = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Redirect to role-specific dashboard
  const dashboardRoutes = {
    student: "/student",
    recruiter: "/recruiter",
    faculty: "/faculty",
    admin: "/admin"
  };

  const redirectPath = dashboardRoutes[user.role] || "/student";
  
  return <Navigate to={redirectPath} replace />;
};

export default Dashboard;