import { User, Bot, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { format } from 'date-fns'

function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-100' : 'bg-gray-100'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-primary-700" />
        ) : (
          <Bot className="w-5 h-5 text-gray-700" />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
        <div
          className={`inline-block max-w-3xl ${
            isUser
              ? 'bg-primary-600 text-white rounded-2xl rounded-tr-sm'
              : 'bg-gray-100 text-gray-900 rounded-2xl rounded-tl-sm'
          } px-4 py-3`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none markdown-content">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Analysis Data */}
        {message.analysis_data && (
          <div className="mt-3 p-4 bg-blue-50 rounded-lg text-left">
            <h4 className="font-semibold text-sm text-gray-900 mb-2">
              Analysis Summary
            </h4>
            <div className="space-y-1 text-sm">
              {message.analysis_data.stock_symbol && (
                <p>
                  <span className="text-gray-600">Stock:</span>{' '}
                  <span className="font-medium">
                    {message.analysis_data.stock_symbol}
                  </span>
                </p>
              )}
              {message.analysis_data.recommendation && (
                <p>
                  <span className="text-gray-600">Recommendation:</span>{' '}
                  <span className={`font-medium ${
                    message.analysis_data.recommendation === 'BUY'
                      ? 'text-success-600'
                      : message.analysis_data.recommendation === 'SELL'
                      ? 'text-danger-600'
                      : 'text-warning-600'
                  }`}>
                    {message.analysis_data.recommendation}
                  </span>
                </p>
              )}
              {message.analysis_data.confidence && (
                <p>
                  <span className="text-gray-600">Confidence:</span>{' '}
                  <span className="font-medium">
                    {message.analysis_data.confidence}
                  </span>
                </p>
              )}
            </div>
          </div>
        )}

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 text-left">
            <details className="text-xs text-gray-600">
              <summary className="cursor-pointer hover:text-gray-900">
                Sources ({message.sources.length})
              </summary>
              <ul className="mt-2 space-y-1 pl-4">
                {message.sources.map((source, idx) => (
                  <li key={idx}>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary-600 hover:underline"
                    >
                      <ExternalLink className="w-3 h-3" />
                      {source.title || source.type}
                    </a>
                  </li>
                ))}
              </ul>
            </details>
          </div>
        )}

        {/* Timestamp */}
        <p className="mt-1 text-xs text-gray-500">
          {format(new Date(message.timestamp), 'HH:mm')}
        </p>
      </div>
    </div>
  )
}

export default ChatMessage
