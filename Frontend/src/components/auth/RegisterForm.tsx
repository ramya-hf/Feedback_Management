import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export const RegisterForm: React.FC = () => {
  const { register } = useAuth();
  const [form, setForm] = useState({
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    if (form.password !== form.password_confirm) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }
    try {
      await register(form);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16 p-6 card">
      <h2 className="text-2xl font-bold mb-4">Register</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input className="input" name="email" placeholder="Email" value={form.email} onChange={handleChange} required />
        <input className="input" name="username" placeholder="Username" value={form.username} onChange={handleChange} required />
        <input className="input" name="first_name" placeholder="First Name" value={form.first_name} onChange={handleChange} required />
        <input className="input" name="last_name" placeholder="Last Name" value={form.last_name} onChange={handleChange} required />
        <input className="input" name="password" type="password" placeholder="Password" value={form.password} onChange={handleChange} required />
        <input className="input" name="password_confirm" type="password" placeholder="Confirm Password" value={form.password_confirm} onChange={handleChange} required />
        {error && <div className="text-red-500 text-sm">{error}</div>}
        <button className="btn btn-primary w-full" type="submit" disabled={loading}>{loading ? 'Registering...' : 'Register'}</button>
      </form>
    </div>
  );
}; 