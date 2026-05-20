"""
Stock Data Service
Fetches stock data from external APIs
"""
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.config import settings
from app.core.logging import logger
from app.core.exceptions import StockDataException


class StockDataService:
    """
    Service to fetch stock market data from various sources
    """
    
    def __init__(self):
        self.nifty_100_250_stocks = self._load_stock_universe()
    
    def _load_stock_universe(self) -> List[str]:
        """
        Load list of Nifty 100-250 stocks with market cap > ₹5000 Cr
        """
        # This should be loaded from a configuration file or database
        # For now, returning a sample list
        return [
            "TCS", "INFY", "HDFCBANK", "ICICIBANK", "RELIANCE", "HINDUNILVR",
            "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK",
            "WIPRO", "HCLTECH", "ASIANPAINT", "MARUTI", "TITAN", "BAJFINANCE",
            "SUNPHARMA", "ULTRACEMCO", "NESTLEIND", "TECHM", "ONGC", "NTPC",
            "POWERGRID", "M&M", "TATAMOTORS", "TATASTEEL", "ADANIPORTS",
            "JSWSTEEL", "INDUSINDBK", "BAJAJFINSV", "GRASIM", "DRREDDY",
            "CIPLA", "DIVISLAB", "EICHERMOT", "HEROMOTOCO", "BRITANNIA",
            "COALINDIA", "BPCL", "IOC", "SHREECEM", "UPL", "HINDALCO"
        ]
    
    async def is_valid_symbol(self, symbol: str) -> bool:
        """
        Check if stock symbol is valid and in our universe
        """
        return symbol.upper() in self.nifty_100_250_stocks
    
    async def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search stocks by symbol or name
        """
        query_upper = query.upper()
        
        # Filter matching stocks
        matching_stocks = [
            stock for stock in self.nifty_100_250_stocks
            if query_upper in stock
        ][:limit]
        
        # Fetch details for each
        results = []
        for symbol in matching_stocks:
            try:
                details = await self.get_stock_details(symbol)
                results.append(details)
            except:
                # If fetch fails, add basic info
                results.append({
                    "symbol": symbol,
                    "name": symbol,
                    "sector": "Unknown",
                    "market_cap": 0.0
                })
        
        return results
    
    async def get_stock_details(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic stock details
        """
        # This would call real APIs like NSE, BSE, or Screener.in
        # For demonstration, returning mock data
        
        # In production, use:
        # - NSE API: https://www.nseindia.com/api/quote-equity?symbol={symbol}
        # - BSE API or Yahoo Finance India
        
        company_names = {
            "TCS": "Tata Consultancy Services",
            "INFY": "Infosys Limited",
            "HDFCBANK": "HDFC Bank Limited",
            "RELIANCE": "Reliance Industries Limited",
            # ... add more
        }
        
        return {
            "symbol": symbol,
            "name": company_names.get(symbol, symbol),
            "sector": "Technology",  # Would be fetched from API
            "market_cap": 1250000.0  # In crores
        }
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current price and basic quote data
        """
        try:
            # Mock implementation
            # In production, call NSE API or similar
            
            # Example NSE API call:
            # url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            # async with httpx.AsyncClient() as client:
            #     response = await client.get(url, headers=self._get_nse_headers())
            #     data = response.json()
            
            # Mock data for demonstration
            mock_price = 3450.50
            
            return {
                "symbol": symbol,
                "company_name": f"{symbol} Limited",
                "current_price": mock_price,
                "previous_close": 3420.00,
                "change": 30.50,
                "change_percent": 0.89,
                "open": 3430.00,
                "high": 3475.00,
                "low": 3425.00,
                "volume": 1250000,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise StockDataException(f"Failed to fetch price for {symbol}")
    
    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1M",
        interval: str = "1D"
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data
        """
        try:
            # Parse period
            days = self._parse_period(period)
            
            # Mock implementation
            # In production, use Yahoo Finance India or NSE historical data API
            
            # Generate mock historical data
            historical_data = []
            base_price = 3400.00
            current_date = datetime.utcnow()
            
            for i in range(days):
                date = current_date - timedelta(days=days - i)
                
                # Simulate price movement
                price_change = (i % 10 - 5) * 20  # Random-ish movement
                close_price = base_price + price_change
                
                historical_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": close_price - 10,
                    "high": close_price + 15,
                    "low": close_price - 15,
                    "close": close_price,
                    "volume": 1000000 + (i % 100000)
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Get fundamental data from Screener.in or similar source
        """
        try:
            # Mock implementation
            # In production, scrape Screener.in or use their API if available
            
            # Example Screener.in URL:
            # url = f"https://www.screener.in/api/company/{symbol}/"
            
            return {
                "symbol": symbol,
                "company_name": f"{symbol} Limited",
                "sector": "IT Services",
                "industry": "Software Products",
                "market_cap": 1250000.0,  # In crores
                
                # Valuation
                "pe_ratio": 28.5,
                "pb_ratio": 11.2,
                "ps_ratio": 7.8,
                "peg_ratio": 1.8,
                
                # Profitability
                "roe": 42.3,
                "roa": 28.5,
                "roce": 45.2,
                "net_profit_margin": 19.5,
                "operating_margin": 24.8,
                
                # Growth
                "revenue_growth_yoy": 12.5,
                "eps_growth_yoy": 10.8,
                "profit_growth_yoy": 11.2,
                
                # Financial Health
                "debt_to_equity": 0.05,
                "current_ratio": 2.8,
                "quick_ratio": 2.5,
                "interest_coverage": 45.0,
                
                # Dividend
                "dividend_yield": 1.8,
                "payout_ratio": 35.0,
                
                # Ownership
                "promoter_holding": 72.3,
                "pledged_percentage": 0.0,
                
                # Per Share
                "eps": 121.5,
                "book_value_per_share": 287.0
            }
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return {}
    
    async def get_recent_news(
        self,
        stock_symbol: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get recent news articles for a stock
        """
        try:
            # In production, use NewsAPI or Google News RSS
            # Example NewsAPI call:
            # url = "https://newsapi.org/v2/everything"
            # params = {
            #     "q": f"{stock_symbol} stock OR {company_name}",
            #     "from": (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d"),
            #     "language": "en",
            #     "sortBy": "publishedAt",
            #     "apiKey": settings.NEWS_API_KEY
            # }
            
            # Mock news data
            mock_news = [
                {
                    "title": f"{stock_symbol} reports strong Q3 earnings, beats estimates",
                    "description": f"{stock_symbol} posted impressive quarterly results with revenue growth of 15%.",
                    "source": "Economic Times",
                    "published_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "url": f"https://economictimes.com/{stock_symbol.lower()}-earnings"
                },
                {
                    "title": f"{stock_symbol} announces major contract win in BFSI sector",
                    "description": "Company secures multi-year deal worth $500 million.",
                    "source": "Business Standard",
                    "published_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
                    "url": f"https://business-standard.com/{stock_symbol.lower()}-contract"
                },
                {
                    "title": f"Analysts upgrade {stock_symbol} to 'Buy' with higher target",
                    "description": "Leading brokerage raises target price citing strong fundamentals.",
                    "source": "MoneyControl",
                    "published_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                    "url": f"https://moneycontrol.com/{stock_symbol.lower()}-upgrade"
                }
            ]
            
            return mock_news
            
        except Exception as e:
            logger.error(f"Error fetching news for {stock_symbol}: {e}")
            return []
    
    async def get_trending_stocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending stocks based on volume and activity
        """
        # Mock implementation
        # In production, calculate based on:
        # - Volume breakouts
        # - News frequency
        # - Social media mentions
        # - Price movements
        
        trending = self.nifty_100_250_stocks[:limit]
        
        results = []
        for symbol in trending:
            try:
                price_data = await self.get_current_price(symbol)
                results.append(price_data)
            except:
                pass
        
        return results
    
    def _parse_period(self, period: str) -> int:
        """
        Parse period string to number of days
        """
        period_map = {
            "1D": 1,
            "1W": 7,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365
        }
        return period_map.get(period.upper(), 30)
    
    def _get_nse_headers(self) -> Dict[str, str]:
        """
        Get headers required for NSE API calls
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
