"""
Analysis Result Models
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TechnicalAnalysis(BaseModel):
    """Technical analysis results"""
    score: float = Field(..., ge=0, le=10)
    trend: str
    support_levels: List[float]
    resistance_levels: List[float]
    indicators: Dict[str, Any]
    signals: List[str]


class FundamentalAnalysis(BaseModel):
    """Fundamental analysis results"""
    score: float = Field(..., ge=0, le=10)
    strengths: List[str]
    weaknesses: List[str]
    red_flags: List[str]
    metrics: Dict[str, Any]


class SentimentAnalysis(BaseModel):
    """Sentiment analysis results"""
    score: float = Field(..., ge=0, le=10)
    sentiment: str
    positive_signals: List[str]
    negative_signals: List[str]
    news_count: int


class VolumeAnalysis(BaseModel):
    """Volume-based analysis"""
    current_volume: int
    average_volume: int
    volume_ratio: float
    signal: str
    institutional_activity: str
