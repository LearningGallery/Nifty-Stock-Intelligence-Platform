"""
Dependency Injection
"""
import boto3
from typing import Dict, Any
from functools import lru_cache
import redis.asyncio as redis

from app.config import settings
from app.core.logging import logger


@lru_cache()
async def get_aws_clients() -> Dict[str, Any]:
    """
    Get AWS service clients (cached)
    """
    return {
        "bedrock_runtime": boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION
        ),
        "dynamodb": boto3.resource(
            "dynamodb",
            region_name=settings.AWS_REGION
        ),
        "s3": boto3.client(
            "s3",
            region_name=settings.AWS_REGION
        ),
        "secrets_manager": boto3.client(
            "secretsmanager",
            region_name=settings.AWS_REGION
        )
    }


async def get_redis_client() -> redis.Redis:
    """
    Get Redis client
    """
    return redis.Redis(
        host=settings.REDIS_ENDPOINT,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
