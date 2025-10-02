import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
  connectGoogle: () => api.get('/auth/google/authorize'),
};

// Locations
export const locationsAPI = {
  getAll: () => api.get('/locations/'),
  getById: (id: number) => api.get(`/locations/${id}`),
  create: (data: any) => api.post('/locations/', data),
  update: (id: number, data: any) => api.put(`/locations/${id}`, data),
  delete: (id: number) => api.delete(`/locations/${id}`),
  sync: () => api.post('/locations/sync'),
};

// Posts
export const postsAPI = {
  getAll: (locationId?: number) =>
    api.get('/posts/', { params: { location_id: locationId } }),
  getById: (id: number) => api.get(`/posts/${id}`),
  create: (data: any) => api.post('/posts/', data),
  update: (id: number, data: any) => api.put(`/posts/${id}`, data),
  delete: (id: number) => api.delete(`/posts/${id}`),
  publish: (id: number) => api.post(`/posts/${id}/publish`),
  generate: (data: { location_id: number; topic?: string; post_type?: string }) =>
    api.post('/posts/generate', data),
};

// Reviews
export const reviewsAPI = {
  getAll: (locationId?: number) =>
    api.get('/reviews/', { params: { location_id: locationId } }),
  getById: (id: number) => api.get(`/reviews/${id}`),
  update: (id: number, data: any) => api.put(`/reviews/${id}`, data),
  reply: (id: number, replyText: string) =>
    api.post(`/reviews/${id}/reply`, null, { params: { reply_text: replyText } }),
  generateReply: (id: number, tone?: string) =>
    api.post(`/reviews/${id}/generate-reply`, { review_id: id, tone }),
  sync: (locationId?: number) =>
    api.post('/reviews/sync', null, { params: { location_id: locationId } }),
};

export default api;
