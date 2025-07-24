// User types
export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'moderator' | 'contributor';
  avatar?: string;
  bio?: string;
  phone_number?: string;
  company?: string;
  job_title?: string;
  is_email_verified: boolean;
  email_notifications: boolean;
  date_joined: string;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

// Board types
export interface Board {
  id: string;
  name: string;
  description: string;
  slug: string;
  visibility: 'public' | 'private';
  allow_anonymous_feedback: boolean;
  require_approval: boolean;
  allow_comments: boolean;
  allow_voting: boolean;
  owner: User;
  moderators: User[];
  members: User[];
  created_at: string;
  updated_at: string;
  is_active: boolean;
  feedback_count: number;
  total_votes: number;
}

// Feedback types
export interface Feedback {
  id: string;
  title: string;
  description: string;
  status: 'draft' | 'pending' | 'under_review' | 'planned' | 'in_progress' | 'completed' | 'declined' | 'duplicate';
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: 'feature' | 'bug' | 'improvement' | 'question' | 'other';
  board: string;
  author?: User;
  author_name: string;
  author_email: string;
  assigned_to?: User;
  upvotes: string[];
  downvotes: string[];
  vote_count: number;
  total_votes: number;
  comment_count: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  anonymous_email?: string;
  anonymous_name?: string;
  file?: string;
  tags: string[];
}

// Comment types
export interface Comment {
  id: string;
  content: string;
  feedback: string;
  author?: User;
  author_name: string;
  author_email: string;
  parent?: string;
  is_reply: boolean;
  reply_count: number;
  upvotes: string[];
  downvotes: string[];
  vote_count: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  anonymous_email?: string;
  anonymous_name?: string;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

// Form types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
  company?: string;
  job_title?: string;
  phone_number?: string;
  bio?: string;
}

export interface FeedbackForm {
  title: string;
  description: string;
  board: string;
  category: 'feature' | 'bug' | 'improvement' | 'question' | 'other';
  priority: 'low' | 'medium' | 'high' | 'critical';
  anonymous_email?: string;
  anonymous_name?: string;
  tags?: string[];
}

export interface CommentForm {
  content: string;
  feedback: string;
  parent?: string;
  anonymous_email?: string;
  anonymous_name?: string;
}

// Context types
export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginForm) => Promise<void>;
  register: (userData: RegisterForm) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
} 