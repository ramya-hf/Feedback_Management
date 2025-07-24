import axios from 'axios';
import { Board, BoardForm, User } from '../types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
});

// Always attach JWT token if present
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const boardsAPI = {
  list: async (): Promise<Board[]> => {
    const res = await api.get('/boards/');
    return res.data.results || res.data;
  },
  get: async (id: string): Promise<Board> => {
    const res = await api.get(`/boards/${id}/`);
    return res.data;
  },
  create: async (data: BoardForm): Promise<Board> => {
    const res = await api.post('/boards/', data);
    return res.data;
  },
  update: async (id: string, data: BoardForm): Promise<Board> => {
    const res = await api.patch(`/boards/${id}/`, data);
    return res.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/boards/${id}/`);
  },
  addMember: async (boardId: string, userId: string) => {
    await api.post(`/boards/${boardId}/add-member/`, { user_id: userId });
  },
  removeMember: async (boardId: string, userId: string) => {
    await api.post(`/boards/${boardId}/remove-member/`, { user_id: userId });
  },
  addModerator: async (boardId: string, userId: string) => {
    await api.post(`/boards/${boardId}/add-moderator/`, { user_id: userId });
  },
  removeModerator: async (boardId: string, userId: string) => {
    await api.post(`/boards/${boardId}/remove-moderator/`, { user_id: userId });
  },
};

export const usersAPI = {
  list: async (): Promise<User[]> => {
    const res = await api.get('/auth/users/');
    return res.data.results || res.data;
  },
};

export default api; 