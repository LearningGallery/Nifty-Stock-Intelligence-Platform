import { CheckCircle, XCircle } from 'lucide-react'

function ProsConsCard({ pros, cons }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="card bg-success-50 border-success-200">
        <h3 className="text-lg font-semibold text-success-900 mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5" />
          Strengths & Opportunities
        </h3>
        <ul className="space-y-2">
          {pros.map((pro, idx) => (
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
          {cons.map((con, idx) => (
            <li key={idx} className="flex items-start gap-2 text-danger-800">
              <span className="text-danger-600 font-bold mt-0.5">•</span>
              <span>{con}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default ProsConsCard
