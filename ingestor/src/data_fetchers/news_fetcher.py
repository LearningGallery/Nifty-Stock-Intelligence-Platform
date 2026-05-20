"""
News Data Fetcher
"""
import os
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta

from utils.helpers import logger


class NewsFetcher:
    """
    Fetches news articles for stocks
    """
    
    def __init__(self):
        # In production, store API key in Secrets Manager
        self.news_api_key = os.environ.get('NEWS_API_KEY', '')
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch_stock_news(
        self,
        symbol: str,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent news articles for a stock
        """
        try:
            # If no API key, return mock data
            if not self.news_api_key:
                logger.warning("No News API key, returning mock data")
                return self._get_mock_news(symbol)
            
            # Calculate date range
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=days)
            
            # Build query
            query = f"{symbol} stock OR {symbol} shares"
            
            params = {
                'q': query,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Format articles
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'source': article.get('source', {}).get('name'),
                    'published_at': article.get('publishedAt'),
                    'url': article.get('url'),
                    'image_url': article.get('urlToImage')
                })
            
            logger.info(f"Fetched {len(formatted_articles)} news articles for {symbol}")
            return formatted_articles
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return self._get_mock_news(symbol)
    
    def _get_mock_news(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Return mock news data
        """
        return [
            {
                'title': f"{symbol} reports strong quarterly results",
                'description': f"{symbol} posted impressive quarterly results with revenue growth.",
                'source': "Economic Times",
                'published_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'url': f"https://economictimes.com/{symbol.lower()}",
                'image_url': None
            },
            {
                'title': f"{symbol} announces strategic partnership",
                'description': f"{symbol} enters into major partnership deal.",
                'source': "Business Standard",
                'published_at': (datetime.utcnow() - timedelta(days=3)).isoformat(),
                'url': f"https://business-standard.com/{symbol.lower()}",
                'image_url': None
            }
        ]
