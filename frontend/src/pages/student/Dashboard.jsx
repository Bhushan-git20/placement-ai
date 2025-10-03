import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { 
  Briefcase, 
  FileText, 
  Brain, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertCircle,
  Target,
  Book,
  Trophy
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { api } from '../../store/authStore';
import useAuthStore from '../../store/authStore';
import { format } from 'date-fns';

const StudentDashboard = () => {
  const { user } = useAuthStore();
  const [studentData, setStudentData] = useState(null);
  const [applications, setApplications] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStudentData();
    fetchApplications();
    fetchAssessments();
  }, []);

  const fetchStudentData = async () => {
    try {
      const response = await api.get('/students/me');
      setStudentData(response.data);
    } catch (error) {
      console.error('Failed to fetch student data:', error);
    }
  };

  const fetchApplications = async () => {
    try {
      const response = await api.get('/applications/me');
      setApplications(response.data.slice(0, 5)); // Get last 5 applications
    } catch (error) {
      console.error('Failed to fetch applications:', error);
    }
  };

  const fetchAssessments = async () => {
    try {
      const response = await api.get('/assessments/me');
      setAssessments(response.data.slice(0, 3)); // Get last 3 assessments
    } catch (error) {
      console.error('Failed to fetch assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for charts
  const performanceData = [
    { month: 'Jan', score: 65 },
    { month: 'Feb', score: 70 },
    { month: 'Mar', score: 75 },
    { month: 'Apr', score: 78 },
    { month: 'May', score: 82 },
    { month: 'Jun', score: 85 },
  ];

  const skillRadarData = [
    { skill: 'Technical', A: studentData?.placement_score || 80 },
    { skill: 'Communication', A: 85 },
    { skill: 'Problem Solving', A: 90 },
    { skill: 'Leadership', A: 70 },
    { skill: 'Teamwork', A: 88 },
    { skill: 'Adaptability', A: 75 },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      applied: { variant: 'secondary', icon: Clock },
      shortlisted: { variant: 'default', icon: CheckCircle },
      interviewed: { variant: 'outline', icon: AlertCircle },
      hired: { variant: 'default', icon: Trophy },
      rejected: { variant: 'destructive', icon: AlertCircle },
    };

    const config = statusConfig[status] || statusConfig.applied;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Student Dashboard</h1>
          <p className="text-gray-600">
            Welcome back, {studentData?.user?.full_name}! Track your placement journey.
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">{format(new Date(), 'EEEE, MMMM do, yyyy')}</p>
          <Badge variant="outline" className="mt-1">
            {studentData?.department} - Year {studentData?.year}
          </Badge>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CGPA</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{studentData?.cgpa || 'N/A'}</div>
            <p className="text-xs text-muted-foreground">
              Current academic performance
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Applications</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{applications.length}</div>
            <p className="text-xs text-muted-foreground">
              Job applications submitted
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Assessments</CardTitle>
            <Book className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{assessments.length}</div>
            <p className="text-xs text-muted-foreground">
              Assessments completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Placement Score</CardTitle>
            <Trophy className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{studentData?.placement_score || 0}</div>
            <p className="text-xs text-muted-foreground">
              AI-calculated readiness
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Performance Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Trend</CardTitle>
            <CardDescription>Your assessment scores over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#8884d8" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Skill Radar */}
        <Card>
          <CardHeader>
            <CardTitle>Skill Assessment</CardTitle>
            <CardDescription>Your competency across different areas</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={skillRadarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="skill" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Skills"
                  dataKey="A"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions and Recent Activity */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Get started with these actions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link to="/profile">
              <Button variant="outline" className="w-full justify-start">
                <FileText className="mr-2 h-4 w-4" />
                Update Profile & Resume
              </Button>
            </Link>
            <Link to="/jobs">
              <Button variant="outline" className="w-full justify-start">
                <Briefcase className="mr-2 h-4 w-4" />
                Browse Job Opportunities
              </Button>
            </Link>
            <Link to="/assessments">
              <Button variant="outline" className="w-full justify-start">
                <Book className="mr-2 h-4 w-4" />
                Take Assessment Tests
              </Button>
            </Link>
            <Link to="/ai-coach">
              <Button className="w-full justify-start">
                <Brain className="mr-2 h-4 w-4" />
                Chat with AI Career Coach
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Applications */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Applications</CardTitle>
            <CardDescription>Your latest job applications</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {applications.length > 0 ? (
              applications.map((application, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Job Application #{application.app_id.slice(-8)}</p>
                    <p className="text-sm text-muted-foreground">
                      Applied on {format(new Date(application.applied_date), 'MMM dd')}
                    </p>
                  </div>
                  {getStatusBadge(application.status)}
                </div>
              ))
            ) : (
              <div className="text-center py-6">
                <Briefcase className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-500">No applications yet</p>
                <Link to="/jobs">
                  <Button className="mt-2" size="sm">
                    Browse Jobs
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Assessments */}
      {assessments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Assessments</CardTitle>
            <CardDescription>Your latest assessment performances</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {assessments.map((assessment, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">{assessment.category}</h4>
                    <p className="text-sm text-muted-foreground">
                      {assessment.type.replace('_', ' ')} • {format(new Date(assessment.assessment_date), 'MMM dd, yyyy')}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold">{assessment.score}</p>
                    <p className="text-sm text-muted-foreground">
                      {assessment.correct_answers}/{assessment.total_questions}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default StudentDashboard;