import { Link } from 'react-router-dom'
import { Menu, TrendingUp, User, LogOut } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

function Header({ onMenuClick }) {
  const { user, isAuthenticated, logout } = useAuthStore()

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            <Menu className="w-6 h-6" />
          </button>
          
          <Link to="/" className="flex items-center gap-2">
            <TrendingUp className="w-8 h-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900">
              Nifty Stock Intelligence
            </span>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">
                  {user?.name || user?.email}
                </span>
              </div>
              <button
                onClick={logout}
                className="btn btn-secondary flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn btn-primary">
              Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
