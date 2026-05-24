import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

import { useChatStore } from '@/store/chatStore'
import { chatAPI } from '@/services/api'
import ChatMessage from '@/components/Chat/ChatMessage'
import TypingIndicator from '@/components/Chat/TypingIndicator'
import DocumentUpload from '@/components/Chat/DocumentUpload'

// Helper function to generate UUIDs in all browser contexts
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

function ChatPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const messagesEndRef = useRef(null)

  const {
    currentSessionId,
    messages,
    isLoading,
    setCurrentSession,
    addMessage,
    setMessages,
    setLoading,
    clearMessages,
  } = useChatStore()

  const [inputValue, setInputValue] = useState('')
  const [uploadedDocs, setUploadedDocs] = useState([])

  useEffect(() => {
    if (sessionId && sessionId !== currentSessionId) {
      loadSession(sessionId)
    } else if (!sessionId && !currentSessionId) {
      const newSessionId = generateUUID()
      setCurrentSession(newSessionId)
      navigate(`/chat/${newSessionId}`, { replace: true })
    }
  }, [sessionId, currentSessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadSession = async (id) => {
    try {
      setLoading(true)
      const response = await chatAPI.getSession(id)
      setCurrentSession(id)
      setMessages(response.data.messages || [])
    } catch (error) {
      toast.error('Failed to load chat session')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleDocumentUpload = (docStatus) => {
    setUploadedDocs(prev => [...prev, docStatus])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    }

    addMessage(userMessage)
    setInputValue('')
    setLoading(true)

    try {
      const response = await chatAPI.sendMessage({
        session_id: currentSessionId,
        message: inputValue,
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.content,
        timestamp: response.data.timestamp,
        analysis_data: response.data.analysis_data,
        sources: response.data.sources,
      }

      addMessage(assistantMessage)
    } catch (error) {
      toast.error('Failed to send message.')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = () => {
    clearMessages()
    const newSessionId = generateUUID()
    setCurrentSession(newSessionId)
    navigate(`/chat/${newSessionId}`)
  }

  const handleDeleteChat = async () => {
    if (!currentSessionId) return
    try {
      await chatAPI.deleteSession(currentSessionId)
      toast.success('Chat deleted')
      handleNewChat()
    } catch (error) {
      toast.error('Failed to delete chat')
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stock Analysis Chat</h1>
        </div>
        <div className="flex gap-2">
          <button onClick={handleNewChat} className="btn btn-secondary">New Chat</button>
          {messages.length > 0 && (
            <button onClick={handleDeleteChat} className="btn btn-danger">Delete</button>
          )}
        </div>
      </div>

      <div className="flex-1 bg-white rounded-xl border border-gray-200 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="mb-4">
            <DocumentUpload onUploadComplete={handleDocumentUpload} />
          </div>

          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about any stock..."
              className="input flex-1"
              disabled={isLoading}
            />
            <button type="submit" disabled={!inputValue.trim() || isLoading} className="btn btn-primary">
              {isLoading ? <Loader2 className="animate-spin" /> : <Send />}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ChatPage