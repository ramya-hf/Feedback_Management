import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Layout } from './Layout';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-6">Welcome, {user?.first_name}!</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card p-6 flex flex-col items-center">
          <span className="text-2xl font-bold text-blue-600">Boards</span>
          <span className="text-4xl font-extrabold mt-2">—</span>
          <span className="text-gray-500 mt-1">Total Boards</span>
        </div>
        <div className="card p-6 flex flex-col items-center">
          <span className="text-2xl font-bold text-green-600">Feedback</span>
          <span className="text-4xl font-extrabold mt-2">—</span>
          <span className="text-gray-500 mt-1">Total Feedback</span>
        </div>
        <div className="card p-6 flex flex-col items-center">
          <span className="text-2xl font-bold text-purple-600">Members</span>
          <span className="text-4xl font-extrabold mt-2">—</span>
          <span className="text-gray-500 mt-1">Total Members</span>
        </div>
      </div>
      <div className="card p-6">
        <h2 className="text-xl font-semibold mb-2">Get Started</h2>
        <ul className="list-disc pl-6 text-gray-700">
          <li>Use the sidebar to navigate between Dashboard and Boards.</li>
          <li>Create and manage boards, add members, and collect feedback.</li>
          <li>All features are protected and require login.</li>
        </ul>
      </div>
    </Layout>
  );
}; 