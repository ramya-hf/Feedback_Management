import React, { useEffect, useState } from 'react';
import { Board } from '../../types';
import { boardsAPI } from '../../services/api';
import { Link } from 'react-router-dom';
import { Layout } from '../Layout';

export const BoardList: React.FC = () => {
  const [boards, setBoards] = useState<Board[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    boardsAPI.list()
      .then(setBoards)
      .catch(() => setError('Failed to load boards'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Boards</h2>
        <Link to="/boards/new" className="btn btn-primary">+ New Board</Link>
      </div>
      {loading ? (
        <div className="p-8 text-center">Loading boards...</div>
      ) : error ? (
        <div className="p-8 text-center text-red-500">{error}</div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {boards.map(board => (
            <div key={board.id} className="card p-6 flex flex-col gap-2">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold">{board.name}</h3>
                <span className={`px-2 py-1 rounded text-xs ${board.visibility === 'public' ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-700'}`}>{board.visibility}</span>
              </div>
              <p className="text-gray-600 text-sm mb-2">{board.description}</p>
              <div className="flex gap-2 mt-auto">
                <Link to={`/boards/${board.id}/edit`} className="btn btn-secondary">Edit</Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}; 