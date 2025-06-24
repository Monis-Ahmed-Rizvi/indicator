import axios from 'axios';

const API_BASE_URL = 'http://192.168.94.131:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const stockAPI = {
  searchStock: (query) => api.get(`/stocks/search/?q=${query}`),
  getStockData: (symbol) => api.get(`/stocks/${symbol}/data/`),
  getIndicators: () => api.get('/indicators/'),
  runAnalysis: (data) => api.post('/analysis/', data),
  getResults: (symbol) => api.get(`/results/${symbol}/`),
};

export default api;
