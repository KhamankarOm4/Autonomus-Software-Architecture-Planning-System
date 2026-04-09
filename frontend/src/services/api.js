import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeProject = async (mode, input) => {
  try {
    const response = await api.post('/api/analyze', { mode, input });
    return response.data;
  } catch (error) {
    console.error('API Error (analyzeProject):', error);
    throw error.response?.data || error.message;
  }
};

export const runGreenfieldAnalysis = async (requirements) => {
  try {
    const response = await api.post('/api/greenfield', { requirements });
    return response.data;
  } catch (error) {
    console.error('API Error (runGreenfieldAnalysis):', error);
    throw error.response?.data || error.message;
  }
};

export const runBrownfieldAnalysis = async (input) => {
  try {
    const response = await api.post('/api/brownfield', { input });
    return response.data;
  } catch (error) {
    console.error('API Error (runBrownfieldAnalysis):', error);
    throw error.response?.data || error.message;
  }
};

export default api;
