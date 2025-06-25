import axios from 'axios';

// Use relative path so it works through the domain
const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Add debugging
api.interceptors.request.use(request => {
  console.log('Making API request to:', request.baseURL + request.url);
  return request;
});

api.interceptors.response.use(
  response => {
    console.log('API response success:', response.status);
    return response;
  },
  error => {
    console.error('API error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export const stockAPI = {
  searchStock: (query) => api.get(`/stocks/search/?q=${query}`),
  getStockData: (symbol) => api.get(`/stocks/${symbol}/data/`),
  getIndicators: () => api.get('/indicators/'),
  runAnalysis: (data) => api.post('/analysis/', data),
  getResults: (symbol) => api.get(`/results/${symbol}/`),
};

export default api;
