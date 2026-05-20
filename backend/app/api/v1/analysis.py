"""
Stock Analysis API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, Dict, Any

from app.models.stock import StockAnalysisRequest, StockAnalysisResponse
from app.services.orchestration import OrchestrationService
from app.core.security import get_optional_user
from app.core.logging import logger

router = APIRouter()


@router.post("/comprehensive", response_model=StockAnalysisResponse)
async def comprehensive_analysis(
    request: StockAnalysisRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
) -> StockAnalysisResponse:
    """
    Get comprehensive stock analysis with AI-powered insights
    
    Includes:
    - Technical analysis with indicators
    - Fundamental analysis with key metrics
    - Sentiment analysis from news
    - Price targets and recommendations
    - Risk assessment
    """
    try:
        logger.info(f"Starting comprehensive analysis for {request.stock_symbol}")
        
        orchestration_service = OrchestrationService()
        
        analysis = await orchestration_service.generate_comprehensive_analysis(
            stock_symbol=request.stock_symbol,
            analysis_type=request.analysis_type,
            timeframe=request.timeframe
        )
        
        logger.info(f"Completed analysis for {request.stock_symbol}")
        
        return analysis
        
    except Exception as e:
        logger.exception(f"Error in comprehensive analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze {request.stock_symbol}"
        )


@router.get("/{symbol}/quick")
async def quick_analysis(
    symbol: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get quick analysis snapshot (cached for 5 minutes)
    
    Returns: Basic recommendation, current price, and key signals
    """
    try:
        orchestration_service = OrchestrationService()
        
        quick_data = await orchestration_service.get_quick_analysis(symbol)
        
        return quick_data
        
    except Exception as e:
        logger.exception(f"Error in quick analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quick analysis for {symbol}"
        )
