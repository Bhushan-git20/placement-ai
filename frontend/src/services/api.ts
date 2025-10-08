const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
};

export const api = {
  students: {
    getAll: () => fetch(`${API_URL}/students`).then(handleResponse),
    getById: (id: string) => fetch(`${API_URL}/students/${id}`).then(handleResponse),
    create: (data: any) => fetch(`${API_URL}/students`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    update: (id: string, data: any) => fetch(`${API_URL}/students/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    uploadResume: (id: string, resumeText: string) => {
      const formData = new FormData();
      formData.append('resume_text', resumeText);
      return fetch(`${API_URL}/students/${id}/resume`, {
        method: 'POST',
        body: formData
      }).then(handleResponse);
    },
    delete: (id: string) => fetch(`${API_URL}/students/${id}`, {
      method: 'DELETE'
    }).then(handleResponse)
  },
  jobs: {
    getAll: (activeOnly = true) => fetch(`${API_URL}/jobs?active_only=${activeOnly}`).then(handleResponse),
    getById: (id: string) => fetch(`${API_URL}/jobs/${id}`).then(handleResponse),
    create: (data: any) => fetch(`${API_URL}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    update: (id: string, data: any) => fetch(`${API_URL}/jobs/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    delete: (id: string) => fetch(`${API_URL}/jobs/${id}`, {
      method: 'DELETE'
    }).then(handleResponse)
  },
  applications: {
    create: (data: any) => fetch(`${API_URL}/applications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    getByStudent: (studentId: string) => fetch(`${API_URL}/applications/student/${studentId}`).then(handleResponse),
    getAll: () => fetch(`${API_URL}/applications`).then(handleResponse),
    updateStatus: (appId: string, status: string) => fetch(`${API_URL}/applications/${appId}/status?status=${status}`, {
      method: 'PUT'
    }).then(handleResponse)
  },
  tests: {
    getAll: () => fetch(`${API_URL}/tests`).then(handleResponse),
    getById: (id: string) => fetch(`${API_URL}/tests/${id}`).then(handleResponse),
    create: (data: any) => fetch(`${API_URL}/tests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    submit: (data: any) => fetch(`${API_URL}/tests/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    getStudentResults: (studentId: string) => fetch(`${API_URL}/test-results/student/${studentId}`).then(handleResponse)
  },
  interviewQuestions: {
    seed: () => fetch(`${API_URL}/interview-questions/seed`, {
      method: 'POST'
    }).then(handleResponse),
    create: (data: any) => fetch(`${API_URL}/interview-questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(handleResponse),
    getAll: (category?: string, difficulty?: string) => {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (difficulty) params.append('difficulty', difficulty);
      return fetch(`${API_URL}/interview-questions?${params.toString()}`).then(handleResponse);
    }
  },
  ai: {
    generateJobMatch: (studentId: string) => fetch(`${API_URL}/ai/job-match/${studentId}`, {
      method: 'POST'
    }).then(handleResponse),
    getJobMatches: (studentId: string) => fetch(`${API_URL}/ai/job-match/${studentId}`).then(handleResponse),
    generateSkillGap: (studentId: string) => fetch(`${API_URL}/ai/skill-gap/${studentId}`, {
      method: 'POST'
    }).then(handleResponse),
    getSkillGap: (studentId: string) => fetch(`${API_URL}/ai/skill-gap/${studentId}`).then(handleResponse),
    getRecommendations: (studentId: string, limit = 5) => fetch(`${API_URL}/ai/job-recommendations/${studentId}?limit=${limit}`, {
      method: 'POST'
    }).then(handleResponse)
  },
  analytics: {
    getStudentAnalytics: (studentId: string) => fetch(`${API_URL}/analytics/student/${studentId}`).then(handleResponse),
    getOverview: () => fetch(`${API_URL}/analytics/overview`).then(handleResponse)
  }
};