import { CheckCircle, XCircle, AlertTriangle, TrendingUp, Calendar } from 'lucide-react'
import { format } from 'date-fns'
import ReactMarkdown from 'react-markdown'

function AnalysisReport({ data }) {
  return (
    <div className="space-y-6">
      {/* Company Overview */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {data.company_name}
            </h2>
            <p className="text-gray-600 mt-1">
              {data.sector} • Market Cap: ₹{(data.market_cap / 100).toFixed(0)}K Cr
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600">Analyzed on</div>
            <div className="text-sm font-medium text-gray-900">
              {format(new Date(data.analysis_timestamp), 'MMM dd, yyyy HH:mm')}
            </div>
          </div>
        </div>
      </div>

      {/* Pros and Cons */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card bg-success-50 border-success-200">
          <h3 className="text-lg font-semibold text-success-900 mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Strengths & Opportunities
          </h3>
          <ul className="space-y-2">
            {data.pros.map((pro, idx) => (
              <li key={idx} className="flex items-start gap-2 text-success-800">
                <span className="text-success-600 font-bold mt-0.5">•</span>
                <span>{pro}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="card bg-danger-50 border-danger-200">
          <h3 className="text-lg font-semibold text-danger-900 mb-4 flex items-center gap-2">
            <XCircle className="w-5 h-5" />
            Risks & Concerns
          </h3>
          <ul className="space-y-2">
            {data.cons.map((con, idx) => (
              <li key={idx} className="flex items-start gap-2 text-danger-800">
                <span className="text-danger-600 font-bold mt-0.5">•</span>
                <span>{con}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Price Targets */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          Price Targets (Short-Term: 1-3 months)
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Entry Point</div>
            <div className="text-xl font-bold text-gray-900">
              ₹{data.short_term_target.entry_point.toFixed(2)}
            </div>
          </div>

          <div className="text-center p-4 bg-success-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Target 1</div>
            <div className="text-xl font-bold text-success-700">
              ₹{data.short_term_target.target_1.toFixed(2)}
            </div>
            <div className="text-xs text-success-600 mt-1">
              +{data.short_term_target.expected_upside_percent.toFixed(1)}%
            </div>
          </div>

          {data.short_term_target.target_2 && (
            <div className="text-center p-4 bg-success-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Target 2</div>
              <div className="text-xl font-bold text-success-700">
                ₹{data.short_term_target.target_2.toFixed(2)}
              </div>
            </div>
          )}

          <div className="text-center p-4 bg-danger-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Stop Loss</div>
            <div className="text-xl font-bold text-danger-700">
              ₹{data.short_term_target.stop_loss.toFixed(2)}
            </div>
          </div>

          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Risk:Reward</div>
            <div className="text-xl font-bold text-gray-900">
              {data.short_term_target.risk_reward_ratio}
            </div>
          </div>
        </div>
      </div>

      {/* Technical Signals */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Technical Analysis
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.technical_signals.map((signal, idx) => (
            <div key={idx} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">{signal.indicator}</span>
                <span className="text-sm font-semibold text-primary-600">
                  {signal.signal}
                </span>
              </div>
              <div className="text-sm text-gray-600">{signal.description}</div>
              <div className="text-xs text-gray-500 mt-1">
                Value: {signal.value}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fundamental Data */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Fundamental Metrics
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(data.fundamental_data).map(([key, value]) => (
            <div key={key} className="p-3 bg-gray-50 rounded-lg">
              <div className="text-xs text-gray-600 mb-1">
                {key.replace(/_/g, ' ').toUpperCase()}
              </div>
              <div className="text-lg font-semibold text-gray-900">
                {typeof value === 'number' ? value.toFixed(2) : value}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* News & Sentiment */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          News & Sentiment
        </h3>
        
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-600">Sentiment Score</span>
            <span className="text-xl font-bold text-gray-900">
              {data.sentiment_score.toFixed(1)}/10
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all"
              style={{ width: `${(data.sentiment_score / 10) * 100}%` }}
            />
          </div>
        </div>

        <p className="text-gray-700 mb-4">{data.news_summary}</p>

        {data.recent_news.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900">Recent Headlines:</h4>
            <ul className="space-y-2">
              {data.recent_news.slice(0, 5).map((news, idx) => (
                <li key={idx} className="text-sm">
                  <a
                    href={news.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:underline"
                  >
                    {news.title}
                  </a>
                  <span className="text-gray-500 text-xs ml-2">
                    {news.source}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Risk Factors */}
      <div className="card bg-yellow-50 border-yellow-200">
        <h3 className="text-lg font-semibold text-yellow-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          Risk Factors to Monitor
        </h3>
        <ul className="space-y-2">
          {data.risk_factors.map((risk, idx) => (
            <li key={idx} className="flex items-start gap-2 text-yellow-800">
              <span className="text-yellow-600 font-bold mt-0.5">⚠</span>
              <span>{risk}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Action Items */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          Action Items
        </h3>
        <ul className="space-y-2">
          {data.action_items.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2 text-blue-800">
              <input type="checkbox" className="mt-1" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Disclaimer */}
      <div className="card bg-gray-100 border-gray-300">
        <p className="text-xs text-gray-700">
          <strong>⚠️ Disclaimer:</strong> This analysis is generated by AI for
          informational purposes only and should not be construed as financial
          advice. Please consult with a SEBI-registered financial advisor before
          making investment decisions. Past performance does not guarantee future
          results. Data sources: {data.data_sources.join(', ')}
        </p>
      </div>
    </div>
  )
}

export default AnalysisReport
