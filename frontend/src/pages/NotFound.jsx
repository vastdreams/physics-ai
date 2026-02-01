/**
 * PATH: frontend/src/pages/NotFound.jsx
 * PURPOSE: 404 Not Found page
 */

import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <div className="text-8xl font-bold gradient-text mb-4">404</div>
      <h1 className="text-2xl font-semibold text-dark-100 mb-2">Page Not Found</h1>
      <p className="text-dark-400 max-w-md mb-8">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div className="flex items-center gap-4">
        <Link to="/" className="btn-primary flex items-center gap-2">
          <Home size={18} />
          Go Home
        </Link>
        <button 
          onClick={() => window.history.back()}
          className="btn-secondary flex items-center gap-2"
        >
          <ArrowLeft size={18} />
          Go Back
        </button>
      </div>
    </div>
  );
}
