import { useState, useEffect, useRef } from 'react'
import { Search, TrendingUp } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { stockAPI } from '@/services/api'

function StockSearchBar({ onSelect, placeholder }) {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const wrapperRef = useRef(null)

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['stockSearch', query],
    queryFn: () => stockAPI.searchStocks(query, 10),
    enabled: query.length >= 2,
    staleTime: 60000,
  })

  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (stock) => {
    setQuery(stock.symbol)
    setIsOpen(false)
    onSelect(stock)
  }

  return (
    <div ref={wrapperRef} className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder || 'Search stocks...'}
          className="input pl-10"
        />
      </div>

      {isOpen && query.length >= 2 && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-gray-500">
              Searching...
            </div>
          ) : searchResults?.data?.length > 0 ? (
            <ul>
              {searchResults.data.map((stock) => (
                <li key={stock.symbol}>
                  <button
                    onClick={() => handleSelect(stock)}
                    className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors flex items-center justify-between"
                  >
                    <div>
                      <div className="font-semibold text-gray-900">
                        {stock.symbol}
                      </div>
                      <div className="text-sm text-gray-600">
                        {stock.name}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-500">
                        {stock.sector}
                      </div>
                      <div className="text-xs text-gray-400">
                        ₹{(stock.market_cap / 100).toFixed(0)}K Cr
                      </div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-4 text-center text-gray-500">
              No stocks found
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default StockSearchBar
