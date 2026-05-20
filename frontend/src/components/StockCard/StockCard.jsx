import { TrendingUp, TrendingDown } from 'lucide-react'
import { format } from 'date-fns'

function StockCard({ stock, onClick }) {
  const isPositive = (stock.change_percent || 0) >= 0

  return (
    <button
      onClick={onClick}
      className="card text-left hover:shadow-lg transition-all cursor-pointer w-full"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{stock.symbol}</h3>
          <p className="text-sm text-gray-600 line-clamp-1">{stock.company_name}</p>
        </div>
        {stock.sector && (
          <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full">
            {stock.sector}
          </span>
        )}
      </div>

      <div className="flex items-baseline gap-3 mb-3">
        <span className="text-2xl font-bold text-gray-900">
          ₹{stock.current_price?.toFixed(2) || 'N/A'}
        </span>
        <div
          className={`flex items-center gap-1 text-sm font-medium ${
            isPositive ? 'text-success-600' : 'text-danger-600'
          }`}
        >
          {isPositive ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          <span>
            {isPositive ? '+' : ''}
            {stock.change_percent?.toFixed(2)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <span className="text-gray-600">Open:</span>
          <span className="ml-2 font-medium text-gray-900">
            ₹{stock.open?.toFixed(2) || 'N/A'}
          </span>
        </div>
        <div>
          <span className="text-gray-600">High:</span>
          <span className="ml-2 font-medium text-gray-900">
            ₹{stock.high?.toFixed(2) || 'N/A'}
          </span>
        </div>
        <div>
          <span className="text-gray-600">Low:</span>
          <span className="ml-2 font-medium text-gray-900">
            ₹{stock.low?.toFixed(2) || 'N/A'}
          </span>
        </div>
        <div>
          <span className="text-gray-600">Volume:</span>
          <span className="ml-2 font-medium text-gray-900">
            {stock.volume ? (stock.volume / 1000000).toFixed(2) + 'M' : 'N/A'}
          </span>
        </div>
      </div>

      {stock.last_updated && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Updated: {format(new Date(stock.last_updated), 'MMM dd, HH:mm')}
          </p>
        </div>
      )}
    </button>
  )
}

export default StockCard
