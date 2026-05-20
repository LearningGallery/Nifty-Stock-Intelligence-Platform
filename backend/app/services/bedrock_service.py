"""
Amazon Bedrock Service
Handles all LLM interactions
"""
import json
from typing import Dict, Any, Optional, AsyncIterator
import boto3
from botocore.exceptions import ClientError

from app.config import settings
from app.core.logging import logger
from app.core.exceptions import BedrockException


class BedrockService:
    """
    Service for interacting with Amazon Bedrock
    """
    
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION
        )
        self.model_id = settings.BEDROCK_MODEL_ID
        self.max_tokens = settings.BEDROCK_MAX_TOKENS
        self.temperature = settings.BEDROCK_TEMPERATURE
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Generate response from Claude via Bedrock
        """
        try:
            # Build request body based on model
            if "claude" in self.model_id.lower():
                body = self._build_claude_request(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=temperature or self.temperature,
                    stop_sequences=stop_sequences
                )
            else:
                raise BedrockException(f"Unsupported model: {self.model_id}")
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content based on model response format
            if "claude" in self.model_id.lower():
                content = response_body.get("content", [{}])[0].get("text", "")
                usage = {
                    "input_tokens": response_body.get("usage", {}).get("input_tokens", 0),
                    "output_tokens": response_body.get("usage", {}).get("output_tokens", 0)
                }
            else:
                content = response_body.get("completion", "")
                usage = {}
            
            logger.info(f"Bedrock response generated. Tokens: {usage}")
            
            return {
                "content": content,
                "usage": usage,
                "model_id": self.model_id
            }
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise BedrockException(
                message="Failed to generate response from Bedrock",
                details={"error": str(e)}
            )
        except Exception as e:
            logger.exception(f"Unexpected error in Bedrock service: {e}")
            raise BedrockException(
                message="Unexpected error generating response",
                details={"error": str(e)}
            )
    
    async def generate_streaming_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> AsyncIterator[str]:
        """
        Generate streaming response from Bedrock
        """
        try:
            body = self._build_claude_request(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
            
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_data = json.loads(chunk.get('bytes').decode())
                        
                        if chunk_data.get('type') == 'content_block_delta':
                            delta = chunk_data.get('delta', {})
                            text = delta.get('text', '')
                            if text:
                                yield text
            
        except Exception as e:
            logger.exception(f"Streaming error: {e}")
            raise BedrockException(
                message="Failed to stream response",
                details={"error": str(e)}
            )
    
    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding using Titan Embeddings
        """
        try:
            body = json.dumps({
                "inputText": text
            })
            
            response = self.client.invoke_model(
                modelId=settings.BEDROCK_EMBEDDING_MODEL,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            embedding = response_body.get("embedding", [])
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise BedrockException(
                message="Failed to generate embedding",
                details={"error": str(e)}
            )
    
    def _build_claude_request(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        stop_sequences: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Build request body for Claude models
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if system_prompt:
            body["system"] = system_prompt
        
        if stop_sequences:
            body["stop_sequences"] = stop_sequences
        
        return body
