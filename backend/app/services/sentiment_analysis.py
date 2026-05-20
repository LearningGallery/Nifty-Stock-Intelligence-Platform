"""
Sentiment Analysis Service
Analyzes news and social media sentiment
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import re
from collections import Counter

from app.services.stock_data_service import StockDataService
from app.core.logging import logger


class SentimentAnalysisService:
    """
    News and sentiment analysis service
    """
    
    def __init__(self):
        self.stock_service = StockDataService()
    
    async def analyze(self, stock_symbol: str) -> Dict[str, Any]:
        """
        Perform sentiment analysis on recent news
        """
        try:
            # Get recent news
            news_articles = await self.stock_service.get_recent_news(
                stock_symbol=stock_symbol,
                days=7
            )
            
            if not news_articles:
                logger.warning(f"No news found for {stock_symbol}")
                return self._get_default_analysis()
            
            # Analyze sentiment for each article
            sentiments = []
            positive_signals = []
            negative_signals = []
            
            for article in news_articles:
                sentiment = self._analyze_article_sentiment(article)
                sentiments.append(sentiment)
                
                if sentiment['sentiment'] == 'positive':
                    positive_signals.append(article.get('title', ''))
                elif sentiment['sentiment'] == 'negative':
                    negative_signals.append(article.get('title', ''))
            
            # Calculate overall sentiment
            sentiment_counts = Counter([s['sentiment'] for s in sentiments])
            overall_sentiment = self._determine_overall_sentiment(sentiment_counts)
            
            # Calculate sentiment score
            score = self._calculate_sentiment_score(sentiment_counts, len(news_articles))
            
            # Create summary
            summary = self._create_summary(news_articles, overall_sentiment)
            
            analysis = {
                "score": score,
                "sentiment": overall_sentiment,
                "positive_count": sentiment_counts.get('positive', 0),
                "negative_count": sentiment_counts.get('negative', 0),
                "neutral_count": sentiment_counts.get('neutral', 0),
                "positive_signals": positive_signals[:5],
                "negative_signals": negative_signals[:5],
                "summary": summary,
                "recent_news": [
                    {
                        "title": article.get('title'),
                        "source": article.get('source'),
                        "published_at": article.get('published_at'),
                        "url": article.get('url'),
                        "sentiment": self._analyze_article_sentiment(article)['sentiment']
                    }
                    for article in news_articles[:10]
                ],
                "news_count": len(news_articles),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Sentiment analysis completed for {stock_symbol}")
            return analysis
            
        except Exception as e:
            logger.exception(f"Sentiment analysis error for {stock_symbol}: {e}")
            return self._get_default_analysis()
    
    async def get_latest_sentiment(self, stock_symbol: str) -> Dict[str, Any]:
        """
        Get quick sentiment snapshot
        """
        try:
            analysis = await self.analyze(stock_symbol)
            return {
                "sentiment": analysis.get("sentiment", "neutral"),
                "score": analysis.get("score", 5.0)
            }
        except:
            return {"sentiment": "neutral", "score": 5.0}
    
    def _analyze_article_sentiment(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment of a single article
        Using keyword-based approach (can be enhanced with ML models)
        """
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        # Positive keywords
        positive_keywords = [
            'surge', 'gain', 'profit', 'growth', 'positive', 'upgrade', 'buy',
            'strong', 'rally', 'record', 'high', 'success', 'beat', 'outperform',
            'bullish', 'increase', 'expansion', 'win', 'award', 'innovation',
            'breakthrough', 'partnership', 'contract', 'order', 'dividend'
        ]
        
        # Negative keywords
        negative_keywords = [
            'fall', 'drop', 'loss', 'decline', 'negative', 'downgrade', 'sell',
            'weak', 'crash', 'low', 'failure', 'miss', 'underperform',
            'bearish', 'decrease', 'layoff', 'scandal', 'probe', 'fine',
            'lawsuit', 'concern', 'worry', 'risk', 'warning', 'cut'
        ]
        
        # Count keywords
        positive_count = sum(1 for keyword in positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text)
        
        # Determine sentiment
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(positive_count / (positive_count + negative_count + 1), 1.0)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(negative_count / (positive_count + negative_count + 1), 1.0)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_keywords": positive_count,
            "negative_keywords": negative_count
        }
    
    def _determine_overall_sentiment(self, sentiment_counts: Counter) -> str:
        """
        Determine overall sentiment from counts
        """
        positive = sentiment_counts.get('positive', 0)
        negative = sentiment_counts.get('negative', 0)
        neutral = sentiment_counts.get('neutral', 0)
        
        total = positive + negative + neutral
        if total == 0:
            return "neutral"
        
        positive_ratio = positive / total
        negative_ratio = negative / total
        
        if positive_ratio > 0.6:
            return "Very Positive"
        elif positive_ratio > 0.4:
            return "Positive"
        elif negative_ratio > 0.6:
            return "Very Negative"
        elif negative_ratio > 0.4:
            return "Negative"
        else:
            return "Neutral"
    
    def _calculate_sentiment_score(self, sentiment_counts: Counter, total_articles: int) -> float:
        """
        Calculate sentiment score (0-10)
        """
        if total_articles == 0:
            return 5.0
        
        positive = sentiment_counts.get('positive', 0)
        negative = sentiment_counts.get('negative', 0)
        neutral = sentiment_counts.get('neutral', 0)
        
        # Calculate weighted score
        positive_weight = 2
        neutral_weight = 1
        negative_weight = 0
        
        weighted_sum = (positive * positive_weight + 
                       neutral * neutral_weight + 
                       negative * negative_weight)
        max_possible = total_articles * positive_weight
        
        score = (weighted_sum / max_possible) * 10 if max_possible > 0 else 5.0
        
        return round(score, 1)
    
    def _create_summary(self, news_articles: List[Dict[str, Any]], overall_sentiment: str) -> str:
        """
        Create summary of news sentiment
        """
        if not news_articles:
            return "No recent news available."
        
        latest_article = news_articles[0]
        title = latest_article.get('title', 'Recent developments')
        
        summary = f"Recent news sentiment is {overall_sentiment.lower()}. "
        summary += f"Latest: {title}. "
        summary += f"Total {len(news_articles)} articles analyzed in the last 7 days."
        
        return summary
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """
        Return default analysis when no news is available
        """
        return {
            "score": 5.0,
            "sentiment": "Neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "positive_signals": [],
            "negative_signals": [],
            "summary": "No recent news available for sentiment analysis.",
            "recent_news": [],
            "news_count": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
