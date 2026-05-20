"""
Technical Indicator Calculation Helpers
"""
import pandas as pd
import numpy as np
from typing import List, Tuple


def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Calculate Simple Moving Average"""
    df = pd.DataFrame({'close': prices})
    sma = df['close'].rolling(window=period).mean()
    return sma.tolist()


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Calculate Exponential Moving Average"""
    df = pd.DataFrame({'close': prices})
    ema = df['close'].ewm(span=period, adjust=False).mean()
    return ema.tolist()


def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """Calculate Relative Strength Index"""
    df = pd.DataFrame({'close': prices})
    
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.tolist()


def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Tuple[List[float], List[float], List[float]]:
    """
    Calculate MACD
    Returns: (macd_line, signal_line, histogram)
    """
    df = pd.DataFrame({'close': prices})
    
    ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return (
        macd_line.tolist(),
        signal_line.tolist(),
        histogram.tolist()
    )


def calculate_bollinger_bands(
    prices: List[float],
    period: int = 20,
    std_dev: int = 2
) -> Tuple[List[float], List[float], List[float]]:
    """
    Calculate Bollinger Bands
    Returns: (upper_band, middle_band, lower_band)
    """
    df = pd.DataFrame({'close': prices})
    
    middle_band = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return (
        upper_band.tolist(),
        middle_band.tolist(),
        lower_band.tolist()
    )


def find_support_resistance(
    highs: List[float],
    lows: List[float],
    num_levels: int = 3
) -> Tuple[List[float], List[float]]:
    """
    Find support and resistance levels
    Returns: (support_levels, resistance_levels)
    """
    # Simple implementation using local extrema
    highs_arr = np.array(highs)
    lows_arr = np.array(lows)
    
    # Find resistance levels (local maxima)
    resistance_candidates = []
    for i in range(1, len(highs_arr) - 1):
        if highs_arr[i] > highs_arr[i-1] and highs_arr[i] > highs_arr[i+1]:
            resistance_candidates.append(highs_arr[i])
    
    # Find support levels (local minima)
    support_candidates = []
    for i in range(1, len(lows_arr) - 1):
        if lows_arr[i] < lows_arr[i-1] and lows_arr[i] < lows_arr[i+1]:
            support_candidates.append(lows_arr[i])
    
    # Take top N levels
    resistance_levels = sorted(resistance_candidates, reverse=True)[:num_levels]
    support_levels = sorted(support_candidates, reverse=True)[:num_levels]
    
    return (support_levels, resistance_levels)
