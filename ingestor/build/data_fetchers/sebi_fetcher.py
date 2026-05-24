"""
SEBI (Securities and Exchange Board of India) Data Fetcher
Fetches regulatory filings, insider trading, and corporate governance data
"""
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
import re

from utils.helpers import logger


class SEBIFetcher:
    """
    Fetches regulatory data from SEBI
    """
    
    # SEBI doesn't have a public API, but data is available through NSE/BSE filings
    NSE_CORPORATE_URL = "https://www.nseindia.com/api/corporates-pit"
    NSE_BOARD_MEETING_URL = "https://www.nseindia.com/api/corporate-board-meetings"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session with NSE (required for cookies)"""
        try:
            self.session.get(
                "https://www.nseindia.com",
                headers=self.headers,
                timeout=10
            )
        except Exception as e:
            logger.warning(f"SEBI session initialization warning: {e}")
    
    def fetch_insider_trading(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch insider trading data (promoter/director buying/selling)
        """
        try:
            url = self.NSE_CORPORATE_URL
            params = {
                'index': 'equities',
                'symbol': symbol
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse insider trading records
            insider_trades = []
            if 'data' in data:
                for trade in data['data']:
                    insider_trades.append({
                        'person_name': trade.get('name'),
                        'person_category': trade.get('personCategory'),
                        'security_type': trade.get('securityType'),
                        'transaction_type': trade.get('acqMode'),
                        'shares': trade.get('befAcqSharesNo'),
                        'transaction_date': trade.get('acqfromDt'),
                        'intimation_date': trade.get('intimDt')
                    })
            
            logger.info(f"Fetched {len(insider_trades)} insider trades for {symbol}")
            return insider_trades
            
        except Exception as e:
            logger.error(f"Error fetching insider trading for {symbol}: {e}")
            return []
    
    def fetch_board_meetings(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch upcoming/recent board meetings
        """
        try:
            url = self.NSE_BOARD_MEETING_URL
            params = {
                'index': 'equities',
                'symbol': symbol
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            meetings = []
            if 'data' in data:
                for meeting in data['data']:
                    meetings.append({
                        'meeting_date': meeting.get('meetingDate'),
                        'purpose': meeting.get('purpose'),
                        'company': meeting.get('company'),
                        'symbol': symbol
                    })
            
            logger.info(f"Fetched {len(meetings)} board meetings for {symbol}")
            return meetings
            
        except Exception as e:
            logger.error(f"Error fetching board meetings for {symbol}: {e}")
            return []
    
    def fetch_corporate_actions(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch corporate actions (dividends, bonus, splits, rights)
        """
        try:
            # NSE corporate actions endpoint
            url = f"https://www.nseindia.com/api/corporates-corporateActions"
            params = {
                'index': 'equities',
                'symbol': symbol
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            actions = {
                'dividends': [],
                'splits': [],
                'bonus': [],
                'rights': []
            }
            
            if 'data' in data:
                for action in data['data']:
                    action_type = action.get('subject', '').lower()
                    
                    if 'dividend' in action_type:
                        actions['dividends'].append({
                            'ex_date': action.get('exDate'),
                            'purpose': action.get('subject'),
                            'details': action.get('details')
                        })
                    elif 'split' in action_type:
                        actions['splits'].append({
                            'ex_date': action.get('exDate'),
                            'purpose': action.get('subject'),
                            'details': action.get('details')
                        })
                    elif 'bonus' in action_type:
                        actions['bonus'].append({
                            'ex_date': action.get('exDate'),
                            'purpose': action.get('subject'),
                            'details': action.get('details')
                        })
                    elif 'rights' in action_type:
                        actions['rights'].append({
                            'ex_date': action.get('exDate'),
                            'purpose': action.get('subject'),
                            'details': action.get('details')
                        })
            
            return actions
            
        except Exception as e:
            logger.error(f"Error fetching corporate actions for {symbol}: {e}")
            return {
                'dividends': [],
                'splits': [],
                'bonus': [],
                'rights': []
            }
    
    def fetch_shareholding_pattern(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch shareholding pattern (promoter, FII, DII, public)
        """
        try:
            url = f"https://www.nseindia.com/api/corporates-shareholding-pattern"
            params = {
                'index': 'equities',
                'symbol': symbol
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse shareholding data
            if 'data' in data and len(data['data']) > 0:
                latest = data['data'][0]
                
                return {
                    'promoter_holding': latest.get('promoterAndPromoterGroup'),
                    'fii_holding': latest.get('fii'),
                    'dii_holding': latest.get('dii'),
                    'public_holding': latest.get('public'),
                    'quarter': latest.get('quarter'),
                    'date': latest.get('date')
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching shareholding pattern for {symbol}: {e}")
            return {}
