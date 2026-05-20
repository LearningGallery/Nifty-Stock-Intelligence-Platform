"""
Document Processor
Converts raw stock data into structured documents
"""
from typing import Dict, Any, List
from datetime import datetime
import hashlib


class DocumentProcessor:
    """
    Processes raw stock data into structured documents
    """
    
    def process_stock_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert raw stock data into processable documents
        """
        documents = []
        symbol = raw_data.get('symbol')
        timestamp = raw_data.get('timestamp')
        
        # Process price data
        if raw_data.get('price_data'):
            price_doc = self._create_price_document(
                symbol=symbol,
                price_data=raw_data['price_data'],
                timestamp=timestamp
            )
            documents.append(price_doc)
        
        # Process news articles
        if raw_data.get('news'):
            for article in raw_data['news']:
                news_doc = self._create_news_document(
                    symbol=symbol,
                    article=article,
                    timestamp=timestamp
                )
                documents.append(news_doc)
        
        # Process fundamental data
        if raw_data.get('fundamentals'):
            fundamental_doc = self._create_fundamental_document(
                symbol=symbol,
                fundamentals=raw_data['fundamentals'],
                timestamp=timestamp
            )
            documents.append(fundamental_doc)
        
        return documents
    
    def _create_price_document(
        self,
        symbol: str,
        price_data: Dict[str, Any],
        timestamp: str
    ) -> Dict[str, Any]:
        """
        Create document from price data
        """
        content = f"""
Stock: {symbol}
Current Price: ₹{price_data.get('current_price', 'N/A')}
Change: {price_data.get('change_percent', 'N/A')}%
Open: ₹{price_data.get('open', 'N/A')}
High: ₹{price_data.get('high', 'N/A')}
Low: ₹{price_data.get('low', 'N/A')}
Volume: {price_data.get('volume', 'N/A')}
Last Updated: {timestamp}
"""
        
        return {
            'content': content.strip(),
            'metadata': {
                'type': 'price_data',
                'symbol': symbol,
                'timestamp': timestamp,
                'source': 'NSE'
            }
        }
    
    def _create_news_document(
        self,
        symbol: str,
        article: Dict[str, Any],
        timestamp: str
    ) -> Dict[str, Any]:
        """
        Create document from news article
        """
        content = f"""
Stock: {symbol}
Title: {article.get('title', 'N/A')}
Description: {article.get('description', 'N/A')}
Source: {article.get('source', 'N/A')}
Published: {article.get('published_at', 'N/A')}
"""
        
        return {
            'content': content.strip(),
            'metadata': {
                'type': 'news',
                'symbol': symbol,
                'timestamp': timestamp,
                'source': article.get('source'),
                'url': article.get('url'),
                'published_at': article.get('published_at')
            }
        }
    
    def _create_fundamental_document(
        self,
        symbol: str,
        fundamentals: Dict[str, Any],
        timestamp: str
    ) -> Dict[str, Any]:
        """
        Create document from fundamental data
        """
        content = f"""
Stock: {symbol}
Sector: {fundamentals.get('sector', 'N/A')}
Market Cap: ₹{fundamentals.get('market_cap', 'N/A')} Cr
P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}
P/B Ratio: {fundamentals.get('pb_ratio', 'N/A')}
ROE: {fundamentals.get('roe', 'N/A')}%
Debt/Equity: {fundamentals.get('debt_to_equity', 'N/A')}
Revenue Growth: {fundamentals.get('revenue_growth_yoy', 'N/A')}%
Promoter Holding: {fundamentals.get('promoter_holding', 'N/A')}%
Last Updated: {timestamp}
"""
        
        return {
            'content': content.strip(),
            'metadata': {
                'type': 'fundamental',
                'symbol': symbol,
                'timestamp': timestamp,
                'source': 'Screener.in',
                'sector': fundamentals.get('sector')
            }
        }
