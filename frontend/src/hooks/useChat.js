import { useState, useCallback } from 'react'
import { chatAPI } from '@/services/api'
import { toast } from 'sonner'

export function useChat(sessionId) {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const sendMessage = useCallback(async (content) => {
    if (!content.trim()) return

    const userMessage = {
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      const response = await chatAPI.sendMessage({
        session_id: sessionId,
        message: content
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.content,
        timestamp: response.data.timestamp,
        analysis_data: response.data.analysis_data,
        sources: response.data.sources
      }

      setMessages(prev => [...prev, assistantMessage])
      
      return response.data
    } catch (err) {
      setError(err.message)
      toast.error('Failed to send message. Please try again.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    setMessages
  }
}
