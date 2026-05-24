"""
Technical Analysis Service
Calculates technical indicators and generates signals
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas_ta_classic as ta

from app.services.stock_data_service import StockDataService
from app.core.logging import logger


class TechnicalAnalysisService:
    """
    Technical analysis with indicators and pattern recognition
    """
    
    def __init__(self):
        self.stock_service = StockDataService()
    
    async def analyze(self, stock_symbol: str) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis
        """
        try:
            # Get historical data (1 year daily)
            historical_data = await self.stock_service.get_historical_data(
                symbol=stock_symbol,
                period="1Y",
                interval="1D"
            )
            
            if not historical_data or len(historical_data) < 50:
                logger.warning(f"Insufficient data for {stock_symbol}")
                return self._get_default_analysis()
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.set_index('date', inplace=True)
            
            # Calculate all indicators
            indicators = await self._calculate_indicators(df)
            
            # Generate signals
            signals = self._generate_signals(df, indicators)
            
            # Calculate support and resistance
            support_resistance = self._calculate_support_resistance(df)
            
            # Determine overall trend
            trend = self._determine_trend(df, indicators)
            
            # Calculate technical score
            score = self._calculate_technical_score(signals, indicators, trend)
            
            analysis = {
                "score": score,
                "trend": trend,
                "support_levels": support_resistance["support"],
                "resistance_levels": support_resistance["resistance"],
                "indicators": indicators,
                "signals": signals,
                "crossovers": self._detect_crossovers(df, indicators),
                "patterns": self._detect_patterns(df),
                "volume_analysis": self._analyze_volume(df),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Technical analysis completed for {stock_symbol}")
            return analysis
            
        except Exception as e:
            logger.exception(f"Technical analysis error for {stock_symbol}: {e}")
            return self._get_default_analysis()
    
    async def get_simple_signal(self, stock_symbol: str) -> str:
        """
        Get simple bullish/bearish/neutral signal
        """
        try:
            analysis = await self.analyze(stock_symbol)
            score = analysis.get("score", 5.0)
            
            if score >= 7:
                return "bullish"
            elif score <= 3:
                return "bearish"
            else:
                return "neutral"
        except:
            return "neutral"
    
    async def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all technical indicators
        """
        indicators = {}
        
        # Moving Averages
        df['SMA_20'] = ta.sma(df['close'], length=20)
        df['SMA_50'] = ta.sma(df['close'], length=50)
        df['SMA_200'] = ta.sma(df['close'], length=200)
        df['EMA_12'] = ta.ema(df['close'], length=12)
        df['EMA_26'] = ta.ema(df['close'], length=26)
        
        indicators['sma_20'] = float(df['SMA_20'].iloc[-1]) if not pd.isna(df['SMA_20'].iloc[-1]) else None
        indicators['sma_50'] = float(df['SMA_50'].iloc[-1]) if not pd.isna(df['SMA_50'].iloc[-1]) else None
        indicators['sma_200'] = float(df['SMA_200'].iloc[-1]) if not pd.isna(df['SMA_200'].iloc[-1]) else None
        
        # RSI
        df['RSI'] = ta.rsi(df['close'], length=14)
        indicators['rsi'] = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
        
        # MACD
        macd = ta.macd(df['close'])
        if macd is not None and not macd.empty:
            df = pd.concat([df, macd], axis=1)
            indicators['macd'] = float(df['MACD_12_26_9'].iloc[-1]) if 'MACD_12_26_9' in df.columns else 0.0
            indicators['macd_signal'] = float(df['MACDs_12_26_9'].iloc[-1]) if 'MACDs_12_26_9' in df.columns else 0.0
            indicators['macd_histogram'] = float(df['MACDh_12_26_9'].iloc[-1]) if 'MACDh_12_26_9' in df.columns else 0.0
        
        # Bollinger Bands
        bbands = ta.bbands(df['close'], length=20, std=2)
        if bbands is not None and not bbands.empty:
            df = pd.concat([df, bbands], axis=1)
            indicators['bb_upper'] = float(df['BBU_20_2.0'].iloc[-1]) if 'BBU_20_2.0' in df.columns else None
            indicators['bb_middle'] = float(df['BBM_20_2.0'].iloc[-1]) if 'BBM_20_2.0' in df.columns else None
            indicators['bb_lower'] = float(df['BBL_20_2.0'].iloc[-1]) if 'BBL_20_2.0' in df.columns else None
        
        # Stochastic Oscillator
        stoch = ta.stoch(df['high'], df['low'], df['close'])
        if stoch is not None and not stoch.empty:
            df = pd.concat([df, stoch], axis=1)
            indicators['stoch_k'] = float(df['STOCHk_14_3_3'].iloc[-1]) if 'STOCHk_14_3_3' in df.columns else 50.0
            indicators['stoch_d'] = float(df['STOCHd_14_3_3'].iloc[-1]) if 'STOCHd_14_3_3' in df.columns else 50.0
        
        # ATR (Average True Range)
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        indicators['atr'] = float(df['ATR'].iloc[-1]) if not pd.isna(df['ATR'].iloc[-1]) else None
        
        # ADX (Average Directional Index)
        adx = ta.adx(df['high'], df['low'], df['close'], length=14)
        if adx is not None and not adx.empty:
            df = pd.concat([df, adx], axis=1)
            indicators['adx'] = float(df['ADX_14'].iloc[-1]) if 'ADX_14' in df.columns else None
        
        # OBV (On Balance Volume)
        df['OBV'] = ta.obv(df['close'], df['volume'])
        indicators['obv'] = float(df['OBV'].iloc[-1]) if not pd.isna(df['OBV'].iloc[-1]) else None
        
        # Current price
        indicators['current_price'] = float(df['close'].iloc[-1])
        
        return indicators
    
    def _generate_signals(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, Any]
    ) -> List[str]:
        """
        Generate trading signals based on indicators
        """
        signals = []
        current_price = indicators.get('current_price', 0)
        
        # RSI signals
        rsi = indicators.get('rsi', 50)
        if rsi > 70:
            signals.append("RSI Overbought (>70)")
        elif rsi < 30:
            signals.append("RSI Oversold (<30)")
        else:
            signals.append(f"RSI Neutral ({rsi:.1f})")
        
        # MACD signals
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd > macd_signal:
            signals.append("MACD Bullish Crossover")
        elif macd < macd_signal:
            signals.append("MACD Bearish Crossover")
        
        # Moving Average signals
        sma_20 = indicators.get('sma_20')
        sma_50 = indicators.get('sma_50')
        sma_200 = indicators.get('sma_200')
        
        if sma_20 and sma_50:
            if current_price > sma_20 > sma_50:
                signals.append("Price above SMA 20 & 50 (Bullish)")
            elif current_price < sma_20 < sma_50:
                signals.append("Price below SMA 20 & 50 (Bearish)")
        
        if sma_200:
            if current_price > sma_200:
                signals.append("Price above 200 SMA (Long-term Bullish)")
            else:
                signals.append("Price below 200 SMA (Long-term Bearish)")
        
        # Bollinger Bands
        bb_upper = indicators.get('bb_upper')
        bb_lower = indicators.get('bb_lower')
        if bb_upper and bb_lower:
            if current_price >= bb_upper:
                signals.append("Price at Upper Bollinger Band (Overbought)")
            elif current_price <= bb_lower:
                signals.append("Price at Lower Bollinger Band (Oversold)")
        
        # Stochastic
        stoch_k = indicators.get('stoch_k', 50)
        if stoch_k > 80:
            signals.append("Stochastic Overbought")
        elif stoch_k < 20:
            signals.append("Stochastic Oversold")
        
        return signals
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """
        Calculate support and resistance levels using pivot points
        """
        # Get recent high, low, close
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        recent_close = df['close'].iloc[-1]
        
        # Calculate pivot point
        pivot = (recent_high + recent_low + recent_close) / 3
        
        # Calculate support and resistance levels
        r1 = 2 * pivot - recent_low
        r2 = pivot + (recent_high - recent_low)
        r3 = recent_high + 2 * (pivot - recent_low)
        
        s1 = 2 * pivot - recent_high
        s2 = pivot - (recent_high - recent_low)
        s3 = recent_low - 2 * (recent_high - pivot)
        
        return {
            "support": sorted([float(s3), float(s2), float(s1)], reverse=True),
            "resistance": sorted([float(r1), float(r2), float(r3)])
        }
    
    def _determine_trend(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, Any]
    ) -> str:
        """
        Determine overall trend
        """
        current_price = indicators.get('current_price', 0)
        sma_20 = indicators.get('sma_20')
        sma_50 = indicators.get('sma_50')
        sma_200 = indicators.get('sma_200')
        
        bullish_signals = 0
        bearish_signals = 0
        
        # Check moving averages
        if sma_20 and current_price > sma_20:
            bullish_signals += 1
        elif sma_20 and current_price < sma_20:
            bearish_signals += 1
        
        if sma_50 and current_price > sma_50:
            bullish_signals += 1
        elif sma_50 and current_price < sma_50:
            bearish_signals += 1
        
        if sma_200 and current_price > sma_200:
            bullish_signals += 2  # More weight
        elif sma_200 and current_price < sma_200:
            bearish_signals += 2
        
        # Check MACD
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd > macd_signal:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # Determine trend
        if bullish_signals > bearish_signals + 1:
            return "Strong Uptrend"
        elif bullish_signals > bearish_signals:
            return "Weak Uptrend"
        elif bearish_signals > bullish_signals + 1:
            return "Strong Downtrend"
        elif bearish_signals > bullish_signals:
            return "Weak Downtrend"
        else:
            return "Sideways"
    
    def _calculate_technical_score(
        self,
        signals: List[str],
        indicators: Dict[str, Any],
        trend: str
    ) -> float:
        """
        Calculate overall technical score (0-10)
        """
        score = 5.0  # Start neutral
        
        # RSI contribution
        rsi = indicators.get('rsi', 50)
        if 40 <= rsi <= 60:
            score += 1
        elif rsi < 30:
            score += 1.5  # Oversold - potential buy
        elif rsi > 70:
            score -= 1.5  # Overbought
        
        # MACD contribution
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd > macd_signal:
            score += 1
        else:
            score -= 1
        
        # Trend contribution
        if "Strong Uptrend" in trend:
            score += 2
        elif "Weak Uptrend" in trend:
            score += 1
        elif "Strong Downtrend" in trend:
            score -= 2
        elif "Weak Downtrend" in trend:
            score -= 1
        
        # MA alignment
        current_price = indicators.get('current_price', 0)
        sma_50 = indicators.get('sma_50')
        sma_200 = indicators.get('sma_200')
        
        if sma_50 and sma_200:
            if current_price > sma_50 > sma_200:
                score += 1.5  # Golden alignment
            elif current_price < sma_50 < sma_200:
                score -= 1.5  # Bearish alignment
        
        # Clamp between 0 and 10
        return max(0.0, min(10.0, score))
    
    def _detect_crossovers(
        self,
        df: pd.DataFrame,
        indicators: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Detect recent crossovers
        """
        crossovers = []
        
        # Check if we have enough data
        if len(df) < 3:
            return crossovers
        
        # MACD crossover
        if 'MACD_12_26_9' in df.columns and 'MACDs_12_26_9' in df.columns:
            macd_current = df['MACD_12_26_9'].iloc[-1]
            macd_prev = df['MACD_12_26_9'].iloc[-2]
            signal_current = df['MACDs_12_26_9'].iloc[-1]
            signal_prev = df['MACDs_12_26_9'].iloc[-2]
            
            if macd_prev < signal_prev and macd_current > signal_current:
                crossovers.append({
                    "type": "MACD Bullish Crossover",
                    "description": "MACD line crossed above signal line"
                })
            elif macd_prev > signal_prev and macd_current < signal_current:
                crossovers.append({
                    "type": "MACD Bearish Crossover",
                    "description": "MACD line crossed below signal line"
                })
        
        # Golden Cross / Death Cross
        if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
            sma50_current = df['SMA_50'].iloc[-1]
            sma50_prev = df['SMA_50'].iloc[-2]
            sma200_current = df['SMA_200'].iloc[-1]
            sma200_prev = df['SMA_200'].iloc[-2]
            
            if not pd.isna(sma50_current) and not pd.isna(sma200_current):
                if sma50_prev < sma200_prev and sma50_current > sma200_current:
                    crossovers.append({
                        "type": "Golden Cross",
                        "description": "50 SMA crossed above 200 SMA (Very Bullish)"
                    })
                elif sma50_prev > sma200_prev and sma50_current < sma200_current:
                    crossovers.append({
                        "type": "Death Cross",
                        "description": "50 SMA crossed below 200 SMA (Very Bearish)"
                    })
        
        return crossovers
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Detect chart patterns (simplified)
        """
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        # Simple pattern detection
        recent_highs = df['high'].tail(10)
        recent_lows = df['low'].tail(10)
        
        # Double Top/Bottom (simplified)
        if len(recent_highs) >= 5:
            if abs(recent_highs.iloc[-1] - recent_highs.iloc[-5]) / recent_highs.iloc[-5] < 0.02:
                patterns.append({
                    "type": "Potential Double Top",
                    "description": "Two similar peaks - bearish reversal pattern"
                })
        
        if len(recent_lows) >= 5:
            if abs(recent_lows.iloc[-1] - recent_lows.iloc[-5]) / recent_lows.iloc[-5] < 0.02:
                patterns.append({
                    "type": "Potential Double Bottom",
                    "description": "Two similar troughs - bullish reversal pattern"
                })
        
        return patterns
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze volume patterns
        """
        avg_volume_20 = df['volume'].tail(20).mean()
        current_volume = df['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0
        
        # Determine signal
        if volume_ratio > 2.0:
            signal = "High Volume Breakout"
        elif volume_ratio > 1.5:
            signal = "Above Average Volume"
        elif volume_ratio < 0.5:
            signal = "Low Volume"
        else:
            signal = "Normal Volume"
        
        return {
            "current_volume": int(current_volume),
            "average_volume_20d": int(avg_volume_20),
            "volume_ratio": round(volume_ratio, 2),
            "signal": signal
        }
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """
        Return default analysis when data is insufficient
        """
        return {
            "score": 5.0,
            "trend": "Unknown",
            "support_levels": [],
            "resistance_levels": [],
            "indicators": {},
            "signals": ["Insufficient data for analysis"],
            "crossovers": [],
            "patterns": [],
            "volume_analysis": {},
            "timestamp": datetime.utcnow().isoformat()
        }
