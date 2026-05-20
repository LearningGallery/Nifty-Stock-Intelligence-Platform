import { useRef, useEffect } from 'react'
import ChatMessage from './ChatMessage'
import TypingIndicator from './TypingIndicator'

function ChatContainer({ messages, isLoading }) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.length === 0 && !isLoading && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-6xl mb-4">💬</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Start Your Stock Analysis
            </h3>
            <p className="text-gray-600">
              Ask me anything about Nifty 100-250 stocks
            </p>
          </div>
        </div>
      )}

      {messages.map((message, index) => (
        <ChatMessage key={index} message={message} />
      ))}

      {isLoading && <TypingIndicator />}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default ChatContainer
