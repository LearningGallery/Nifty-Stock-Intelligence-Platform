import { AlertTriangle, Shield } from 'lucide-react'
import clsx from 'clsx'

function RiskMetrics({ riskLevel, riskFactors, confidenceLevel }) {
  const getRiskColor = (level) => {
    switch (level) {
      case 'LOW':
        return 'text-success-600 bg-success-50 border-success-200'
      case 'MODERATE':
        return 'text-warning-600 bg-warning-50 border-warning-200'
      case 'HIGH':
        return 'text-danger-600 bg-danger-50 border-danger-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getConfidenceColor = (level) => {
    switch (level) {
      case 'HIGH':
        return 'text-success-600'
      case 'MEDIUM':
        return 'text-warning-600'
      case 'LOW':
        return 'text-danger-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className={clsx('card border-2', getRiskColor(riskLevel))}>
          <div className="flex items-center gap-3 mb-3">
            <AlertTriangle className="w-6 h-6" />
            <div>
              <p className="text-sm font-medium opacity-75">Risk Level</p>
              <p className="text-2xl font-bold">{riskLevel}</p>
            </div>
          </div>
          <p className="text-sm opacity-75">
            {riskLevel === 'LOW' && 'Lower risk with stable fundamentals'}
            {riskLevel === 'MODERATE' && 'Balanced risk-reward profile'}
            {riskLevel === 'HIGH' && 'Higher volatility, suitable for risk-tolerant investors'}
          </p>
        </div>

        <div className="card border-2 border-primary-200">
          <div className="flex items-center gap-3 mb-3">
            <Shield className="w-6 h-6 text-primary-600" />
            <div>
              <p className="text-sm font-medium text-gray-600">Confidence Level</p>
              <p className={clsx('text-2xl font-bold', getConfidenceColor(confidenceLevel))}>
                {confidenceLevel}
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-600">
            Based on data quality and market conditions
          </p>
        </div>
      </div>

      {riskFactors && riskFactors.length > 0 && (
        <div className="card bg-yellow-50 border-yellow-200">
          <h4 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Risk Factors to Monitor
          </h4>
          <ul className="space-y-2">
            {riskFactors.map((risk, idx) => (
              <li key={idx} className="flex items-start gap-2 text-yellow-800 text-sm">
                <span className="text-yellow-600 font-bold mt-0.5">⚠</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default RiskMetrics
