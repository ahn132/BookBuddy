import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const setAuthToken = (token: string) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const register = async (email: string, username: string, password: string) => {
  const response = await api.post('/register', { email, username, password });
  return response.data;
};

export const login = async (username: string, password: string) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  const response = await api.post('/token', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/users/me');
  return response.data;
};

// Admin endpoints
export const getAllUsers = async () => {
  const response = await api.get('/admin/users');
  return response.data;
};

export const toggleUserAdmin = async (userId: number) => {
  const response = await api.put(`/admin/users/${userId}/toggle-admin`);
  return response.data;
}; 