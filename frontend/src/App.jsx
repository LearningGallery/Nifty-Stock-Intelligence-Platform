import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'

// Pages
import HomePage from './pages/HomePage'
import ChatPage from './pages/ChatPage'
import AnalysisPage from './pages/AnalysisPage'
import ExplorePage from './pages/ExplorePage'
import NotFoundPage from './pages/NotFoundPage'

// Layout
import Layout from './components/Layout/Layout'

// Hooks
import { useAuthStore } from './store/authStore'

function App() {
  const { initialize } = useAuthStore()

  useEffect(() => {
    // Initialize auth state
    initialize()
  }, [initialize])

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="chat/:sessionId" element={<ChatPage />} />
        <Route path="analysis" element={<AnalysisPage />} />
        <Route path="analysis/:symbol" element={<AnalysisPage />} />
        <Route path="explore" element={<ExplorePage />} />
        <Route path="404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Route>
    </Routes>
  )
}

export default App
