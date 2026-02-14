/**
 * PATH: frontend/src/pages/NotFound.jsx
 * PURPOSE: 404 Not Found page
 */

import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

const ICON_SIZE = 18;

/** 404 page with links to navigate home or go back. */
export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <div className="text-8xl font-black gradient-text-animated mb-4">404</div>
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Page Not Found</h1>
      <p className="text-slate-500 max-w-md mb-8">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div className="flex items-center gap-4">
        <Link to="/" className="btn-primary flex items-center gap-2">
          <Home size={ICON_SIZE} />
          Go Home
        </Link>
        <button 
          onClick={() => window.history.back()}
          className="btn-secondary flex items-center gap-2"
        >
          <ArrowLeft size={ICON_SIZE} />
          Go Back
        </button>
      </div>
    </div>
  );
}
