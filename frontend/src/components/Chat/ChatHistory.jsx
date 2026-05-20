import { Clock, MessageSquare, Trash2 } from 'lucide-react'
import { format } from 'date-fns'
import { useState } from 'react'

function ChatHistory({ sessions, onSelectSession, onDeleteSession, currentSessionId }) {
  const [hoveredSession, setHoveredSession] = useState(null)

  return (
    <div className="w-64 border-r border-gray-200 bg-gray-50 overflow-y-auto">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
      </div>

      <div className="p-2 space-y-1">
        {sessions.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-sm">
            No chat history yet
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                currentSessionId === session.session_id
                  ? 'bg-primary-50 border border-primary-200'
                  : 'hover:bg-gray-100'
              }`}
              onClick={() => onSelectSession(session.session_id)}
              onMouseEnter={() => setHoveredSession(session.session_id)}
              onMouseLeave={() => setHoveredSession(null)}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <MessageSquare className="w-4 h-4 text-gray-600 flex-shrink-0" />
                    <span className="text-sm font-medium text-gray-900 truncate">
                      {session.messages?.[0]?.content?.substring(0, 30) || 'New Chat'}...
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    {format(new Date(session.updated_at), 'MMM dd, HH:mm')}
                  </div>
                </div>

                {hoveredSession === session.session_id && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteSession(session.session_id)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ChatHistory
