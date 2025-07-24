import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { BoardList } from '../components/boards/BoardList';
import { BoardForm } from '../components/boards/BoardForm';

export const BoardsPage: React.FC = () => (
  <Routes>
    <Route path="/" element={<BoardList />} />
    <Route path="/new" element={<BoardForm />} />
    <Route path=":id/edit" element={<BoardForm />} />
  </Routes>
); 