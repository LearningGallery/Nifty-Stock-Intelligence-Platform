import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Search, Filter } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { stockAPI } from '@/services/api'

function ExplorePage() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSector, setSelectedSector] = useState('all')

  const { data: trendingStocks, isLoading } = useQuery({
    queryKey: ['trendingStocks'],
    queryFn: () => stockAPI.getTrending(20),
    staleTime: 300000, // 5 minutes
  })

  const sectors = ['all', 'IT', 'Banking', 'Pharma', 'Auto', 'FMCG', 'Energy']

  const filteredStocks = trendingStocks?.data?.filter((stock) => {
    const matchesSearch =
      stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      stock.company_name?.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesSector =
      selectedSector === 'all' ||
      stock.sector?.toLowerCase() === selectedSector.toLowerCase()

    return matchesSearch && matchesSector
  })

  const handleStockClick = (symbol) => {
    navigate(`/analysis/${symbol}`)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Explore Stocks
        </h1>
        <p className="text-gray-600">
          Discover and analyze trending stocks from Nifty 100-250
        </p>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Stocks
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by symbol or company name..."
                className="input pl-10"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Sector
            </label>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={selectedSector}
                onChange={(e) => setSelectedSector(e.target.value)}
                className="input pl-10"
              >
                {sectors.map((sector) => (
                  <option key={sector} value={sector}>
                    {sector === 'all' ? 'All Sectors' : sector}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Trending Stocks Grid */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">
            Trending Stocks
          </h2>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
                <div className="h-6 bg-gray-200 rounded w-1/2 mb-2" />
                <div className="h-4 bg-gray-200 rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : filteredStocks && filteredStocks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredStocks.map((stock) => (
              <StockCard
                key={stock.symbol}
                stock={stock}
                onClick={() => handleStockClick(stock.symbol)}
              />
            ))}
          </div>
        ) : (
          <div className="card text-center py-12">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              No stocks found matching your criteria
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

function StockCard({ stock, onClick }) {
  const changePercent = stock.change_percent || 0
  const isPositive = changePercent >= 0

  return (
    <button
      onClick={onClick}
      className="card text-left hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{stock.symbol}</h3>
          <p className="text-sm text-gray-600">{stock.company_name}</p>
        </div>
        <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
          {stock.sector || 'N/A'}
        </span>
      </div>

      <div className="flex items-baseline gap-2 mb-2">
        <span className="text-2xl font-bold text-gray-900">
          ₹{stock.current_price?.toFixed(2) || 'N/A'}
        </span>
        <span
          className={`text-sm font-medium ${
            isPositive ? 'text-success-600' : 'text-danger-600'
          }`}
        >
          {isPositive ? '+' : ''}
          {changePercent.toFixed(2)}%
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-gray-600">Volume:</span>
          <span className="ml-1 font-medium text-gray-900">
            {stock.volume ? (stock.volume / 1000000).toFixed(2) + 'M' : 'N/A'}
          </span>
        </div>
        <div>
          <span className="text-gray-600">High:</span>
          <span className="ml-1 font-medium text-gray-900">
            ₹{stock.high?.toFixed(2) || 'N/A'}
          </span>
        </div>
      </div>
    </button>
  )
}

export default ExplorePage
