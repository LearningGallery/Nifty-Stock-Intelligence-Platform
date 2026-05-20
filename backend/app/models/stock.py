"""
Stock Data Models
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


class StockSymbol(BaseModel):
    """Stock symbol model"""
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    

class RecommendationType(str, Enum):
    """Recommendation types"""
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class ConfidenceLevel(str, Enum):
    """Confidence levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class TechnicalSignal(BaseModel):
    """Technical analysis signal"""
    indicator: str
    signal: str
    value: float
    description: str


class TimeframeTarget(BaseModel):
    """Price target for specific timeframe"""
    entry_point: float
    target_1: float
    target_2: Optional[float] = None
    stop_loss: float
    risk_reward_ratio: str
    expected_upside_percent: float


class StockAnalysisRequest(BaseModel):
    """Stock analysis request"""
    stock_symbol: str = Field(..., description="Stock symbol (e.g., TCS, INFY)")
    analysis_type: Optional[str] = Field("comprehensive", description="Type of analysis")
    timeframe: Optional[str] = Field("short_term", description="Analysis timeframe")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stock_symbol": "TCS",
                "analysis_type": "comprehensive",
                "timeframe": "short_term"
            }
        }


class StockAnalysisResponse(BaseModel):
    """Complete stock analysis response"""
    stock_symbol: str
    company_name: str
    sector: str
    market_cap: float
    current_price: float
    
    # Overall recommendation
    recommendation: RecommendationType
    confidence_level: ConfidenceLevel
    risk_level: RiskLevel
    
    # Pros and Cons
    pros: List[str]
    cons: List[str]
    
    # Timeframe targets
    short_term_target: TimeframeTarget
    long_term_target: Optional[TimeframeTarget] = None
    
    # Technical signals
    technical_signals: List[TechnicalSignal]
    technical_score: float = Field(..., ge=0, le=10)
    
    # Fundamental snapshot
    fundamental_data: Dict[str, Any]
    fundamental_score: float = Field(..., ge=0, le=10)
    
    # News & Sentiment
    news_summary: str
    sentiment_score: float = Field(..., ge=0, le=10)
    recent_news: List[Dict[str, Any]]
    
    # Risk factors
    risk_factors: List[str]
    
    # Action items
    action_items: List[str]
    
    # Metadata
    analysis_timestamp: datetime
    data_sources: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "stock_symbol": "TCS",
                "company_name": "Tata Consultancy Services",
                "sector": "IT Services",
                "market_cap": 1250000.0,
                "current_price": 3450.50,
                "recommendation": "BUY",
                "confidence_level": "HIGH",
                "risk_level": "MODERATE",
                "pros": [
                    "Strong Q3 results with 15% YoY growth",
                    "Increasing deal wins in BFSI sector",
                    "Healthy promoter holding at 72%"
                ],
                "cons": [
                    "High P/E ratio compared to peers",
                    "Currency headwinds affecting margins"
                ],
                "short_term_target": {
                    "entry_point": 3450.0,
                    "target_1": 3650.0,
                    "target_2": 3800.0,
                    "stop_loss": 3300.0,
                    "risk_reward_ratio": "1:2.5",
                    "expected_upside_percent": 10.14
                },
                "technical_signals": [
                    {
                        "indicator": "RSI",
                        "signal": "Neutral",
                        "value": 55.0,
                        "description": "RSI at 55, not overbought"
                    }
                ],
                "technical_score": 7.5,
                "fundamental_data": {
                    "pe_ratio": 28.5,
                    "pb_ratio": 11.2,
                    "debt_to_equity": 0.05,
                    "roe": 42.3,
                    "eps_growth_yoy": 12.5
                },
                "fundamental_score": 8.0,
                "news_summary": "TCS reported strong Q3 results...",
                "sentiment_score": 8.5,
                "recent_news": [],
                "risk_factors": [
                    "Global recession concerns",
                    "Client concentration risk"
                ],
                "action_items": [
                    "Monitor Q4 earnings call on Feb 10",
                    "Set price alert at ₹3650"
                ],
                "analysis_timestamp": "2024-01-15T10:30:00Z",
                "data_sources": ["NSE", "Screener.in", "NewsAPI"]
            }
        }
