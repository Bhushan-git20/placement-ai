import React, { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, Clock, Video, MapPin, User, Building, Phone } from "lucide-react";
import { toast } from "sonner";

const Interviews = () => {
  const { user } = useAuth();
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data for now
  useEffect(() => {
    const mockInterviews = [
      {
        id: 1,
        job: {
          title: "Frontend Developer",
          company: "StartupXYZ"
        },
        scheduled_at: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
        interview_type: "online",
        location_or_link: "https://zoom.us/j/123456789",
        status: "scheduled",
        notes: "Technical interview with the development team"
      },
      {
        id: 2,
        job: {
          title: "Software Engineer",
          company: "Tech Corp"
        },
        scheduled_at: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
        interview_type: "offline",
        location_or_link: "123 Tech Street, San Francisco, CA 94105",
        status: "scheduled",
        notes: "Final round interview with the CTO"
      },
      {
        id: 3,
        job: {
          title: "Full Stack Developer",
          company: "Innovation Labs"
        },
        scheduled_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        interview_type: "phone",
        location_or_link: "+1-555-0123",
        status: "completed",
        notes: "HR screening call"
      }
    ];
    
    setTimeout(() => {
      setInterviews(mockInterviews);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    const colors = {
      scheduled: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800"
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case "online":
        return <Video className="h-4 w-4" />;
      case "offline":
        return <MapPin className="h-4 w-4" />;
      case "phone":
        return <Phone className="h-4 w-4" />;
      default:
        return <Calendar className="h-4 w-4" />;
    }
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  };

  const formatType = (type) => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  const isUpcoming = (dateString) => {
    return new Date(dateString) > new Date();
  };

  const upcomingInterviews = interviews.filter(interview => 
    isUpcoming(interview.scheduled_at) && interview.status === 'scheduled'
  );
  
  const pastInterviews = interviews.filter(interview => 
    !isUpcoming(interview.scheduled_at) || interview.status !== 'scheduled'
  );

  if (loading) {
    return (
      <Layout title="Interviews">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Interviews">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Interviews</h1>
          <p className="text-gray-600">Manage your interview schedule</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {upcomingInterviews.length}
              </div>
              <div className="text-sm text-gray-600">Upcoming Interviews</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {interviews.filter(i => i.status === 'completed').length}
              </div>
              <div className="text-sm text-gray-600">Completed</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-purple-600">
                {interviews.length}
              </div>
              <div className="text-sm text-gray-600">Total Interviews</div>
            </CardContent>
          </Card>
        </div>

        {/* Upcoming Interviews */}
        {upcomingInterviews.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Upcoming Interviews</h2>
            <div className="space-y-4">
              {upcomingInterviews.map((interview) => {
                const dateTime = formatDateTime(interview.scheduled_at);
                return (
                  <Card key={interview.id} className="border-l-4 border-l-blue-500">
                    <CardContent className="p-6">
                      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900">
                                {interview.job.title}
                              </h3>
                              <div className="flex items-center gap-1 text-gray-600 mt-1">
                                <Building className="h-4 w-4" />
                                {interview.job.company}
                              </div>
                            </div>
                            <Badge className={getStatusColor(interview.status)}>
                              {interview.status}
                            </Badge>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4" />
                              {dateTime.date} at {dateTime.time}
                            </div>
                            <div className="flex items-center gap-2">
                              {getTypeIcon(interview.interview_type)}
                              {formatType(interview.interview_type)}
                            </div>
                          </div>

                          {interview.location_or_link && (
                            <div className="mb-3 text-sm">
                              <span className="font-medium text-gray-700">
                                {interview.interview_type === 'online' ? 'Meeting Link:' : 
                                 interview.interview_type === 'phone' ? 'Phone:' : 'Location:'}
                              </span>
                              <div className="text-blue-600 mt-1">
                                {interview.interview_type === 'online' ? (
                                  <a href={interview.location_or_link} target="_blank" rel="noopener noreferrer" 
                                     className="hover:underline">
                                    {interview.location_or_link}
                                  </a>
                                ) : (
                                  interview.location_or_link
                                )}
                              </div>
                            </div>
                          )}

                          {interview.notes && (
                            <p className="text-gray-700 text-sm">{interview.notes}</p>
                          )}
                        </div>

                        <div className="flex flex-col gap-2">
                          {interview.interview_type === 'online' && (
                            <Button size="sm">
                              Join Meeting
                            </Button>
                          )}
                          <Button variant="outline" size="sm">
                            Reschedule
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* Past Interviews */}
        {pastInterviews.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Past Interviews</h2>
            <div className="space-y-4">
              {pastInterviews.map((interview) => {
                const dateTime = formatDateTime(interview.scheduled_at);
                return (
                  <Card key={interview.id} className="opacity-75">
                    <CardContent className="p-6">
                      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900">
                                {interview.job.title}
                              </h3>
                              <div className="flex items-center gap-1 text-gray-600 mt-1">
                                <Building className="h-4 w-4" />
                                {interview.job.company}
                              </div>
                            </div>
                            <Badge className={getStatusColor(interview.status)}>
                              {interview.status}
                            </Badge>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4" />
                              {dateTime.date} at {dateTime.time}
                            </div>
                            <div className="flex items-center gap-2">
                              {getTypeIcon(interview.interview_type)}
                              {formatType(interview.interview_type)}
                            </div>
                          </div>

                          {interview.notes && (
                            <p className="text-gray-700 text-sm">{interview.notes}</p>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* Empty State */}
        {interviews.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No interviews scheduled
              </h3>
              <p className="text-gray-600">
                Your interview schedule will appear here once you have scheduled interviews.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default Interviews;