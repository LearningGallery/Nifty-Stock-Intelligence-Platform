"""
OpenSearch Repository
"""
from typing import List, Dict, Any, Optional
from opensearchpy import AsyncOpenSearch, AWSV4SignerAuth, RequestsHttpConnection
from boto3 import Session

from app.config import settings
from app.core.logging import logger
from app.core.exceptions import OpenSearchException


class OpenSearchRepository:
    """
    Repository for OpenSearch operations
    """
    
    def __init__(self):
        self.client = self._create_client()
        self.index_name = settings.OPENSEARCH_INDEX
    
    def _create_client(self) -> AsyncOpenSearch:
        """Create authenticated OpenSearch client"""
        session = Session()
        credentials = session.get_credentials()
        auth = AWSV4SignerAuth(credentials, settings.AWS_REGION, "es")
        
        host = settings.OPENSEARCH_ENDPOINT.replace("https://", "").replace("http://", "")
        
        return AsyncOpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30
        )
    
    async def index_document(
        self,
        doc_id: str,
        document: Dict[str, Any],
        index: Optional[str] = None
    ) -> None:
        """Index a document"""
        try:
            await self.client.index(
                index=index or self.index_name,
                id=doc_id,
                body=document
            )
            logger.debug(f"Indexed document: {doc_id}")
        except Exception as e:
            logger.error(f"OpenSearch index error: {e}")
            raise OpenSearchException(f"Failed to index document {doc_id}")
    
    async def get_document(
        self,
        doc_id: str,
        index: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            response = await self.client.get(
                index=index or self.index_name,
                id=doc_id
            )
            return response.get('_source')
        except Exception as e:
            logger.error(f"OpenSearch get error: {e}")
            return None
    
    async def search(
        self,
        query: Dict[str, Any],
        index: Optional[str] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents"""
        try:
            response = await self.client.search(
                index=index or self.index_name,
                body=query,
                size=size
            )
            
            hits = response.get('hits', {}).get('hits', [])
            return [hit['_source'] for hit in hits]
        except Exception as e:
            logger.error(f"OpenSearch search error: {e}")
            raise OpenSearchException("Search failed")
    
    async def delete_document(
        self,
        doc_id: str,
        index: Optional[str] = None
    ) -> None:
        """Delete document by ID"""
        try:
            await self.client.delete(
                index=index or self.index_name,
                id=doc_id
            )
        except Exception as e:
            logger.error(f"OpenSearch delete error: {e}")
            raise OpenSearchException(f"Failed to delete document {doc_id}")
    
    async def close(self):
        """Close client connection"""
        await self.client.close()
