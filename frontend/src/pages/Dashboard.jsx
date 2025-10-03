import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { 
  Users, 
  Building2, 
  TrendingUp, 
  Briefcase,
  GraduationCap,
  Target,
  Award,
  Calendar
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { api } from '../store/authStore';
import useAuthStore from '../store/authStore';
import { format } from 'date-fns';

const Dashboard = () => {
  const { user } = useAuthStore();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for charts
  const placementTrendData = [
    { month: 'Jan', placements: 45, applications: 120 },
    { month: 'Feb', placements: 52, applications: 140 },
    { month: 'Mar', placements: 61, applications: 160 },
    { month: 'Apr', placements: 58, applications: 150 },
    { month: 'May', placements: 67, applications: 180 },
    { month: 'Jun', placements: 74, applications: 200 },
  ];

  const skillTrendData = [
    { skill: 'Python', demand: 85 },
    { skill: 'React', demand: 80 },
    { skill: 'Node.js', demand: 75 },
    { skill: 'AWS', demand: 70 },
    { skill: 'Docker', demand: 65 },
  ];

  const departmentData = [
    { name: 'CSE', value: 40, color: '#0088FE' },
    { name: 'ECE', value: 25, color: '#00C49F' },
    { name: 'ME', value: 20, color: '#FFBB28' },
    { name: 'EEE', value: 15, color: '#FF8042' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  const stats = dashboardData?.placement_stats || {};

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.full_name}!</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">{format(new Date(), 'EEEE, MMMM do, yyyy')}</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_students || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active students in system
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Placements</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_placed || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats.placement_percentage?.toFixed(1)}% placement rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Package</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹{stats.average_package?.toFixed(1)}L</div>
            <p className="text-xs text-muted-foreground">
              Average salary package
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Companies</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.top_recruiters?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active recruiting companies
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        {/* Placement Trends */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Placement Trends</CardTitle>
            <CardDescription>Monthly placement vs applications</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={placementTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="placements" stroke="#8884d8" strokeWidth={2} />
                <Line type="monotone" dataKey="applications" stroke="#82ca9d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Department Distribution */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Department Distribution</CardTitle>
            <CardDescription>Student placement by department</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={departmentData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {departmentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Additional Content */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Top Skills in Demand */}
        <Card>
          <CardHeader>
            <CardTitle>Top Skills in Demand</CardTitle>
            <CardDescription>Skills trending in the job market</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {dashboardData?.trending_skills?.map((skill, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{skill.skill_name}</p>
                  <p className="text-sm text-muted-foreground">
                    {skill.growth_rate}% growth
                  </p>
                </div>
                <Badge variant={skill.trend === 'rising' ? 'default' : 'secondary'}>
                  {skill.trend}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Recent Placements */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Placements</CardTitle>
            <CardDescription>Latest student placements</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {dashboardData?.recent_placements?.map((placement, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{placement.student_name}</p>
                  <p className="text-sm text-muted-foreground">
                    {placement.company} - {placement.role}
                  </p>
                </div>
                <Badge variant="outline">
                  ₹{placement.package}L
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;