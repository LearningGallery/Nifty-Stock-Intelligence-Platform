import { createContext, useContext, useState } from 'react'

const ChatContext = createContext(null)

export function ChatProvider({ children }) {
  const [activeSessions, setActiveSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)

  const addSession = (session) => {
    setActiveSessions(prev => [session, ...prev])
  }

  const removeSession = (sessionId) => {
    setActiveSessions(prev => prev.filter(s => s.session_id !== sessionId))
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null)
    }
  }

  const value = {
    activeSessions,
    currentSessionId,
    setCurrentSessionId,
    addSession,
    removeSession
  }

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChatContext() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider')
  }
  return context
}
