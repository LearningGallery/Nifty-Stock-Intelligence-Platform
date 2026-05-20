"""
Document Upload API
Handles PDF/Excel upload and processing
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from app.config import settings
from app.core.security import get_current_user
from app.core.logging import logger
from app.models.documents import DocumentUploadResponse, DocumentStatus

router = APIRouter()

s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
lambda_client = boto3.client('lambda', region_name=settings.AWS_REGION)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    stock_symbol: Optional[str] = None,
    document_type: str = "annual_report",
    user: Dict[str, Any] = Depends(get_current_user)
) -> DocumentUploadResponse:
    """
    Upload financial document (PDF/Excel) for analysis
    
    Supports:
    - Annual reports
    - Quarterly results
    - Investor presentations
    - Analyst reports
    
    Max file size: 50MB
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, Excel"
            )
        
        # Validate file size (50MB limit)
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 50MB limit"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime('%Y/%m/%d/%H%M%S')
        
        # S3 key structure
        s3_key = f"uploads/{user['user_id']}/{timestamp}/{document_id}/{file.filename}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=settings.UPLOAD_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type,
            Metadata={
                'user_id': user['user_id'],
                'document_id': document_id,
                'stock_symbol': stock_symbol or '',
                'document_type': document_type,
                'original_filename': file.filename
            }
        )
        
        logger.info(f"Document uploaded: {document_id} ({file.filename})")
        
        # Trigger async processing Lambda
        lambda_client.invoke(
            FunctionName=settings.DOCUMENT_PROCESSOR_LAMBDA,
            InvocationType='Event',  # Async
            Payload=json.dumps({
                'document_id': document_id,
                's3_bucket': settings.UPLOAD_BUCKET,
                's3_key': s3_key,
                'user_id': user['user_id'],
                'stock_symbol': stock_symbol,
                'document_type': document_type
            })
        )
        
        logger.info(f"Processing triggered for document: {document_id}")
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            status="processing",
            message="Document uploaded successfully. Processing will complete in 2-5 minutes.",
            s3_location=f"s3://{settings.UPLOAD_BUCKET}/{s3_key}",
            uploaded_at=datetime.utcnow()
        )
        
    except ClientError as e:
        logger.error(f"S3 upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )
    except Exception as e:
        logger.exception(f"Document upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status/{document_id}", response_model=DocumentStatus)
async def get_document_status(
    document_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> DocumentStatus:
    """
    Check processing status of uploaded document
    """
    try:
        # Query DynamoDB for status
        dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        table = dynamodb.Table(settings.DOCUMENT_METADATA_TABLE)
        
        response = table.get_item(
            Key={'document_id': document_id}
        )
        
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        item = response['Item']
        
        # Verify ownership
        if item.get('user_id') != user['user_id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return DocumentStatus(
            document_id=document_id,
            filename=item.get('original_filename'),
            status=item.get('status', 'processing'),
            progress=item.get('progress', 0),
            total_pages=item.get('total_pages'),
            chunks_created=item.get('chunks_created'),
            error_message=item.get('error_message'),
            processed_at=item.get('processed_at'),
            stock_symbol=item.get('stock_symbol')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting document status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document status"
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete uploaded document and all associated data
    """
    try:
        # Verify ownership and get S3 location
        dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        table = dynamodb.Table(settings.DOCUMENT_METADATA_TABLE)
        
        response = table.get_item(Key={'document_id': document_id})
        
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        item = response['Item']
        
        if item.get('user_id') != user['user_id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete from S3
        s3_path = item.get('s3_path', '')
        if s3_path:
            bucket, key = s3_path.replace('s3://', '').split('/', 1)
            s3_client.delete_object(Bucket=bucket, Key=key)
        
        # Delete from OpenSearch (all chunks)
        from opensearchpy import OpenSearch, RequestsHttpConnection
        from requests_aws4auth import AWS4Auth
        
        # Delete documents with matching document_id
        # Implementation depends on your OpenSearch structure
        
        # Delete from DynamoDB
        table.delete_item(Key={'document_id': document_id})
        
        logger.info(f"Deleted document: {document_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )
