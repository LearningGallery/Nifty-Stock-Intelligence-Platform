"""
Stock Data API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.stock import StockSymbol
from app.services.stock_data_service import StockDataService
from app.core.logging import logger

router = APIRouter()


@router.get("/search", response_model=List[StockSymbol])
async def search_stocks(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
) -> List[StockSymbol]:
    """
    Search for stocks by symbol or company name
    
    Examples:
    - /stocks/search?query=TCS
    - /stocks/search?query=Tata&limit=5
    """
    try:
        stock_service = StockDataService()
        results = await stock_service.search_stocks(query, limit)
        
        return results
        
    except Exception as e:
        logger.exception(f"Error searching stocks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search stocks"
        )


@router.get("/{symbol}/price")
async def get_stock_price(symbol: str):
    """
    Get current price and basic info for a stock
    
    Example: /stocks/TCS/price
    """
    try:
        stock_service = StockDataService()
        price_data = await stock_service.get_current_price(symbol)
        
        if not price_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock {symbol} not found"
            )
        
        return price_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting stock price: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stock price"
        )


@router.get("/{symbol}/historical")
async def get_historical_data(
    symbol: str,
    period: str = Query("1M", description="Period (1D, 1W, 1M, 3M, 6M, 1Y)"),
    interval: str = Query("1D", description="Interval (1m, 5m, 15m, 1H, 1D)")
):
    """
    Get historical price data for a stock
    
    Example: /stocks/TCS/historical?period=3M&interval=1D
    """
    try:
        stock_service = StockDataService()
        historical_data = await stock_service.get_historical_data(
            symbol=symbol,
            period=period,
            interval=interval
        )
        
        return historical_data
        
    except Exception as e:
        logger.exception(f"Error getting historical data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve historical data"
        )


@router.get("/{symbol}/fundamentals")
async def get_fundamentals(symbol: str):
    """
    Get fundamental data for a stock
    
    Example: /stocks/TCS/fundamentals
    """
    try:
        stock_service = StockDataService()
        fundamentals = await stock_service.get_fundamentals(symbol)
        
        if not fundamentals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fundamental data for {symbol} not found"
            )
        
        return fundamentals
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting fundamentals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve fundamental data"
        )


@router.get("/trending")
async def get_trending_stocks(limit: int = Query(10, ge=1, le=50)):
    """
    Get trending stocks based on volume and news activity
    
    Example: /stocks/trending?limit=10
    """
    try:
        stock_service = StockDataService()
        trending = await stock_service.get_trending_stocks(limit)
        
        return trending
        
    except Exception as e:
        logger.exception(f"Error getting trending stocks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trending stocks"
        )
