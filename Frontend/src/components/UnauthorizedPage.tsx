import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, ArrowLeft } from 'lucide-react';

export const UnauthorizedPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        <div className="flex justify-center">
          <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center">
            <Shield className="h-12 w-12 text-red-600" />
          </div>
        </div>
        
        <h1 className="mt-6 text-3xl font-extrabold text-gray-900">
          Access Denied
        </h1>
        
        <p className="mt-4 text-lg text-gray-600">
          You don't have permission to access this page.
        </p>
        
        <p className="mt-2 text-sm text-gray-500">
          Please contact your administrator if you believe this is an error.
        </p>
        
        <div className="mt-8 space-y-4">
          <Link
            to="/dashboard"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}; 