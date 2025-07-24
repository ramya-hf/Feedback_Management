import React, { useState, useEffect } from 'react';
import { Board, BoardForm as BoardFormType } from '../../types';
import { boardsAPI } from '../../services/api';
import { validateBoardForm } from '../../utils';
import { useNavigate, useParams } from 'react-router-dom';
import { Layout } from '../Layout';

const defaultForm: BoardFormType = {
  name: '',
  description: '',
  visibility: 'public',
  allow_anonymous_feedback: false,
  require_approval: false,
  allow_comments: true,
  allow_voting: true,
};

export const BoardForm: React.FC = () => {
  const [form, setForm] = useState<BoardFormType>(defaultForm);
  const [errors, setErrors] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = Boolean(id);

  useEffect(() => {
    if (isEdit) {
      setLoading(true);
      boardsAPI.get(id as string)
        .then(board => setForm({
          name: board.name,
          description: board.description,
          visibility: board.visibility,
          allow_anonymous_feedback: board.allow_anonymous_feedback,
          require_approval: board.require_approval,
          allow_comments: board.allow_comments,
          allow_voting: board.allow_voting,
        }))
        .catch(() => setApiError('Failed to load board'))
        .finally(() => setLoading(false));
    }
  }, [id, isEdit]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validateBoardForm(form);
    setErrors(errs);
    if (Object.keys(errs).length) return;
    setLoading(true);
    setApiError('');
    try {
      if (isEdit) {
        await boardsAPI.update(id as string, form);
      } else {
        await boardsAPI.create(form);
      }
      navigate('/boards');
    } catch (err: any) {
      setApiError('Failed to save board');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">{isEdit ? 'Edit Board' : 'Create Board'}</h2>
        {apiError && <div className="text-red-500 mb-2">{apiError}</div>}
        <form onSubmit={handleSubmit} className="space-y-4 card p-6">
          <div>
            <label className="block font-medium mb-1">Name</label>
            <input name="name" value={form.name} onChange={handleChange} className="input" />
            {errors.name && <div className="text-red-500 text-sm">{errors.name}</div>}
          </div>
          <div>
            <label className="block font-medium mb-1">Description</label>
            <textarea name="description" value={form.description} onChange={handleChange} className="input" />
          </div>
          <div>
            <label className="block font-medium mb-1">Visibility</label>
            <select name="visibility" value={form.visibility} onChange={handleChange} className="input">
              <option value="public">Public</option>
              <option value="private">Private</option>
            </select>
            {errors.visibility && <div className="text-red-500 text-sm">{errors.visibility}</div>}
          </div>
          <div className="flex gap-4 flex-wrap">
            <label className="flex items-center gap-2">
              <input type="checkbox" name="allow_anonymous_feedback" checked={form.allow_anonymous_feedback} onChange={handleChange} />
              Allow Anonymous Feedback
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" name="require_approval" checked={form.require_approval} onChange={handleChange} />
              Require Approval
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" name="allow_comments" checked={form.allow_comments} onChange={handleChange} />
              Allow Comments
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" name="allow_voting" checked={form.allow_voting} onChange={handleChange} />
              Allow Voting
            </label>
          </div>
          <div>
            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? 'Saving...' : isEdit ? 'Update Board' : 'Create Board'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}; 