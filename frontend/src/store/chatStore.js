import { create } from 'zustand'

const useChatStore = create((set, get) => ({
  currentSessionId: null,
  messages: [],
  isLoading: false,
  error: null,

  setCurrentSession: (sessionId) => {
    set({ currentSessionId: sessionId, messages: [] })
  },

  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }))
  },

  setMessages: (messages) => {
    set({ messages })
  },

  setLoading: (isLoading) => {
    set({ isLoading })
  },

  setError: (error) => {
    set({ error })
  },

  clearMessages: () => {
    set({ messages: [], error: null })
  },

  clearError: () => {
    set({ error: null })
  },
}))

export { useChatStore }
