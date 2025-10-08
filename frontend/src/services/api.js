const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
};

export const api = {
  students: {
    getAll: () => fetch(`${API_URL}/students`).then(handleResponse),
    getById: (id) => fetch(`${API_URL}/students/${id}`).then(handleResponse),
    create: (data) => fetch(`${API_URL}/students`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    update: (id, data) => fetch(`${API_URL}/students/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    uploadResume: (id, resumeText) => {
      const formData = new FormData();
      formData.append('resume_text', resumeText);
      return fetch(`${API_URL}/students/${id}/resume`, {
        method: 'POST',
        body: formData
      }).then(handleResponse);
    },
    delete: (id) => fetch(`${API_URL}/students/${id}`, {
      method: 'DELETE'
    }).then(handleResponse)
  },
  jobs: {
    getAll: (activeOnly = true) => fetch(`${API_URL}/jobs?active_only=${activeOnly}`).then(handleResponse),
    getById: (id) => fetch(`${API_URL}/jobs/${id}`).then(handleResponse),
    create: (data) => fetch(`${API_URL}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    update: (id, data) => fetch(`${API_URL}/jobs/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    delete: (id) => fetch(`${API_URL}/jobs/${id}`, {
      method: 'DELETE'
    }).then(handleResponse)
  },
  applications: {
    create: (data) => fetch(`${API_URL}/applications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    getByStudent: (studentId) => fetch(`${API_URL}/applications/student/${studentId}`).then(handleResponse),
    getAll: () => fetch(`${API_URL}/applications`).then(handleResponse),
    updateStatus: (appId, status) => fetch(`${API_URL}/applications/${appId}/status?status=${status}`, {
      method: 'PUT'
    }).then(handleResponse)
  },
  tests: {
    getAll: () => fetch(`${API_URL}/tests`).then(handleResponse),
    getById: (id) => fetch(`${API_URL}/tests/${id}`).then(handleResponse),
    create: (data) => fetch(`${API_URL}/tests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    submit: (data) => fetch(`${API_URL}/tests/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    getStudentResults: (studentId) => fetch(`${API_URL}/test-results/student/${studentId}`).then(handleResponse)
  },
  interviewQuestions: {
    seed: () => fetch(`${API_URL}/interview-questions/seed`, {
      method: 'POST'
    }).then(handleResponse),
    create: (data) => fetch(`${API_URL}/interview-questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    getAll: (category, difficulty) => {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (difficulty) params.append('difficulty', difficulty);
      return fetch(`${API_URL}/interview-questions?${params.toString()}`).then(handleResponse);
    }
  },
  ai: {
    generateJobMatch: (studentId) => fetch(`${API_URL}/ai/job-match/${studentId}`, {
      method: 'POST'
    }).then(handleResponse),
    getJobMatches: (studentId) => fetch(`${API_URL}/ai/job-match/${studentId}`).then(handleResponse),
    generateSkillGap: (studentId) => fetch(`${API_URL}/ai/skill-gap/${studentId}`, {
      method: 'POST'
    }).then(handleResponse),
    getSkillGap: (studentId) => fetch(`${API_URL}/ai/skill-gap/${studentId}`).then(handleResponse),
    getRecommendations: (studentId, limit = 5) => fetch(`${API_URL}/ai/job-recommendations/${studentId}?limit=${limit}`, {
      method: 'POST'
    }).then(handleResponse)
  },
  analytics: {
    getStudentAnalytics: (studentId) => fetch(`${API_URL}/analytics/student/${studentId}`).then(handleResponse),
    getOverview: () => fetch(`${API_URL}/analytics/overview`).then(handleResponse)
  }
};