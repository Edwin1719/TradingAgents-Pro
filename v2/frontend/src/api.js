
import axios from 'axios';

// In development (npm start), process.env.NODE_ENV is 'development'
// In production (docker), it will be 'production'
const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
