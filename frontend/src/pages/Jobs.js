import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Briefcase, MapPin, Clock, Search, Filter } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const Jobs = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filteredJobs, setFilteredJobs] = useState([]);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await axios.get(`${API}/jobs`);
        setJobs(response.data);
        setFilteredJobs(response.data);
      } catch (error) {
        console.error("Error fetching jobs:", error);
        toast.error("Failed to load jobs");
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [API]);

  useEffect(() => {
    let filtered = jobs;

    if (searchTerm) {
      filtered = filtered.filter(
        (job) =>
          job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          job.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterType) {
      filtered = filtered.filter((job) => job.job_type === filterType);
    }

    setFilteredJobs(filtered);
  }, [jobs, searchTerm, filterType]);

  const getJobTypeColor = (type) => {
    const colors = {
      "full-time": "bg-blue-100 text-blue-800",
      "part-time": "bg-green-100 text-green-800",
      internship: "bg-purple-100 text-purple-800",
      contract: "bg-orange-100 text-orange-800",
    };
    return colors[type] || "bg-gray-100 text-gray-800";
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <Layout title="Jobs">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Jobs">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Job Opportunities</h1>
            <p className="text-gray-600">Discover your next career opportunity</p>
          </div>
          {user?.role === "recruiter" && (
            <Button asChild>
              <Link to="/recruiter/post-job">Post New Job</Link>
            </Button>
          )}
        </div>

        {/* Search and Filters */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search jobs by title, company, or keywords..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="Job Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Types</SelectItem>
                  <SelectItem value="full-time">Full Time</SelectItem>
                  <SelectItem value="part-time">Part Time</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="text-sm text-gray-600 mb-4">
          {filteredJobs.length} job{filteredJobs.length !== 1 ? "s" : ""} found
        </div>

        {/* Job Listings */}
        <div className="space-y-4">
          {filteredJobs.length > 0 ? (
            filteredJobs.map((job) => (
              <Card key={job.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            <Link
                              to={`/jobs/${job.id}`}
                              className="hover:text-blue-600"
                            >
                              {job.title}
                            </Link>
                          </h3>
                          <p className="text-gray-600">Company Name</p>
                        </div>
                        <Badge className={getJobTypeColor(job.job_type)}>
                          {job.job_type || "Full Time"}
                        </Badge>
                      </div>

                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                        {job.location && (
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            {job.location}
                          </div>
                        )}
                        {job.salary_range && (
                          <div className="flex items-center gap-1">
                            <span>💰 {job.salary_range}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          Posted {formatDate(job.created_at)}
                        </div>
                      </div>

                      <p className="text-gray-700 mb-4 line-clamp-2">
                        {job.description}
                      </p>

                      {job.requirements && job.requirements.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-4">
                          {job.requirements.slice(0, 3).map((req, index) => (
                            <Badge key={index} variant="outline">
                              {req}
                            </Badge>
                          ))}
                          {job.requirements.length > 3 && (
                            <Badge variant="outline">
                              +{job.requirements.length - 3} more
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col gap-2">
                      <Button asChild>
                        <Link to={`/jobs/${job.id}`}>View Details</Link>
                      </Button>
                      {user?.role === "student" && (
                        <Button variant="outline">Quick Apply</Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No jobs found
                </h3>
                <p className="text-gray-600">
                  Try adjusting your search criteria or check back later for new
                  opportunities.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Jobs;