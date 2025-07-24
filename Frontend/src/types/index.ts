export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'moderator' | 'contributor';
  avatar?: string;
}

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

export interface BoardForm {
  name: string;
  description: string;
  visibility: 'public' | 'private';
  allow_anonymous_feedback: boolean;
  require_approval: boolean;
  allow_comments: boolean;
  allow_voting: boolean;
} 