import { useQuery } from '@tanstack/react-query'
import { stockAPI } from '@/services/api'

export function useStockData(symbol) {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => stockAPI.getStockPrice(symbol),
    enabled: !!symbol,
    staleTime: 60000, // 1 minute
    refetchInterval: 300000 // 5 minutes
  })
}

export function useStockSearch(query) {
  return useQuery({
    queryKey: ['stockSearch', query],
    queryFn: () => stockAPI.searchStocks(query),
    enabled: query.length >= 2,
    staleTime: 300000 // 5 minutes
  })
}

export function useHistoricalData(symbol, period = '1M', interval = '1D') {
  return useQuery({
    queryKey: ['historicalData', symbol, period, interval],
    queryFn: () => stockAPI.getHistoricalData(symbol, period, interval),
    enabled: !!symbol,
    staleTime: 600000 // 10 minutes
  })
}

export function useFundamentals(symbol) {
  return useQuery({
    queryKey: ['fundamentals', symbol],
    queryFn: () => stockAPI.getFundamentals(symbol),
    enabled: !!symbol,
    staleTime: 3600000 // 1 hour
  })
}
