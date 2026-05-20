import { Bot } from 'lucide-react'

function TypingIndicator() {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gray-100">
        <Bot className="w-5 h-5 text-gray-700" />
      </div>
      
      <div className="flex-1">
        <div className="inline-block bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
        <p className="mt-1 text-xs text-gray-500">Analyzing...</p>
      </div>
    </div>
  )
}

export default TypingIndicator
