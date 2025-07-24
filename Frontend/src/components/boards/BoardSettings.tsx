import React from 'react';
import { Board } from '../../types';

interface Props {
  board: Board;
}

export const BoardSettings: React.FC<Props> = ({ board }) => (
  <div className="mt-4">
    <h3 className="text-lg font-semibold mb-2">Settings</h3>
    <ul className="space-y-1">
      <li>Visibility: <span className="font-medium">{board.visibility}</span></li>
      <li>Allow Anonymous Feedback: <span className="font-medium">{board.allow_anonymous_feedback ? 'Yes' : 'No'}</span></li>
      <li>Require Approval: <span className="font-medium">{board.require_approval ? 'Yes' : 'No'}</span></li>
      <li>Allow Comments: <span className="font-medium">{board.allow_comments ? 'Yes' : 'No'}</span></li>
      <li>Allow Voting: <span className="font-medium">{board.allow_voting ? 'Yes' : 'No'}</span></li>
    </ul>
  </div>
); 