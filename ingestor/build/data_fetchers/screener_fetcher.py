"""
Screener.in Fundamental Data Fetcher
"""
import requests
from typing import Dict, Any
from datetime import datetime

from utils.helpers import logger


class ScreenerFetcher:
    """
    Fetches fundamental data from Screener.in
    """
    
    BASE_URL = "https://www.screener.in"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch fundamental data for a stock
        
        Note: Screener.in doesn't have an official API, so this uses web scraping
        In production, use a proper financial data API or service
        """
        try:
            # For now, return mock data
            # In production, implement proper scraping or use paid APIs
            return self._get_mock_fundamentals(symbol)
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return self._get_mock_fundamentals(symbol)
    
    def _get_mock_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Return mock fundamental data
        """
        import random
        
        return {
            'symbol': symbol,
            'sector': 'Technology',
            'industry': 'IT Services',
            'market_cap': round(random.uniform(50000, 200000), 2),
            'pe_ratio': round(random.uniform(15, 40), 2),
            'pb_ratio': round(random.uniform(5, 15), 2),
            'dividend_yield': round(random.uniform(0.5, 3.0), 2),
            'roe': round(random.uniform(15, 45), 2),
            'debt_to_equity': round(random.uniform(0, 1.5), 2),
            'current_ratio': round(random.uniform(1.0, 3.0), 2),
            'promoter_holding': round(random.uniform(50, 75), 2),
            'revenue_growth_yoy': round(random.uniform(5, 25), 2),
            'profit_growth_yoy': round(random.uniform(5, 25), 2),
            'last_updated': datetime.utcnow().isoformat(),
            'mock': True
        }
