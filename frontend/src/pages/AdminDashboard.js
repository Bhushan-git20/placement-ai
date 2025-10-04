import React from "react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users, Shield, Settings, Activity } from "lucide-react";

const AdminDashboard = () => {
  return (
    <Layout title="Admin Dashboard">
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-red-600 to-rose-600 rounded-lg p-6 text-white">
          <h1 className="text-2xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-red-100">System administration and user management.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Total Users
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">156</p>
              <p className="text-sm text-gray-600">Active users</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="h-5 w-5 mr-2" />
                Students
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">120</p>
              <p className="text-sm text-gray-600">Registered students</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Recruiters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">25</p>
              <p className="text-sm text-gray-600">Active recruiters</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2" />
                System Health
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-green-600">99%</p>
              <p className="text-sm text-gray-600">Uptime</p>
            </CardContent>
          </Card>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Admin Actions</CardTitle>
            <CardDescription>System management and configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button className="w-full">Manage Users</Button>
            <Button variant="outline" className="w-full">System Settings</Button>
            <Button variant="outline" className="w-full">View Reports</Button>
            <Button variant="outline" className="w-full">Backup Data</Button>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default AdminDashboard;