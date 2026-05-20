"""
Orchestration Service
Coordinates all analysis components and LLM interaction
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.bedrock_service import BedrockService
from app.services.rag_service import RAGService
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.fundamental_analysis import FundamentalAnalysisService
from app.services.sentiment_analysis import SentimentAnalysisService
from app.services.cache_service import CacheService
from app.services.stock_data_service import StockDataService
from app.models.stock import (
    StockAnalysisResponse,
    RecommendationType,
    ConfidenceLevel,
    RiskLevel,
    TimeframeTarget,
    TechnicalSignal
)
from app.prompts.system_prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT_TEMPLATE
from app.core.logging import logger
from app.core.exceptions import StockDataException


class OrchestrationService:
    """
    Orchestrates multi-component stock analysis workflow
    """
    
    def __init__(self):
        self.bedrock_service = BedrockService()
        self.rag_service = RAGService()
        self.technical_service = TechnicalAnalysisService()
        self.fundamental_service = FundamentalAnalysisService()
        self.sentiment_service = SentimentAnalysisService()
        self.cache_service = CacheService()
        self.stock_service = StockDataService()
    
    async def process_chat_message(
        self,
        message: str,
        session_id: str,
        conversation_history: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a chat message with full context awareness
        """
        logger.info(f"Processing chat message for session {session_id}")
        
        # Extract stock symbol from message if present
        stock_symbol = await self._extract_stock_symbol(message)
        
        # Retrieve relevant documents via RAG
        rag_context = await self.rag_service.retrieve_relevant_documents(
            query=message,
            stock_symbol=stock_symbol,
            top_k=5
        )
        
        # If stock analysis is requested, gather analysis data
        analysis_data = None
        if stock_symbol:
            logger.info(f"Stock analysis requested for: {stock_symbol}")
            analysis_data = await self._gather_analysis_data(stock_symbol)
        
        # Build prompt with all context
        prompt = await self._build_chat_prompt(
            message=message,
            conversation_history=conversation_history,
            rag_context=rag_context,
            analysis_data=analysis_data,
            context=context
        )
        
        # Get LLM response
        llm_response = await self.bedrock_service.generate_response(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=4096,
            temperature=0.7
        )
        
        # Format response
        response = {
            "content": llm_response["content"],
            "analysis_data": analysis_data,
            "sources": rag_context.get("sources", []),
            "stock_symbol": stock_symbol
        }
        
        return response
    
    async def generate_comprehensive_analysis(
        self,
        stock_symbol: str,
        analysis_type: str = "comprehensive",
        timeframe: str = "short_term"
    ) -> StockAnalysisResponse:
        """
        Generate complete stock analysis with all components
        """
        logger.info(f"Generating comprehensive analysis for {stock_symbol}")
        
        # Check cache first
        cache_key = f"analysis:{stock_symbol}:{timeframe}"
        cached = await self.cache_service.get(cache_key)
        if cached:
            logger.info(f"Returning cached analysis for {stock_symbol}")
            return StockAnalysisResponse(**cached)
        
        # Gather all analysis components in parallel
        try:
            analysis_data = await self._gather_analysis_data(stock_symbol)
            
            # Build structured prompt for LLM
            prompt = self._build_analysis_prompt(
                stock_symbol=stock_symbol,
                analysis_data=analysis_data,
                timeframe=timeframe
            )
            
            # Get LLM analysis
            llm_response = await self.bedrock_service.generate_response(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                max_tokens=4096,
                temperature=0.5  # Lower temp for more consistent analysis
            )
            
            # Parse and structure response
            structured_analysis = await self._structure_analysis_response(
                stock_symbol=stock_symbol,
                llm_response=llm_response,
                analysis_data=analysis_data,
                timeframe=timeframe
            )
            
            # Cache result
            await self.cache_service.set(
                cache_key,
                structured_analysis.dict(),
                ttl=300  # 5 minutes
            )
            
            logger.info(f"Completed comprehensive analysis for {stock_symbol}")
            
            return structured_analysis
            
        except Exception as e:
            logger.exception(f"Error generating analysis for {stock_symbol}: {e}")
            raise StockDataException(
                message=f"Failed to analyze {stock_symbol}",
                details={"error": str(e)}
            )
    
    async def get_quick_analysis(self, stock_symbol: str) -> Dict[str, Any]:
        """
        Get quick analysis snapshot (lightweight, cached)
        """
        cache_key = f"quick_analysis:{stock_symbol}"
        cached = await self.cache_service.get(cache_key)
        if cached:
            return cached
        
        # Get current price and basic data
        price_data = await self.stock_service.get_current_price(stock_symbol)
        
        # Get simple technical signal
        technical_signal = await self.technical_service.get_simple_signal(stock_symbol)
        
        # Get recent sentiment
        sentiment = await self.sentiment_service.get_latest_sentiment(stock_symbol)
        
        quick_data = {
            "stock_symbol": stock_symbol,
            "current_price": price_data.get("current_price"),
            "change_percent": price_data.get("change_percent"),
            "technical_signal": technical_signal,
            "sentiment": sentiment.get("sentiment", "neutral"),
            "recommendation": self._derive_quick_recommendation(
                technical_signal, sentiment
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache for 5 minutes
        await self.cache_service.set(cache_key, quick_data, ttl=300)
        
        return quick_data
    
    # ============================================
    # Private Helper Methods
    # ============================================
    
    async def _extract_stock_symbol(self, message: str) -> Optional[str]:
        """
        Extract stock symbol from message using regex and validation
        """
        import re
        
        # Common Nifty 100-250 stock symbols pattern
        # Look for 2-10 uppercase letters (stock symbols)
        pattern = r'\b([A-Z]{2,10})\b'
        matches = re.findall(pattern, message.upper())
        
        if matches:
            # Validate against known symbols
            for match in matches:
                if await self.stock_service.is_valid_symbol(match):
                    return match
        
        return None
    
    async def _gather_analysis_data(self, stock_symbol: str) -> Dict[str, Any]:
        """
        Gather all analysis components for a stock
        """
        import asyncio
        
        # Run all analysis components concurrently
        technical_task = self.technical_service.analyze(stock_symbol)
        fundamental_task = self.fundamental_service.analyze(stock_symbol)
        sentiment_task = self.sentiment_service.analyze(stock_symbol)
        price_task = self.stock_service.get_current_price(stock_symbol)
        
        technical, fundamental, sentiment, price_data = await asyncio.gather(
            technical_task,
            fundamental_task,
            sentiment_task,
            price_task,
            return_exceptions=True
        )
        
        # Handle any exceptions
        if isinstance(technical, Exception):
            logger.error(f"Technical analysis failed: {technical}")
            technical = {}
        if isinstance(fundamental, Exception):
            logger.error(f"Fundamental analysis failed: {fundamental}")
            fundamental = {}
        if isinstance(sentiment, Exception):
            logger.error(f"Sentiment analysis failed: {sentiment}")
            sentiment = {}
        if isinstance(price_data, Exception):
            logger.error(f"Price data fetch failed: {price_data}")
            price_data = {}
        
        return {
            "technical": technical,
            "fundamental": fundamental,
            "sentiment": sentiment,
            "price_data": price_data
        }
    
    async def _build_chat_prompt(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        rag_context: Dict[str, Any],
        analysis_data: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive prompt for chat interaction
        """
        prompt_parts = []
        
        # Add conversation history
        if conversation_history:
            prompt_parts.append("## Conversation History:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role.upper()}: {content}")
            prompt_parts.append("")
        
        # Add RAG context
        if rag_context and rag_context.get("documents"):
            prompt_parts.append("## Relevant Information from Knowledge Base:")
            for doc in rag_context["documents"]:
                prompt_parts.append(f"- {doc.get('content', '')[:500]}")
            prompt_parts.append("")
        
        # Add analysis data if available
        if analysis_data:
            prompt_parts.append("## Stock Analysis Data:")
            prompt_parts.append(json.dumps(analysis_data, indent=2))
            prompt_parts.append("")
        
        # Add current user message
        prompt_parts.append("## Current User Query:")
        prompt_parts.append(message)
        prompt_parts.append("")
        
        prompt_parts.append("Please provide a comprehensive, actionable response based on the above information.")
        
        return "\n".join(prompt_parts)
    
    def _build_analysis_prompt(
        self,
        stock_symbol: str,
        analysis_data: Dict[str, Any],
        timeframe: str
    ) -> str:
        """
        Build structured prompt for comprehensive analysis
        """
        return ANALYSIS_PROMPT_TEMPLATE.format(
            stock_symbol=stock_symbol,
            technical_data=json.dumps(analysis_data.get("technical", {}), indent=2),
            fundamental_data=json.dumps(analysis_data.get("fundamental", {}), indent=2),
            sentiment_data=json.dumps(analysis_data.get("sentiment", {}), indent=2),
            price_data=json.dumps(analysis_data.get("price_data", {}), indent=2),
            timeframe=timeframe
        )
    
    async def _structure_analysis_response(
        self,
        stock_symbol: str,
        llm_response: Dict[str, Any],
        analysis_data: Dict[str, Any],
        timeframe: str
    ) -> StockAnalysisResponse:
        """
        Structure LLM response into StockAnalysisResponse model
        """
        # Extract structured data from LLM response
        content = llm_response.get("content", "")
        
        # Parse LLM response (assuming JSON or structured text)
        # This is a simplified version; implement robust parsing
        try:
            # Attempt to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                # Fallback: create structure from raw analysis data
                parsed = self._create_fallback_structure(analysis_data)
        except:
            parsed = self._create_fallback_structure(analysis_data)
        
        # Get price data
        price_data = analysis_data.get("price_data", {})
        technical = analysis_data.get("technical", {})
        fundamental = analysis_data.get("fundamental", {})
        sentiment = analysis_data.get("sentiment", {})
        
        # Build response
        return StockAnalysisResponse(
            stock_symbol=stock_symbol,
            company_name=price_data.get("company_name", stock_symbol),
            sector=fundamental.get("sector", "Unknown"),
            market_cap=fundamental.get("market_cap", 0.0),
            current_price=price_data.get("current_price", 0.0),
            
            recommendation=parsed.get("recommendation", RecommendationType.HOLD),
            confidence_level=parsed.get("confidence_level", ConfidenceLevel.MEDIUM),
            risk_level=parsed.get("risk_level", RiskLevel.MODERATE),
            
            pros=parsed.get("pros", []),
            cons=parsed.get("cons", []),
            
            short_term_target=TimeframeTarget(**parsed.get("short_term_target", {
                "entry_point": price_data.get("current_price", 0.0),
                "target_1": price_data.get("current_price", 0.0) * 1.05,
                "stop_loss": price_data.get("current_price", 0.0) * 0.95,
                "risk_reward_ratio": "1:1",
                "expected_upside_percent": 5.0
            })),
            
            long_term_target=None,
            
            technical_signals=[
                TechnicalSignal(**sig) for sig in parsed.get("technical_signals", [])
            ],
            technical_score=technical.get("score", 5.0),
            
            fundamental_data=fundamental.get("metrics", {}),
            fundamental_score=fundamental.get("score", 5.0),
            
            news_summary=sentiment.get("summary", ""),
            sentiment_score=sentiment.get("score", 5.0),
            recent_news=sentiment.get("recent_news", []),
            
            risk_factors=parsed.get("risk_factors", []),
            action_items=parsed.get("action_items", []),
            
            analysis_timestamp=datetime.utcnow(),
            data_sources=["NSE", "BSE", "Screener.in", "NewsAPI", "Bedrock AI"]
        )
    
    def _create_fallback_structure(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback structure when LLM response parsing fails
        """
        technical = analysis_data.get("technical", {})
        fundamental = analysis_data.get("fundamental", {})
        sentiment = analysis_data.get("sentiment", {})
        
        return {
            "recommendation": RecommendationType.HOLD,
            "confidence_level": ConfidenceLevel.MEDIUM,
            "risk_level": RiskLevel.MODERATE,
            "pros": fundamental.get("strengths", [])[:5],
            "cons": fundamental.get("weaknesses", [])[:5],
            "technical_signals": [],
            "risk_factors": fundamental.get("red_flags", []),
            "action_items": ["Review detailed analysis", "Monitor price action"]
        }
    
    def _derive_quick_recommendation(
        self,
        technical_signal: str,
        sentiment: Dict[str, Any]
    ) -> str:
        """
        Derive quick recommendation from technical and sentiment signals
        """
        if technical_signal == "bullish" and sentiment.get("score", 5) > 6:
            return "BUY"
        elif technical_signal == "bearish" or sentiment.get("score", 5) < 4:
            return "SELL"
        else:
            return "HOLD"
