function TechnicalIndicators({ indicators }) {
  if (!indicators) {
    return null
  }

  const getRSIColor = (rsi) => {
    if (rsi > 70) return 'text-danger-600'
    if (rsi < 30) return 'text-success-600'
    return 'text-gray-900'
  }

  const getMACDSignal = () => {
    if (!indicators.macd || !indicators.macd_signal) return 'Neutral'
    return indicators.macd > indicators.macd_signal ? 'Bullish' : 'Bearish'
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600 mb-1">RSI (14)</p>
        <p className={`text-lg font-bold ${getRSIColor(indicators.rsi)}`}>
          {indicators.rsi?.toFixed(2) || 'N/A'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {indicators.rsi > 70 ? 'Overbought' : indicators.rsi < 30 ? 'Oversold' : 'Neutral'}
        </p>
      </div>

      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600 mb-1">MACD</p>
        <p className="text-lg font-bold text-gray-900">
          {indicators.macd?.toFixed(2) || 'N/A'}
        </p>
        <p className="text-xs text-gray-500 mt-1">{getMACDSignal()}</p>
      </div>

      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600 mb-1">SMA (50)</p>
        <p className="text-lg font-bold text-gray-900">
          ₹{indicators.sma_50?.toFixed(2) || 'N/A'}
        </p>
      </div>

      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600 mb-1">SMA (200)</p>
        <p className="text-lg font-bold text-gray-900">
          ₹{indicators.sma_200?.toFixed(2) || 'N/A'}
        </p>
      </div>
    </div>
  )
}

export default TechnicalIndicators
