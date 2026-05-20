import { Link } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'

function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <div className="text-9xl font-bold text-primary-600 mb-4">404</div>
      
      <h1 className="text-3xl font-bold text-gray-900 mb-2">
        Page Not Found
      </h1>
      
      <p className="text-gray-600 mb-8 max-w-md">
        The page you're looking for doesn't exist or has been moved.
      </p>

      <div className="flex gap-4">
        <Link
          to="/"
          className="btn btn-primary flex items-center gap-2"
        >
          <Home className="w-5 h-5" />
          Go Home
        </Link>
        
        <button
          onClick={() => window.history.back()}
          className="btn btn-secondary flex items-center gap-2"
        >
          <ArrowLeft className="w-5 h-5" />
          Go Back
        </button>
      </div>
    </div>
  )
}

export default NotFoundPage
