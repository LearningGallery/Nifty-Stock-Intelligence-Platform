"""
Document Processor Lambda
Uses AWS Textract to extract text from PDFs
"""
import json
import os
from typing import Dict, Any
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from processors.document_processor import DocumentProcessor
from processors.chunker import DocumentChunker
from processors.embedder import EmbeddingGenerator
from utils.helpers import logger

# AWS clients
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
metadata_table = dynamodb.Table(os.environ['DOCUMENT_METADATA_TABLE'])


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process uploaded document:
    1. Extract text using Textract
    2. Chunk document
    3. Generate embeddings
    4. Index to OpenSearch
    """
    try:
        document_id = event['document_id']
        s3_bucket = event['s3_bucket']
        s3_key = event['s3_key']
        user_id = event['user_id']
        stock_symbol = event.get('stock_symbol')
        
        logger.info(f"Processing document: {document_id}")
        
        # Update status to processing
        update_status(document_id, "processing", 0)
        
        # 1. Extract text from PDF using Textract
        logger.info("Starting Textract extraction...")
        
        response = textract_client.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': s3_bucket,
                    'Name': s3_key
                }
            }
        )
        
        job_id = response['JobId']
        
        # Wait for Textract to complete
        extracted_text = wait_for_textract_job(job_id)
        
        if not extracted_text:
            raise Exception("Failed to extract text from document")
        
        logger.info(f"Extracted {len(extracted_text)} characters")
        update_status(document_id, "processing", 30)
        
        # 2. Chunk the document
        logger.info("Chunking document...")
        chunker = DocumentChunker(chunk_size=512, chunk_overlap=50)
        
        chunks = chunker.chunk_document(
            content=extracted_text,
            metadata={
                'document_id': document_id,
                'user_id': user_id,
                'stock_symbol': stock_symbol,
                'document_type': event.get('document_type'),
                'source': 'uploaded_document'
            }
        )
        
        logger.info(f"Created {len(chunks)} chunks")
        update_status(document_id, "processing", 50)
        
        # 3. Generate embeddings and index
        logger.info("Generating embeddings and indexing...")
        embedder = EmbeddingGenerator(
            model_id=os.environ['BEDROCK_EMBEDDING_MODEL'],
            region=os.environ['AWS_REGION']
        )
        
        indexed_count = 0
        for i, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding = embedder.generate_embedding(chunk['content'])
                
                # Index to OpenSearch
                index_to_opensearch(
                    chunk_id=chunk['id'],
                    content=chunk['content'],
                    embedding=embedding,
                    metadata=chunk['metadata'],
                    document_id=document_id,
                    stock_symbol=stock_symbol
                )
                
                indexed_count += 1
                
                # Update progress
                progress = 50 + int((i / len(chunks)) * 50)
                if i % 10 == 0:  # Update every 10 chunks
                    update_status(document_id, "processing", progress)
                
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {e}")
        
        # 4. Update final status
        metadata_table.update_item(
            Key={'document_id': document_id},
            UpdateExpression='SET #status = :status, progress = :progress, chunks_created = :chunks, processed_at = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':progress': 100,
                ':chunks': indexed_count,
                ':timestamp': datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Successfully processed document {document_id}: {indexed_count} chunks indexed")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'document_id': document_id,
                'status': 'completed',
                'chunks_indexed': indexed_count
            })
        }
        
    except Exception as e:
        logger.exception(f"Error processing document: {e}")
        
        # Update status to failed
        try:
            update_status(
                document_id,
                "failed",
                error_message=str(e)
            )
        except:
            pass
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def wait_for_textract_job(job_id: str, max_wait: int = 300) -> str:
    """
    Wait for Textract job to complete and retrieve text
    """
    import time
    
    start_time = time.time()
    
    while True:
        if time.time() - start_time > max_wait:
            raise TimeoutError("Textract job timed out")
        
        response = textract_client.get_document_text_detection(JobId=job_id)
        status = response['JobStatus']
        
        if status == 'SUCCEEDED':
            # Extract all text
            blocks = response['Blocks']
            text_lines = []
            
            for block in blocks:
                if block['BlockType'] == 'LINE':
                    text_lines.append(block['Text'])
            
            # Handle pagination
            next_token = response.get('NextToken')
            while next_token:
                response = textract_client.get_document_text_detection(
                    JobId=job_id,
                    NextToken=next_token
                )
                blocks = response['Blocks']
                for block in blocks:
                    if block['BlockType'] == 'LINE':
                        text_lines.append(block['Text'])
                next_token = response.get('NextToken')
            
            return '\n'.join(text_lines)
            
        elif status == 'FAILED':
            raise Exception(f"Textract job failed: {response.get('StatusMessage')}")
        
        time.sleep(5)


def update_status(document_id: str, status: str, progress: int = 0, error_message: str = None):
    """Update document processing status in DynamoDB"""
    update_expr = 'SET #status = :status, progress = :progress'
    expr_values = {':status': status, ':progress': progress}
    expr_names = {'#status': 'status'}
    
    if error_message:
        update_expr += ', error_message = :error'
        expr_values[':error'] = error_message
    
    metadata_table.update_item(
        Key={'document_id': document_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values
    )


def index_to_opensearch(chunk_id, content, embedding, metadata, document_id, stock_symbol):
    """Index chunk to OpenSearch"""
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from requests_aws4auth import AWS4Auth
    
    # Create OpenSearch client
    session = boto3.Session()
    credentials = session.get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        os.environ['AWS_REGION'],
        'es',
        session_token=credentials.token
    )
    
    client = OpenSearch(
        hosts=[{
            'host': os.environ['OPENSEARCH_ENDPOINT'].replace('https://', ''),
            'port': 443
        }],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    document = {
        'content': content,
        'embedding': embedding,
        'metadata': metadata,
        'document_id': document_id,
        'stock_symbol': stock_symbol,
        'document_type': 'uploaded_document',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    client.index(
        index=os.environ['OPENSEARCH_INDEX'],
        id=chunk_id,
        body=document
    )
