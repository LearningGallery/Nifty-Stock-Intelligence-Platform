import { TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'
import clsx from 'clsx'

function QuickStats({ data }) {
  const getRecommendationColor = (rec) => {
    switch (rec) {
      case 'BUY':
        return 'bg-success-100 text-success-700 border-success-200'
      case 'SELL':
        return 'bg-danger-100 text-danger-700 border-danger-200'
      default:
        return 'bg-warning-100 text-warning-700 border-warning-200'
    }
  }

  const getConfidenceColor = (conf) => {
    switch (conf) {
      case 'HIGH':
        return 'text-success-600'
      case 'MEDIUM':
        return 'text-warning-600'
      default:
        return 'text-danger-600'
    }
  }

  const changePercent =
    ((data.current_price - data.short_term_target.entry_point) /
      data.short_term_target.entry_point) *
    100

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Current Price</span>
          {changePercent > 0 ? (
            <TrendingUp className="w-4 h-4 text-success-600" />
          ) : (
            <TrendingDown className="w-4 h-4 text-danger-600" />
          )}
        </div>
        <div className="text-2xl font-bold text-gray-900">
          ₹{data.current_price.toFixed(2)}
        </div>
        <div
          className={clsx(
            'text-sm font-medium mt-1',
            changePercent > 0 ? 'text-success-600' : 'text-danger-600'
          )}
        >
          {changePercent > 0 ? '+' : ''}
          {changePercent.toFixed(2)}%
        </div>
      </div>

      <div className="card">
        <div className="text-sm text-gray-600 mb-2">Recommendation</div>
        <div
          className={clsx(
            'inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border',
            getRecommendationColor(data.recommendation)
          )}
        >
          {data.recommendation}
        </div>
        <div className="text-sm text-gray-600 mt-2">
          Confidence:{' '}
          <span className={clsx('font-medium', getConfidenceColor(data.confidence_level))}>
            {data.confidence_level}
          </span>
        </div>
      </div>

      <div className="card">
        <div className="text-sm text-gray-600 mb-2">Technical Score</div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-gray-900">
            {data.technical_score.toFixed(1)}
          </span>
          <span className="text-gray-500">/10</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all"
            style={{ width: `${(data.technical_score / 10) * 100}%` }}
          />
        </div>
      </div>

      <div className="card">
        <div className="text-sm text-gray-600 mb-2">Risk Level</div>
        <div className="flex items-center gap-2">
          <AlertTriangle
            className={clsx(
              'w-5 h-5',
              data.risk_level === 'HIGH'
                ? 'text-danger-600'
                : data.risk_level === 'MODERATE'
                ? 'text-warning-600'
                : 'text-success-600'
            )}
          />
          <span className="text-lg font-semibold text-gray-900">
            {data.risk_level}
          </span>
        </div>
        <div className="text-sm text-gray-600 mt-2">
          {data.risk_factors.length} risks identified
        </div>
      </div>
    </div>
  )
}

export default QuickStats
