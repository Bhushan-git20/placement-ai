import React, { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { BookOpen, Clock, Award, TrendingUp, Play, CheckCircle } from "lucide-react";
import { toast } from "sonner";

const Assessments = () => {
  const { user } = useAuth();
  const [assessments, setAssessments] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data for now
  useEffect(() => {
    const mockAssessments = [
      {
        id: 1,
        title: "React.js Fundamentals",
        description: "Test your knowledge of React.js basics, components, and hooks",
        duration_minutes: 45,
        passing_score: 70,
        questions: 20,
        difficulty: "Intermediate",
        completed: true,
        score: 85
      },
      {
        id: 2,
        title: "JavaScript ES6+ Features",
        description: "Modern JavaScript features and best practices",
        duration_minutes: 30,
        passing_score: 75,
        questions: 15,
        difficulty: "Beginner",
        completed: false
      },
      {
        id: 3,
        title: "Node.js Backend Development",
        description: "Server-side JavaScript and API development",
        duration_minutes: 60,
        passing_score: 80,
        questions: 25,
        difficulty: "Advanced",
        completed: false
      },
      {
        id: 4,
        title: "Database Design & SQL",
        description: "Relational database concepts and SQL queries",
        duration_minutes: 50,
        passing_score: 70,
        questions: 18,
        difficulty: "Intermediate",
        completed: true,
        score: 92
      }
    ];
    
    setTimeout(() => {
      setAssessments(mockAssessments);
      setLoading(false);
    }, 1000);
  }, []);

  const getDifficultyColor = (difficulty) => {
    const colors = {
      "Beginner": "bg-green-100 text-green-800",
      "Intermediate": "bg-yellow-100 text-yellow-800",
      "Advanced": "bg-red-100 text-red-800"
    };
    return colors[difficulty] || "bg-gray-100 text-gray-800";
  };

  const getScoreColor = (score, passingScore) => {
    if (score >= passingScore + 10) return "text-green-600";
    if (score >= passingScore) return "text-blue-600";
    return "text-red-600";
  };

  const handleStartAssessment = (assessmentId) => {
    toast.info("Assessment functionality will be implemented");
  };

  const completedAssessments = assessments.filter(a => a.completed);
  const availableAssessments = assessments.filter(a => !a.completed);
  const averageScore = completedAssessments.length > 0 
    ? Math.round(completedAssessments.reduce((acc, a) => acc + a.score, 0) / completedAssessments.length)
    : 0;

  if (loading) {
    return (
      <Layout title="Assessments">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Assessments">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Skill Assessments</h1>
          <p className="text-gray-600">Test and improve your skills with our assessments</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {assessments.length}
              </div>
              <div className="text-sm text-gray-600">Total Assessments</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {completedAssessments.length}
              </div>
              <div className="text-sm text-gray-600">Completed</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-purple-600">
                {averageScore}%
              </div>
              <div className="text-sm text-gray-600">Average Score</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold text-orange-600">
                {completedAssessments.filter(a => a.score >= a.passing_score).length}
              </div>
              <div className="text-sm text-gray-600">Passed</div>
            </CardContent>
          </Card>
        </div>

        {/* Progress Overview */}
        {completedAssessments.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Your Progress
              </CardTitle>
              <CardDescription>
                Track your assessment performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Overall Completion</span>
                  <span className="text-sm text-gray-600">
                    {Math.round((completedAssessments.length / assessments.length) * 100)}%
                  </span>
                </div>
                <Progress 
                  value={(completedAssessments.length / assessments.length) * 100} 
                  className="w-full" 
                />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Available Assessments */}
        {availableAssessments.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Available Assessments</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {availableAssessments.map((assessment) => (
                <Card key={assessment.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            {assessment.title}
                          </h3>
                          <p className="text-gray-600 text-sm mb-3">
                            {assessment.description}
                          </p>
                        </div>
                        <Badge className={getDifficultyColor(assessment.difficulty)}>
                          {assessment.difficulty}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4" />
                          {assessment.duration_minutes} min
                        </div>
                        <div className="flex items-center gap-2">
                          <BookOpen className="h-4 w-4" />
                          {assessment.questions} questions
                        </div>
                        <div className="flex items-center gap-2">
                          <Award className="h-4 w-4" />
                          Pass: {assessment.passing_score}%
                        </div>
                      </div>

                      <Button 
                        onClick={() => handleStartAssessment(assessment.id)}
                        className="w-full"
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Start Assessment
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Completed Assessments */}
        {completedAssessments.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Completed Assessments</h2>
            <div className="space-y-4">
              {completedAssessments.map((assessment) => (
                <Card key={assessment.id}>
                  <CardContent className="p-6">
                    <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">
                              {assessment.title}
                            </h3>
                            <p className="text-gray-600 text-sm">
                              {assessment.description}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <CheckCircle className="h-5 w-5 text-green-600" />
                            <Badge className={getDifficultyColor(assessment.difficulty)}>
                              {assessment.difficulty}
                            </Badge>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm text-gray-600 mb-4">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            {assessment.duration_minutes} min
                          </div>
                          <div className="flex items-center gap-2">
                            <BookOpen className="h-4 w-4" />
                            {assessment.questions} questions
                          </div>
                          <div className="flex items-center gap-2">
                            <Award className="h-4 w-4" />
                            Pass: {assessment.passing_score}%
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`font-bold ${getScoreColor(assessment.score, assessment.passing_score)}`}>
                              Score: {assessment.score}%
                            </span>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <div className="flex justify-between items-center text-sm">
                            <span>Performance</span>
                            <span className={getScoreColor(assessment.score, assessment.passing_score)}>
                              {assessment.score >= assessment.passing_score ? "Passed" : "Failed"}
                            </span>
                          </div>
                          <Progress 
                            value={assessment.score} 
                            className="w-full" 
                          />
                        </div>
                      </div>

                      <div className="flex flex-col gap-2">
                        <Button variant="outline" size="sm">
                          View Results
                        </Button>
                        <Button variant="outline" size="sm">
                          Retake
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {assessments.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No assessments available
              </h3>
              <p className="text-gray-600">
                Check back later for new skill assessments.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default Assessments;