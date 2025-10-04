import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { MapPin, Clock, DollarSign, Building, Users, ArrowLeft, Send } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const JobDetails = () => {
  const { jobId } = useParams();
  const { user } = useAuth();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [coverLetter, setCoverLetter] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const response = await axios.get(`${API}/jobs/${jobId}`);
        setJob(response.data);
      } catch (error) {
        console.error("Error fetching job:", error);
        toast.error("Failed to load job details");
      } finally {
        setLoading(false);
      }
    };

    fetchJob();
  }, [API, jobId]);

  const handleApply = async () => {
    setApplying(true);
    try {
      await axios.post(`${API}/applications`, {
        job_id: jobId,
        cover_letter: coverLetter,
      });
      toast.success("Application submitted successfully!");
      setDialogOpen(false);
      setCoverLetter("");
    } catch (error) {
      console.error("Error applying for job:", error);
      toast.error(error.response?.data?.detail || "Failed to submit application");
    } finally {
      setApplying(false);
    }
  };

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
      <Layout title="Job Details">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  if (!job) {
    return (
      <Layout title="Job Not Found">
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Job Not Found</h1>
          <p className="text-gray-600 mb-6">The job you're looking for doesn't exist or has been removed.</p>
          <Button asChild>
            <Link to="/jobs">Back to Jobs</Link>
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={job.title}>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Back Button */}
        <Button variant="ghost" asChild>
          <Link to="/jobs">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Jobs
          </Link>
        </Button>

        {/* Job Header */}
        <Card>
          <CardContent className="p-8">
            <div className="flex flex-col lg:flex-row justify-between items-start gap-6">
              <div className="flex-1">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
                    <p className="text-xl text-gray-600">Company Name</p>
                  </div>
                  <Badge className={getJobTypeColor(job.job_type)}>
                    {job.job_type || "Full Time"}
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                  {job.location && (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      {job.location}
                    </div>
                  )}
                  {job.salary_range && (
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4" />
                      {job.salary_range}
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    Posted {formatDate(job.created_at)}
                  </div>
                  {job.application_deadline && (
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      Apply by {formatDate(job.application_deadline)}
                    </div>
                  )}
                </div>
              </div>

              {user?.role === "student" && (
                <div className="w-full lg:w-auto">
                  <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                    <DialogTrigger asChild>
                      <Button size="lg" className="w-full lg:w-auto">
                        <Send className="h-4 w-4 mr-2" />
                        Apply Now
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-md">
                      <DialogHeader>
                        <DialogTitle>Apply for {job.title}</DialogTitle>
                        <DialogDescription>
                          Submit your application with a cover letter.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="coverLetter">Cover Letter</Label>
                          <Textarea
                            id="coverLetter"
                            placeholder="Write a brief cover letter explaining why you're interested in this position..."
                            value={coverLetter}
                            onChange={(e) => setCoverLetter(e.target.value)}
                            rows={4}
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button
                          variant="outline"
                          onClick={() => setDialogOpen(false)}
                        >
                          Cancel
                        </Button>
                        <Button onClick={handleApply} disabled={applying}>
                          {applying ? "Submitting..." : "Submit Application"}
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Job Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <Card>
              <CardHeader>
                <CardTitle>Job Description</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{job.description}</p>
                </div>
              </CardContent>
            </Card>

            {/* Requirements */}
            {job.requirements && job.requirements.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Requirements</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {job.requirements.map((req, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-blue-600 mt-1">•</span>
                        <span className="text-gray-700">{req}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Job Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Job Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Job Type</span>
                  <span className="font-medium">{job.job_type || "Full Time"}</span>
                </div>
                <Separator />
                {job.location && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Location</span>
                      <span className="font-medium">{job.location}</span>
                    </div>
                    <Separator />
                  </>
                )}
                {job.salary_range && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Salary</span>
                      <span className="font-medium">{job.salary_range}</span>
                    </div>
                    <Separator />
                  </>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">Posted</span>
                  <span className="font-medium">{formatDate(job.created_at)}</span>
                </div>
              </CardContent>
            </Card>

            {/* Company Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="h-5 w-5" />
                  About the Company
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">
                  Company information will be displayed here once company profiles are integrated.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default JobDetails;