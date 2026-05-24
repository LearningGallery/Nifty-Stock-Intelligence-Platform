"""
Health Check Endpoints
"""
from fastapi import APIRouter, status
from typing import Dict, Any
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from opensearchpy import AsyncOpenSearch, AWSV4SignerAuth, RequestsHttpConnection
from boto3 import Session

from app.config import settings
from app.core.logging import logger
from app.dependencies import get_aws_clients, get_redis_client

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with dependency checks
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check Bedrock
    try:
        aws_clients = await get_aws_clients()
        await aws_clients["bedrock_runtime"].list_foundation_models()
        health_status["dependencies"]["bedrock"] = "healthy"
    except Exception as e:
        logger.error(f"Bedrock health check failed: {e}")
        health_status["dependencies"]["bedrock"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check DynamoDB
    try:
        aws_clients = await get_aws_clients()
        dynamodb = aws_clients["dynamodb"]
        table = dynamodb.Table(settings.CHAT_SESSIONS_TABLE)
        # Accessing table_status is a lightweight way to check connectivity
        _ = table.table_status
        health_status["dependencies"]["dynamodb"] = "healthy"
    except Exception as e:
        logger.error(f"DynamoDB health check failed: {e}")
        health_status["dependencies"]["dynamodb"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        health_status["dependencies"]["redis"] = "healthy"
        await redis_client.close()
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["dependencies"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check OpenSearch
    try:
        session = Session()
        credentials = session.get_credentials()
        auth = AWSV4SignerAuth(credentials, settings.AWS_REGION, "es")
        
        client = AsyncOpenSearch(
            hosts=[{"host": settings.OPENSEARCH_ENDPOINT.replace("https://", ""), "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        await client.cluster.health()
        health_status["dependencies"]["opensearch"] = "healthy"
        await client.close()
    except Exception as e:
        logger.error(f"OpenSearch health check failed: {e}")
        health_status["dependencies"]["opensearch"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, str]:
    return {"status": "ready"}


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    return {"status": "alive"}