"""
Embedding Generator
Generates embeddings using Amazon Bedrock
"""
import json
from typing import List
import boto3
from botocore.exceptions import ClientError

from utils.helpers import logger


class EmbeddingGenerator:
    """
    Generates embeddings using Bedrock Titan Embeddings
    """
    
    def __init__(self, model_id: str, region: str):
        self.model_id = model_id
        self.client = boto3.client('bedrock-runtime', region_name=region)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        """
        try:
            body = json.dumps({
                "inputText": text
            })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding', [])
            
            logger.info(f"Generated embedding of dimension {len(embedding)}")
            return embedding
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
