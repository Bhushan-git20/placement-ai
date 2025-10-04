import React from "react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Briefcase, Users, Calendar, TrendingUp } from "lucide-react";

const RecruiterDashboard = () => {
  return (
    <Layout title="Recruiter Dashboard">
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg p-6 text-white">
          <h1 className="text-2xl font-bold mb-2">Recruiter Dashboard</h1>
          <p className="text-green-100">Manage your job postings and find the best candidates.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Briefcase className="h-5 w-5 mr-2" />
                Active Jobs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">5</p>
              <p className="text-sm text-gray-600">Currently accepting applications</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Applications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">23</p>
              <p className="text-sm text-gray-600">Pending review</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="h-5 w-5 mr-2" />
                Interviews
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">8</p>
              <p className="text-sm text-gray-600">Scheduled this week</p>
            </CardContent>
          </Card>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common recruiting tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button className="w-full">Post New Job</Button>
            <Button variant="outline" className="w-full">Review Applications</Button>
            <Button variant="outline" className="w-full">Schedule Interviews</Button>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default RecruiterDashboard;