"""
BSE (Bombay Stock Exchange) Data Fetcher
"""
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import time

from utils.helpers import logger


class BSEFetcher:
    """
    Fetches stock data from BSE India
    """
    
    BASE_URL = "https://api.bseindia.com/BseIndiaAPI/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
    
    def fetch_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """
        Fetch current stock quote data from BSE
        
        Args:
            stock_code: BSE stock code (e.g., "532540" for TCS)
        """
        try:
            url = f"{self.BASE_URL}/StockReachGraph/w"
            params = {
                'scripcode': stock_code,
                'flag': 'all',
                'fromdate': '',
                'todate': '',
                'seriesid': ''
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse BSE response format
            if data and 'Data' in data:
                latest = data['Data'][-1] if data['Data'] else {}
                
                return {
                    'stock_code': stock_code,
                    'current_price': latest.get('Close'),
                    'open': latest.get('Open'),
                    'high': latest.get('High'),
                    'low': latest.get('Low'),
                    'volume': latest.get('Volume'),
                    'last_updated': datetime.utcnow().isoformat(),
                    'exchange': 'BSE'
                }
            
            return self._get_mock_data(stock_code)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"BSE API error for {stock_code}: {e}")
            return self._get_mock_data(stock_code)
        except Exception as e:
            logger.error(f"Unexpected error fetching BSE data for {stock_code}: {e}")
            return self._get_mock_data(stock_code)
    
    def fetch_corporate_actions(self, stock_code: str) -> Dict[str, Any]:
        """
        Fetch corporate actions (dividends, splits, bonuses)
        """
        try:
            url = f"{self.BASE_URL}/CorporateAnnouncement/w"
            params = {
                'scripcode': stock_code,
                'fromdate': '',
                'todate': '',
                'strCat': '-1'
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
            logger.error(f"Error fetching BSE corporate actions for {stock_code}: {e}")
            return {}
    
    def _get_mock_data(self, stock_code: str) -> Dict[str, Any]:
        """Return mock data when API fails"""
        import random
        
        base_price = random.uniform(1000, 5000)
        
        return {
            'stock_code': stock_code,
            'current_price': round(base_price, 2),
            'open': round(base_price * 0.995, 2),
            'high': round(base_price * 1.02, 2),
            'low': round(base_price * 0.98, 2),
            'volume': random.randint(500000, 5000000),
            'last_updated': datetime.utcnow().isoformat(),
            'exchange': 'BSE',
            'mock': True
        }
