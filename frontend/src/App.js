import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import StudentsBasic from "./pages/StudentsBasic";
import "./App.css";

const queryClient = new QueryClient();

// Simple Landing Page Component
const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Placement Management System
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
            Comprehensive platform for managing student placements, job opportunities, and career development
          </p>
          <div className="flex justify-center space-x-4">
            <a
              href="/students"
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300"
            >
              Manage Students
            </a>
            <a
              href="/dashboard"
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-6 rounded-lg transition duration-300"
            >
              View Dashboard
            </a>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">Student Management</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Track student profiles, skills, and placement readiness
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">Job Matching</h3>
            <p className="text-gray-600 dark:text-gray-400">
              AI-powered job recommendations and skill gap analysis
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">Analytics</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Comprehensive insights into placement trends and performance
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Simple Dashboard Component
const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Dashboard</h1>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">Total Students</h3>
            <p className="text-3xl font-bold text-blue-600">-</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">Active Jobs</h3>
            <p className="text-3xl font-bold text-green-600">-</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">Applications</h3>
            <p className="text-3xl font-bold text-yellow-600">-</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">Placements</h3>
            <p className="text-3xl font-bold text-purple-600">-</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/students" element={<StudentsBasic />} />
      </Routes>
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;