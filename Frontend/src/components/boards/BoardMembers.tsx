import React, { useEffect, useState } from 'react';
import { Board, User } from '../../types';
import { boardsAPI, usersAPI } from '../../services/api';

interface Props {
  board: Board;
  refresh: () => void;
}

export const BoardMembers: React.FC<Props> = ({ board, refresh }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [role, setRole] = useState<'member' | 'moderator'>('member');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    usersAPI.list().then(setUsers).catch(() => setError('Failed to load users'));
  }, []);

  const handleAdd = async () => {
    if (!selectedUser) return;
    setLoading(true);
    setError('');
    try {
      if (role === 'member') {
        await boardsAPI.addMember(board.id, selectedUser);
      } else {
        await boardsAPI.addModerator(board.id, selectedUser);
      }
      setSelectedUser('');
      refresh();
    } catch {
      setError('Failed to add user');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (userId: string, role: 'member' | 'moderator') => {
    setLoading(true);
    setError('');
    try {
      if (role === 'member') {
        await boardsAPI.removeMember(board.id, userId);
      } else {
        await boardsAPI.removeModerator(board.id, userId);
      }
      refresh();
    } catch {
      setError('Failed to remove user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8">
      <h3 className="text-lg font-semibold mb-2">Members & Moderators</h3>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mb-4">
        <select value={selectedUser} onChange={e => setSelectedUser(e.target.value)} className="input">
          <option value="">Select user...</option>
          {users.map(u => (
            <option key={u.id} value={u.id}>{u.first_name} {u.last_name} ({u.email})</option>
          ))}
        </select>
        <select value={role} onChange={e => setRole(e.target.value as any)} className="input">
          <option value="member">Member</option>
          <option value="moderator">Moderator</option>
        </select>
        <button className="btn btn-primary" onClick={handleAdd} disabled={loading || !selectedUser}>
          Add
        </button>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="font-medium mb-1">Members</h4>
          <ul className="space-y-1">
            {board.members.map(u => (
              <li key={u.id} className="flex justify-between items-center">
                <span>{u.first_name} {u.last_name} ({u.email})</span>
                <button className="btn btn-danger btn-xs" onClick={() => handleRemove(u.id, 'member')} disabled={loading}>Remove</button>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="font-medium mb-1">Moderators</h4>
          <ul className="space-y-1">
            {board.moderators.map(u => (
              <li key={u.id} className="flex justify-between items-center">
                <span>{u.first_name} {u.last_name} ({u.email})</span>
                <button className="btn btn-danger btn-xs" onClick={() => handleRemove(u.id, 'moderator')} disabled={loading}>Remove</button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}; 