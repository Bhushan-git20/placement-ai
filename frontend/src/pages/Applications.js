import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Calendar, Clock, Eye, MapPin, Building } from "lucide-react";
import { toast } from "sonner";

const Applications = () => {
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data for now
  useEffect(() => {
    const mockApplications = [
      {
        id: 1,
        job: {
          id: "job1",
          title: "Software Engineer",
          company: "Tech Corp",
          location: "San Francisco, CA"
        },
        status: "submitted",
        applied_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        cover_letter: "I am very interested in this position..."
      },
      {
        id: 2,
        job: {
          id: "job2",
          title: "Frontend Developer",
          company: "StartupXYZ",
          location: "New York, NY"
        },
        status: "interview_scheduled",
        applied_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        cover_letter: "I would love to contribute to your team..."
      },
      {
        id: 3,
        job: {
          id: "job3",
          title: "Full Stack Developer",
          company: "Innovation Labs",
          location: "Remote"
        },
        status: "reviewed",
        applied_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        cover_letter: "My experience in both frontend and backend..."
      }
    ];
    
    setTimeout(() => {
      setApplications(mockApplications);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    const colors = {
      submitted: "bg-blue-100 text-blue-800",
      reviewed: "bg-yellow-100 text-yellow-800",
      shortlisted: "bg-purple-100 text-purple-800",
      interview_scheduled: "bg-green-100 text-green-800",
      rejected: "bg-red-100 text-red-800",
      selected: "bg-emerald-100 text-emerald-800"
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "submitted":
        return <Clock className="h-4 w-4" />;
      case "interview_scheduled":
        return <Calendar className="h-4 w-4" />;
      case "reviewed":
        return <Eye className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatStatus = (status) => {
    return status.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <Layout title="My Applications">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="My Applications">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">My Applications</h1>
            <p className="text-gray-600">Track your job application status</p>
          </div>
          <Button asChild>
            <Link to="/jobs">Browse More Jobs</Link>
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {applications.length}
              </div>
              <div className="text-sm text-gray-600">Total Applications</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {applications.filter(app => app.status === 'interview_scheduled').length}
              </div>
              <div className="text-sm text-gray-600">Interviews Scheduled</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-yellow-600">
                {applications.filter(app => app.status === 'reviewed' || app.status === 'shortlisted').length}
              </div>
              <div className="text-sm text-gray-600">Under Review</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-purple-600">
                {applications.filter(app => app.status === 'selected').length}
              </div>
              <div className="text-sm text-gray-600">Selected</div>
            </CardContent>
          </Card>
        </div>

        {/* Applications List */}
        <div className="space-y-4">
          {applications.length > 0 ? (
            applications.map((application) => (
              <Card key={application.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {application.job.title}
                          </h3>
                          <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                            <div className="flex items-center gap-1">
                              <Building className="h-4 w-4" />
                              {application.job.company}
                            </div>
                            <div className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              {application.job.location}
                            </div>
                          </div>
                        </div>
                        <Badge className={`${getStatusColor(application.status)} gap-1`}>
                          {getStatusIcon(application.status)}
                          {formatStatus(application.status)}
                        </Badge>
                      </div>

                      <p className="text-gray-700 text-sm mb-3 line-clamp-2">
                        {application.cover_letter}
                      </p>

                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          Applied {formatDate(application.applied_at)}
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <Button asChild size="sm">
                        <Link to={`/jobs/${application.job.id}`}>View Job</Link>
                      </Button>
                      
                      {application.status === 'interview_scheduled' && (
                        <Button asChild variant="outline" size="sm">
                          <Link to="/interviews">View Interview</Link>
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No applications yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Start applying for jobs to see your applications here.
                </p>
                <Button asChild>
                  <Link to="/jobs">Browse Jobs</Link>
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Applications;