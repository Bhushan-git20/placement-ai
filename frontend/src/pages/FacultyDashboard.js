import React from "react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users, BookOpen, FileText, BarChart } from "lucide-react";

const FacultyDashboard = () => {
  return (
    <Layout title="Faculty Dashboard">
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-purple-600 to-violet-600 rounded-lg p-6 text-white">
          <h1 className="text-2xl font-bold mb-2">Faculty Dashboard</h1>
          <p className="text-purple-100">Manage student progress and create assessments.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Students
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">45</p>
              <p className="text-sm text-gray-600">Under supervision</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BookOpen className="h-5 w-5 mr-2" />
                Assessments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">12</p>
              <p className="text-sm text-gray-600">Active assessments</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart className="h-5 w-5 mr-2" />
                Completion Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">87%</p>
              <p className="text-sm text-gray-600">Average pass rate</p>
            </CardContent>
          </Card>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Faculty Actions</CardTitle>
            <CardDescription>Manage students and assessments</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button className="w-full">Create Assessment</Button>
            <Button variant="outline" className="w-full">View Student Progress</Button>
            <Button variant="outline" className="w-full">Update Student Data</Button>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default FacultyDashboard;