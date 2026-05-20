import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Search, TrendingUp, AlertCircle, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useQuery } from '@tanstack/react-query'

import { analysisAPI, stockAPI } from '@/services/api'
import StockSearchBar from '@/components/Analysis/StockSearchBar'
import AnalysisReport from '@/components/Analysis/AnalysisReport'
import QuickStats from '@/components/Analysis/QuickStats'

function AnalysisPage() {
  const { symbol: urlSymbol } = useParams()
  const navigate = useNavigate()
  
  const [selectedStock, setSelectedStock] = useState(urlSymbol || '')
  const [analysisType, setAnalysisType] = useState('comprehensive')
  const [timeframe, setTimeframe] = useState('short_term')

  const {
    data: analysisData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['analysis', selectedStock, analysisType, timeframe],
    queryFn: () =>
      analysisAPI.getComprehensiveAnalysis({
        stock_symbol: selectedStock,
        analysis_type: analysisType,
        timeframe,
      }),
    enabled: !!selectedStock,
    retry: 1,
  })

  useEffect(() => {
    if (urlSymbol && urlSymbol !== selectedStock) {
      setSelectedStock(urlSymbol)
    }
  }, [urlSymbol])

  const handleStockSelect = (stock) => {
    setSelectedStock(stock.symbol)
    navigate(`/analysis/${stock.symbol}`)
  }

  const handleAnalyze = () => {
    if (selectedStock) {
      refetch()
    } else {
      toast.error('Please select a stock to analyze')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Stock Analysis
        </h1>
        <p className="text-gray-600">
          Get comprehensive AI-powered analysis for Nifty 100-250 stocks
        </p>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Stock
            </label>
            <StockSearchBar
              onSelect={handleStockSelect}
              placeholder="Search by symbol or company name (e.g., TCS, Infosys)"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Analysis Type
              </label>
              <select
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value)}
                className="input"
              >
                <option value="comprehensive">Comprehensive</option>
                <option value="technical">Technical Only</option>
                <option value="fundamental">Fundamental Only</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeframe
              </label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="input"
              >
                <option value="short_term">Short Term (1-3 months)</option>
                <option value="medium_term">Medium Term (3-6 months)</option>
                <option value="long_term">Long Term (6-12 months)</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={handleAnalyze}
                disabled={!selectedStock || isLoading}
                className="btn btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5" />
                    Analyze
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      {selectedStock && !isLoading && analysisData && (
        <QuickStats data={analysisData.data} />
      )}

      {/* Error State */}
      {error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-900">
                Analysis Failed
              </h3>
              <p className="text-sm text-red-700 mt-1">
                {error.response?.data?.message || 'Failed to analyze stock. Please try again.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
            <p className="text-gray-600">
              Analyzing {selectedStock}... This may take a few moments.
            </p>
          </div>
        </div>
      )}

      {/* Analysis Report */}
      {!isLoading && analysisData && (
        <AnalysisReport data={analysisData.data} />
      )}

      {/* Empty State */}
      {!selectedStock && !isLoading && (
        <div className="card text-center py-12">
          <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Select a Stock to Analyze
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Search and select a stock from Nifty 100-250 to get comprehensive
            AI-powered analysis with technical, fundamental, and sentiment insights.
          </p>
        </div>
      )}
    </div>
  )
}

export default AnalysisPage
