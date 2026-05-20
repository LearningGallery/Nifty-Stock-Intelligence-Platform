import { TrendingUp, Target, AlertOctagon } from 'lucide-react'

function TargetLevels({ shortTermTarget, longTermTarget }) {
  return (
    <div className="space-y-6">
      {/* Short Term */}
      {shortTermTarget && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-primary-600" />
            Short-Term Targets (1-3 months)
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Entry Point</p>
              <p className="text-xl font-bold text-gray-900">
                ₹{shortTermTarget.entry_point?.toFixed(2)}
              </p>
            </div>

            <div className="text-center p-4 bg-success-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Target 1</p>
              <p className="text-xl font-bold text-success-700">
                ₹{shortTermTarget.target_1?.toFixed(2)}
              </p>
              <p className="text-xs text-success-600 mt-1">
                +{shortTermTarget.expected_upside_percent?.toFixed(1)}%
              </p>
            </div>

            {shortTermTarget.target_2 && (
              <div className="text-center p-4 bg-success-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Target 2</p>
                <p className="text-xl font-bold text-success-700">
                  ₹{shortTermTarget.target_2?.toFixed(2)}
                </p>
              </div>
            )}

            <div className="text-center p-4 bg-danger-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Stop Loss</p>
              <p className="text-xl font-bold text-danger-700">
                ₹{shortTermTarget.stop_loss?.toFixed(2)}
              </p>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Risk:Reward</p>
              <p className="text-xl font-bold text-gray-900">
                {shortTermTarget.risk_reward_ratio}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Long Term */}
      {longTermTarget && (
        <div className="card bg-primary-50 border-primary-200">
          <h3 className="text-lg font-semibold text-primary-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Long-Term Target (6-12 months)
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-white rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Entry Range</p>
              <p className="text-lg font-bold text-gray-900">
                ₹{longTermTarget.entry_point?.toFixed(2)}
              </p>
            </div>

            <div className="text-center p-4 bg-success-100 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Target</p>
              <p className="text-lg font-bold text-success-700">
                ₹{longTermTarget.target_1?.toFixed(2)}
              </p>
              <p className="text-xs text-success-600 mt-1">
                +{longTermTarget.expected_upside_percent?.toFixed(1)}%
              </p>
            </div>

            <div className="text-center p-4 bg-danger-100 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Stop Loss</p>
              <p className="text-lg font-bold text-danger-700">
                ₹{longTermTarget.stop_loss?.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TargetLevels
