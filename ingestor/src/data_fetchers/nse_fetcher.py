"""
NSE Stock Data Fetcher
"""
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import time

from utils.helpers import logger


class NSEFetcher:
    """
    Fetches stock data from NSE India
    """
    
    BASE_URL = "https://www.nseindia.com/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self._initialize_session()
    
    def _initialize_session(self):
        """
        Initialize session with NSE (required for cookies)
        """
        try:
            self.session.get(
                "https://www.nseindia.com",
                headers=self.headers,
                timeout=10
            )
            time.sleep(1)  # Rate limiting
        except Exception as e:
            logger.warning(f"Session initialization warning: {e}")
    
    def fetch_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current stock quote data
        """
        try:
            url = f"{self.BASE_URL}/quote-equity?symbol={symbol}"
            
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant data
            price_info = data.get('priceInfo', {})
            
            return {
                'symbol': symbol,
                'current_price': price_info.get('lastPrice'),
                'previous_close': price_info.get('previousClose'),
                'change': price_info.get('change'),
                'change_percent': price_info.get('pChange'),
                'open': price_info.get('open'),
                'high': price_info.get('intraDayHighLow', {}).get('max'),
                'low': price_info.get('intraDayHighLow', {}).get('min'),
                'volume': price_info.get('totalTradedVolume'),
                'value': price_info.get('totalTradedValue'),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NSE API error for {symbol}: {e}")
            return self._get_mock_data(symbol)
        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol}: {e}")
            return self._get_mock_data(symbol)
    
    def fetch_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime
    ) -> Dict[str, Any]:
        """
        Fetch historical stock data
        """
        try:
            # NSE historical data endpoint
            # Note: This may require additional authentication
            url = f"{self.BASE_URL}/historical/cm/equity"
            
            params = {
                'symbol': symbol,
                'from': from_date.strftime('%d-%m-%Y'),
                'to': to_date.strftime('%d-%m-%Y')
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return {}
    
    def _get_mock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Return mock data when API fails (for development/testing)
        """
        import random
        
        base_price = random.uniform(1000, 5000)
        
        return {
            'symbol': symbol,
            'current_price': round(base_price, 2),
            'previous_close': round(base_price * 0.99, 2),
            'change': round(base_price * 0.01, 2),
            'change_percent': 1.0,
            'open': round(base_price * 0.995, 2),
            'high': round(base_price * 1.02, 2),
            'low': round(base_price * 0.98, 2),
            'volume': random.randint(500000, 5000000),
            'value': round(base_price * random.randint(500000, 5000000), 2),
            'last_updated': datetime.utcnow().isoformat(),
            'mock': True
        }
