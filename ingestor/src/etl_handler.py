"""
ETL Lambda Handler
Processes raw data from S3, chunks documents, generates embeddings, and indexes to OpenSearch
"""
import json
import os
from typing import Dict, Any, List
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from processors.document_processor import DocumentProcessor
from processors.chunker import DocumentChunker
from processors.embedder import EmbeddingGenerator
from utils.helpers import logger

# Environment variables
OPENSEARCH_ENDPOINT = os.environ.get('OPENSEARCH_ENDPOINT')
OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX', 'stock-documents')
BEDROCK_EMBEDDING_MODEL = os.environ.get('BEDROCK_EMBEDDING_MODEL')
DOCUMENT_METADATA_TABLE = os.environ.get('DOCUMENT_METADATA_TABLE')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
metadata_table = dynamodb.Table(DOCUMENT_METADATA_TABLE)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler triggered by S3 events
    Processes raw stock data and indexes to OpenSearch
    """
    logger.info(f"ETL processing started: {json.dumps(event)}")
    
    try:
        # Initialize processors
        doc_processor = DocumentProcessor()
        chunker = DocumentChunker()
        embedder = EmbeddingGenerator(
            model_id=BEDROCK_EMBEDDING_MODEL,
            region=AWS_REGION
        )
        
        results = {
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        # Process S3 events
        for record in event.get('Records', []):
            try:
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                
                logger.info(f"Processing s3://{bucket}/{key}")
                
                # Download file from S3
                response = s3_client.get_object(Bucket=bucket, Key=key)
                raw_data = json.loads(response['Body'].read().decode('utf-8'))
                
                # Process document
                processed_docs = doc_processor.process_stock_data(raw_data)
                
                # Chunk documents
                chunks = []
                for doc in processed_docs:
                    doc_chunks = chunker.chunk_document(
                        content=doc['content'],
                        metadata=doc['metadata']
                    )
                    chunks.extend(doc_chunks)
                
                logger.info(f"Generated {len(chunks)} chunks from {len(processed_docs)} documents")
                
                # Generate embeddings and index
                indexed_count = 0
                for chunk in chunks:
                    try:
                        # Generate embedding
                        embedding = embedder.generate_embedding(chunk['content'])
                        
                        # Index to OpenSearch
                        index_document(
                            chunk_id=chunk['id'],
                            content=chunk['content'],
                            embedding=embedding,
                            metadata=chunk['metadata'],
                            stock_symbol=raw_data.get('symbol')
                        )
                        
                        # Store metadata in DynamoDB
                        store_document_metadata(
                            document_id=chunk['id'],
                            metadata=chunk['metadata'],
                            s3_path=f"s3://{bucket}/{key}",
                            stock_symbol=raw_data.get('symbol')
                        )
                        
                        indexed_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error indexing chunk {chunk['id']}: {e}")
                
                logger.info(f"Successfully indexed {indexed_count}/{len(chunks)} chunks")
                results['processed'] += 1
                
            except Exception as e:
                logger.error(f"Error processing record: {e}")
                results['failed'] += 1
                results['errors'].append({
                    'key': key,
                    'error': str(e)
                })
        
        logger.info(f"ETL completed: {results}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        logger.exception(f"Fatal error in ETL: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }


def index_document(
    chunk_id: str,
    content: str,
    embedding: List[float],
    metadata: Dict[str, Any],
    stock_symbol: str
):
    """
    Index document to OpenSearch
    """
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from requests_aws4auth import AWS4Auth
    
    # Get credentials
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        AWS_REGION,
        'es',
        session_token=credentials.token
    )
    
    # Create OpenSearch client
    client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT.replace('https://', ''), 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    # Prepare document
    document = {
        'content': content,
        'embedding': embedding,
        'metadata': metadata,
        'stock_symbol': stock_symbol,
        'document_type': metadata.get('type'),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Index document
    client.index(
        index=OPENSEARCH_INDEX,
        id=chunk_id,
        body=document
    )
    
    logger.info(f"Indexed document {chunk_id} to OpenSearch")


def store_document_metadata(
    document_id: str,
    metadata: Dict[str, Any],
    s3_path: str,
    stock_symbol: str
):
    """
    Store document metadata in DynamoDB
    """
    timestamp = int(datetime.utcnow().timestamp())
    
    item = {
        'document_id': document_id,
        'version': 1,
        'stock_symbol': stock_symbol,
        'document_type': metadata.get('type'),
        'ingestion_timestamp': timestamp,
        's3_path': s3_path,
        'metadata': metadata,
        'ttl': timestamp + (90 * 24 * 60 * 60)  # 90 days
    }
    
    metadata_table.put_item(Item=item)
    logger.info(f"Stored metadata for document {document_id}")
