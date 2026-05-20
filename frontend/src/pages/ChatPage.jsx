import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, Loader2, Plus, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import ReactMarkdown from 'react-markdown'

import { useChatStore } from '@/store/chatStore'
import { chatAPI } from '@/services/api'
import ChatMessage from '@/components/Chat/ChatMessage'
import TypingIndicator from '@/components/Chat/TypingIndicator'

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

  useEffect(() => {
    if (sessionId && sessionId !== currentSessionId) {
      loadSession(sessionId)
    } else if (!sessionId && !currentSessionId) {
      // Start new session
      const newSessionId = crypto.randomUUID()
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
      toast.error('Failed to send message. Please try again.')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = () => {
    clearMessages()
    const newSessionId = crypto.randomUUID()
    setCurrentSession(newSessionId)
    navigate(`/chat/${newSessionId}`)
  }

  const handleDeleteChat = async () => {
    if (!currentSessionId) return

    try {
      await chatAPI.deleteSession(currentSessionId)
      toast.success('Chat deleted successfully')
      handleNewChat()
    } catch (error) {
      toast.error('Failed to delete chat')
      console.error(error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stock Analysis Chat</h1>
          <p className="text-gray-600 text-sm">
            Ask me anything about Nifty 100-250 stocks
          </p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={handleNewChat}
            className="btn btn-secondary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Chat
          </button>
          {messages.length > 0 && (
            <button
              onClick={handleDeleteChat}
              className="btn btn-danger flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          )}
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 bg-white rounded-xl border border-gray-200 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && !isLoading && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">💬</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Start a Conversation
              </h3>
              <p className="text-gray-600 mb-6">
                Ask me to analyze any stock, compare companies, or provide market insights.
              </p>
              <div className="space-y-2 max-w-md mx-auto text-left">
                <button
                  onClick={() => setInputValue('Analyze TCS for short-term trading')}
                  className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <span className="text-sm text-gray-700">
                    "Analyze TCS for short-term trading"
                  </span>
                </button>
                <button
                  onClick={() => setInputValue('Compare Infosys and Wipro')}
                  className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <span className="text-sm text-gray-700">
                    "Compare Infosys and Wipro"
                  </span>
                </button>
                <button
                  onClick={() => setInputValue('What are the top IT stocks to buy now?')}
                  className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <span className="text-sm text-gray-700">
                    "What are the top IT stocks to buy now?"
                  </span>
                </button>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}

          {isLoading && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about any stock (e.g., 'Analyze TCS for long-term investment')"
              className="input flex-1"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="btn btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Send
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

// Add import
import DocumentUpload from '@/components/Chat/DocumentUpload'

// Add inside ChatPage component
const [uploadedDocs, setUploadedDocs] = useState([])

const handleDocumentUpload = (docStatus) => {
  setUploadedDocs(prev => [...prev, docStatus])
}

// Add before messages container
<div className="mb-4">
  <DocumentUpload onUploadComplete={handleDocumentUpload} />
</div>


export default ChatPage
