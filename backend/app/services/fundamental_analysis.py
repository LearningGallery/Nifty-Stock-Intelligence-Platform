"""
Fundamental Analysis Service
Analyzes company financials and metrics
"""
from typing import Dict, Any, List
from datetime import datetime

from app.services.stock_data_service import StockDataService
from app.core.logging import logger


class FundamentalAnalysisService:
    """
    Fundamental analysis with financial metrics evaluation
    """
    
    def __init__(self):
        self.stock_service = StockDataService()
    
    async def analyze(self, stock_symbol: str) -> Dict[str, Any]:
        """
        Perform comprehensive fundamental analysis
        """
        try:
            # Get fundamental data
            fundamentals = await self.stock_service.get_fundamentals(stock_symbol)
            
            if not fundamentals:
                logger.warning(f"No fundamental data for {stock_symbol}")
                return self._get_default_analysis()
            
            # Extract key metrics
            metrics = self._extract_metrics(fundamentals)
            
            # Evaluate metrics
            strengths = self._identify_strengths(metrics)
            weaknesses = self._identify_weaknesses(metrics)
            red_flags = self._identify_red_flags(metrics)
            
            # Calculate fundamental score
            score = self._calculate_fundamental_score(metrics, strengths, weaknesses, red_flags)
            
            analysis = {
                "score": score,
                "metrics": metrics,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "red_flags": red_flags,
                "sector": fundamentals.get("sector", "Unknown"),
                "industry": fundamentals.get("industry", "Unknown"),
                "market_cap": fundamentals.get("market_cap", 0.0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Fundamental analysis completed for {stock_symbol}")
            return analysis
            
        except Exception as e:
            logger.exception(f"Fundamental analysis error for {stock_symbol}: {e}")
            return self._get_default_analysis()
    
    def _extract_metrics(self, fundamentals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize key financial metrics
        """
        return {
            # Valuation
            "pe_ratio": fundamentals.get("pe_ratio", 0.0),
            "pb_ratio": fundamentals.get("pb_ratio", 0.0),
            "ps_ratio": fundamentals.get("ps_ratio", 0.0),
            "peg_ratio": fundamentals.get("peg_ratio", 0.0),
            
            # Profitability
            "roe": fundamentals.get("roe", 0.0),
            "roa": fundamentals.get("roa", 0.0),
            "roce": fundamentals.get("roce", 0.0),
            "net_profit_margin": fundamentals.get("net_profit_margin", 0.0),
            "operating_margin": fundamentals.get("operating_margin", 0.0),
            
            # Growth
            "revenue_growth_yoy": fundamentals.get("revenue_growth_yoy", 0.0),
            "eps_growth_yoy": fundamentals.get("eps_growth_yoy", 0.0),
            "profit_growth_yoy": fundamentals.get("profit_growth_yoy", 0.0),
            
            # Financial Health
            "debt_to_equity": fundamentals.get("debt_to_equity", 0.0),
            "current_ratio": fundamentals.get("current_ratio", 0.0),
            "quick_ratio": fundamentals.get("quick_ratio", 0.0),
            "interest_coverage": fundamentals.get("interest_coverage", 0.0),
            
            # Dividend
            "dividend_yield": fundamentals.get("dividend_yield", 0.0),
            "payout_ratio": fundamentals.get("payout_ratio", 0.0),
            
            # Ownership
            "promoter_holding": fundamentals.get("promoter_holding", 0.0),
            "pledged_percentage": fundamentals.get("pledged_percentage", 0.0),
            
            # Per Share
            "eps": fundamentals.get("eps", 0.0),
            "book_value_per_share": fundamentals.get("book_value_per_share", 0.0)
        }
    
    def _identify_strengths(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Identify fundamental strengths
        """
        strengths = []
        
        # High ROE
        if metrics.get("roe", 0) > 20:
            strengths.append(f"Strong ROE of {metrics['roe']:.1f}% (>20%)")
        
        # Low debt
        if 0 <= metrics.get("debt_to_equity", 0) < 0.5:
            strengths.append(f"Low Debt-to-Equity ratio of {metrics['debt_to_equity']:.2f}")
        
        # High promoter holding
        if metrics.get("promoter_holding", 0) > 70:
            strengths.append(f"Strong promoter holding at {metrics['promoter_holding']:.1f}%")
        
        # Revenue growth
        if metrics.get("revenue_growth_yoy", 0) > 15:
            strengths.append(f"Strong revenue growth of {metrics['revenue_growth_yoy']:.1f}% YoY")
        
        # Profit margin
        if metrics.get("net_profit_margin", 0) > 15:
            strengths.append(f"Healthy profit margin of {metrics['net_profit_margin']:.1f}%")
        
        # Current ratio
        if metrics.get("current_ratio", 0) > 1.5:
            strengths.append(f"Strong liquidity with current ratio of {metrics['current_ratio']:.2f}")
        
        # Dividend yield
        if metrics.get("dividend_yield", 0) > 2:
            strengths.append(f"Attractive dividend yield of {metrics['dividend_yield']:.2f}%")
        
        return strengths[:5]  # Top 5
    
    def _identify_weaknesses(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Identify fundamental weaknesses
        """
        weaknesses = []
        
        # High P/E
        if metrics.get("pe_ratio", 0) > 40:
            weaknesses.append(f"High P/E ratio of {metrics['pe_ratio']:.1f} (>40)")
        
        # Low ROE
        if 0 < metrics.get("roe", 0) < 10:
            weaknesses.append(f"Low ROE of {metrics['roe']:.1f}% (<10%)")
        
        # High debt
        if metrics.get("debt_to_equity", 0) > 2:
            weaknesses.append(f"High Debt-to-Equity of {metrics['debt_to_equity']:.2f}")
        
        # Negative growth
        if metrics.get("revenue_growth_yoy", 0) < 0:
            weaknesses.append(f"Revenue decline of {metrics['revenue_growth_yoy']:.1f}% YoY")
        
        # Low promoter holding
        if 0 < metrics.get("promoter_holding", 0) < 40:
            weaknesses.append(f"Low promoter holding at {metrics['promoter_holding']:.1f}%")
        
        # Poor liquidity
        if 0 < metrics.get("current_ratio", 0) < 1:
            weaknesses.append(f"Poor liquidity with current ratio of {metrics['current_ratio']:.2f}")
        
        return weaknesses[:5]  # Top 5
    
    def _identify_red_flags(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Identify critical red flags
        """
        red_flags = []
        
        # High pledged shares
        if metrics.get("pledged_percentage", 0) > 50:
            red_flags.append(f"High promoter pledge at {metrics['pledged_percentage']:.1f}%")
        
        # Very high debt
        if metrics.get("debt_to_equity", 0) > 3:
            red_flags.append("Very high debt levels (Debt/Equity > 3)")
        
        # Negative ROE
        if metrics.get("roe", 0) < 0:
            red_flags.append("Negative Return on Equity")
        
        # Current ratio below 0.5
        if 0 < metrics.get("current_ratio", 0) < 0.5:
            red_flags.append("Critical liquidity crisis (Current Ratio < 0.5)")
        
        # Continuous losses
        if metrics.get("net_profit_margin", 0) < -10:
            red_flags.append("Heavy losses with negative margins")
        
        return red_flags
    
    def _calculate_fundamental_score(
        self,
        metrics: Dict[str, Any],
        strengths: List[str],
        weaknesses: List[str],
        red_flags: List[str]
    ) -> float:
        """
        Calculate overall fundamental score (0-10)
        """
        score = 5.0  # Start neutral
        
        # Add for strengths
        score += len(strengths) * 0.5
        
        # Subtract for weaknesses
        score -= len(weaknesses) * 0.3
        
        # Subtract heavily for red flags
        score -= len(red_flags) * 1.0
        
        # Bonus for exceptional metrics
        if metrics.get("roe", 0) > 30:
            score += 1
        if metrics.get("revenue_growth_yoy", 0) > 25:
            score += 1
        if metrics.get("debt_to_equity", 0) < 0.2:
            score += 0.5
        
        # Clamp between 0 and 10
        return max(0.0, min(10.0, score))
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """
        Return default analysis when data is unavailable
        """
        return {
            "score": 5.0,
            "metrics": {},
            "strengths": [],
            "weaknesses": [],
            "red_flags": [],
            "sector": "Unknown",
            "industry": "Unknown",
            "market_cap": 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }
