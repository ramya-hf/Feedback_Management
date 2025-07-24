import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  AuthResponse, 
  User, 
  Board, 
  Feedback, 
  Comment, 
  LoginForm, 
  RegisterForm,
  FeedbackForm,
  CommentForm,
  PaginatedResponse,
  ApiResponse 
} from '../types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post('http://localhost:8000/api/auth/refresh/', {
            refresh: refreshToken,
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: LoginForm): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await api.post('/auth/login/', credentials);
    return response.data;
  },

  register: async (userData: RegisterForm): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await api.post('/auth/logout/', { refresh_token: refreshToken });
    }
  },

  refreshToken: async (): Promise<{ access: string }> => {
    const refreshToken = localStorage.getItem('refresh_token');
    const response: AxiosResponse<{ access: string }> = await api.post('/auth/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/auth/me/');
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response: AxiosResponse<User> = await api.put('/auth/profile/', userData);
    return response.data;
  },

  changePassword: async (passwords: { old_password: string; new_password: string; new_password_confirm: string }): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post('/auth/change-password/', passwords);
    return response.data;
  },
};

// Boards API
export const boardsAPI = {
  getBoards: async (params?: any): Promise<PaginatedResponse<Board>> => {
    const response: AxiosResponse<PaginatedResponse<Board>> = await api.get('/boards/', { params });
    return response.data;
  },

  getBoard: async (id: string): Promise<Board> => {
    const response: AxiosResponse<Board> = await api.get(`/boards/${id}/`);
    return response.data;
  },

  createBoard: async (boardData: Partial<Board>): Promise<Board> => {
    const response: AxiosResponse<Board> = await api.post('/boards/', boardData);
    return response.data;
  },

  updateBoard: async (id: string, boardData: Partial<Board>): Promise<Board> => {
    const response: AxiosResponse<Board> = await api.put(`/boards/${id}/`, boardData);
    return response.data;
  },

  deleteBoard: async (id: string): Promise<void> => {
    await api.delete(`/boards/${id}/`);
  },

  addModerator: async (boardId: string, userId: string): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/boards/${boardId}/add-moderator/`, { user_id: userId });
    return response.data;
  },

  removeModerator: async (boardId: string, userId: string): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/boards/${boardId}/remove-moderator/`, { user_id: userId });
    return response.data;
  },

  addMember: async (boardId: string, userId: string): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/boards/${boardId}/add-member/`, { user_id: userId });
    return response.data;
  },

  removeMember: async (boardId: string, userId: string): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/boards/${boardId}/remove-member/`, { user_id: userId });
    return response.data;
  },
};

// Feedback API
export const feedbackAPI = {
  getFeedback: async (params?: any): Promise<PaginatedResponse<Feedback>> => {
    const response: AxiosResponse<PaginatedResponse<Feedback>> = await api.get('/feedback/', { params });
    return response.data;
  },

  getFeedbackItem: async (id: string): Promise<Feedback> => {
    const response: AxiosResponse<Feedback> = await api.get(`/feedback/${id}/`);
    return response.data;
  },

  createFeedback: async (feedbackData: FeedbackForm): Promise<Feedback> => {
    const response: AxiosResponse<Feedback> = await api.post('/feedback/', feedbackData);
    return response.data;
  },

  updateFeedback: async (id: string, feedbackData: Partial<FeedbackForm>): Promise<Feedback> => {
    const response: AxiosResponse<Feedback> = await api.put(`/feedback/${id}/`, feedbackData);
    return response.data;
  },

  deleteFeedback: async (id: string): Promise<void> => {
    await api.delete(`/feedback/${id}/`);
  },

  voteFeedback: async (id: string, voteType: 'upvote' | 'downvote'): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/feedback/${id}/vote/`, { vote_type: voteType });
    return response.data;
  },

  removeVote: async (id: string): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/feedback/${id}/remove-vote/`);
    return response.data;
  },

  setStatus: async (id: string, status: Feedback['status']): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/feedback/${id}/set-status/`, { status });
    return response.data;
  },

  addTags: async (id: string, tags: string[]): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/feedback/${id}/add-tag/`, { tags });
    return response.data;
  },

  removeTags: async (id: string, tags: string[]): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/feedback/${id}/remove-tag/`, { tags });
    return response.data;
  },

  attachFile: async (id: string, file: File): Promise<ApiResponse<void>> => {
    const formData = new FormData();
    formData.append('file', file);
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/feedback/${id}/attach-file/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

// Comments API
export const commentsAPI = {
  getComments: async (params?: any): Promise<PaginatedResponse<Comment>> => {
    const response: AxiosResponse<PaginatedResponse<Comment>> = await api.get('/comments/', { params });
    return response.data;
  },

  getComment: async (id: string): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.get(`/comments/${id}/`);
    return response.data;
  },

  createComment: async (commentData: CommentForm): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.post('/comments/', commentData);
    return response.data;
  },

  updateComment: async (id: string, commentData: Partial<CommentForm>): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.put(`/comments/${id}/`, commentData);
    return response.data;
  },

  deleteComment: async (id: string): Promise<void> => {
    await api.delete(`/comments/${id}/`);
  },

  voteComment: async (id: string, voteType: 'upvote' | 'downvote'): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/comments/${id}/vote/`, { vote_type: voteType });
    return response.data;
  },

  removeVote: async (id: string): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/comments/${id}/remove-vote/`);
    return response.data;
  },

  moderateComment: async (id: string, isActive: boolean): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.post(`/comments/${id}/moderate/`, { is_active: isActive });
    return response.data;
  },
};

// Users API (for admin/moderator)
export const usersAPI = {
  getUsers: async (params?: any): Promise<PaginatedResponse<User>> => {
    const response: AxiosResponse<PaginatedResponse<User>> = await api.get('/auth/users/', { params });
    return response.data;
  },

  getUser: async (id: string): Promise<User> => {
    const response: AxiosResponse<User> = await api.get(`/auth/users/${id}/`);
    return response.data;
  },

  updateUser: async (id: string, userData: Partial<User>): Promise<User> => {
    const response: AxiosResponse<User> = await api.put(`/auth/users/${id}/`, userData);
    return response.data;
  },

  updateUserRole: async (id: string, role: User['role']): Promise<User> => {
    const response: AxiosResponse<User> = await api.patch(`/auth/users/${id}/role/`, { role });
    return response.data;
  },

  activateUser: async (id: string): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.patch(`/auth/users/${id}/activate/`);
    return response.data;
  },

  deactivateUser: async (id: string): Promise<ApiResponse<void>> => {
    const response: AxiosResponse<ApiResponse<void>> = await api.patch(`/auth/users/${id}/deactivate/`);
    return response.data;
  },

  getUserStats: async (): Promise<any> => {
    const response: AxiosResponse<any> = await api.get('/auth/stats/');
    return response.data;
  },
};

export default api; 