"""
Lambda Handler for Data Ingestion
Fetches stock data from various sources and stores in S3
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

import boto3
from botocore.exceptions import ClientError

from data_fetchers.nse_fetcher import NSEFetcher
from data_fetchers.news_fetcher import NewsFetcher
from data_fetchers.screener_fetcher import ScreenerFetcher
from utils.helpers import logger

# Environment variables
DATA_LAKE_BUCKET = os.environ.get('DATA_LAKE_BUCKET')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
eventbridge_client = boto3.client('events', region_name=AWS_REGION)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for data ingestion
    
    Event types:
    - scheduled: Regular scheduled ingestion (every 30 min)
    - manual: Manual trigger with specific stock symbols
    """
    logger.info(f"Ingestion started: {json.dumps(event)}")
    
    try:
        # Determine ingestion type
        ingestion_type = event.get('ingestion_type', 'scheduled')
        stock_symbols = event.get('stock_symbols', get_nifty_100_250_symbols())
        
        logger.info(f"Ingestion type: {ingestion_type}, Stocks: {len(stock_symbols)}")
        
        # Initialize fetchers
        nse_fetcher = NSEFetcher()
        news_fetcher = NewsFetcher()
        screener_fetcher = ScreenerFetcher()
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'ingestion_type': ingestion_type,
            'total_stocks': len(stock_symbols),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Fetch data for each stock
        for symbol in stock_symbols:
            try:
                logger.info(f"Processing {symbol}...")
                
                # Fetch stock data
                stock_data = nse_fetcher.fetch_stock_data(symbol)
                
                # Fetch news
                news_data = news_fetcher.fetch_stock_news(symbol)
                
                # Fetch fundamentals
                fundamental_data = screener_fetcher.fetch_fundamentals(symbol)
                
                # Combine data
                combined_data = {
                    'symbol': symbol,
                    'timestamp': datetime.utcnow().isoformat(),
                    'price_data': stock_data,
                    'news': news_data,
                    'fundamentals': fundamental_data
                }
                
                # Store in S3
                s3_key = f"raw/stocks/{symbol}/{datetime.utcnow().strftime('%Y/%m/%d/%H%M%S')}.json"
                
                s3_client.put_object(
                    Bucket=DATA_LAKE_BUCKET,
                    Key=s3_key,
                    Body=json.dumps(combined_data, default=str),
                    ContentType='application/json'
                )
                
                logger.info(f"Stored data for {symbol} at {s3_key}")
                results['successful'] += 1
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                results['failed'] += 1
                results['errors'].append({
                    'symbol': symbol,
                    'error': str(e)
                })
        
        logger.info(f"Ingestion completed: {results['successful']} successful, {results['failed']} failed")
        
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        logger.exception(f"Fatal error in ingestion: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }


def get_nifty_100_250_symbols() -> List[str]:
    """
    Get list of Nifty 100-250 stock symbols
    In production, this should be loaded from a configuration or database
    """
    # Sample list - expand this
    return [
        "TCS", "INFY", "HDFCBANK", "ICICIBANK", "RELIANCE", "HINDUNILVR",
        "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK",
        "WIPRO", "HCLTECH", "ASIANPAINT", "MARUTI", "TITAN", "BAJFINANCE",
        "SUNPHARMA", "ULTRACEMCO", "NESTLEIND", "TECHM", "ONGC", "NTPC"
    ]
