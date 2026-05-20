"""
RAG (Retrieval-Augmented Generation) Service
Handles document retrieval from OpenSearch
"""
import json
from typing import Dict, Any, List, Optional
from opensearchpy import AsyncOpenSearch, AWSV4SignerAuth, RequestsHttpConnection
from boto3 import Session

from app.config import settings
from app.core.logging import logger
from app.core.exceptions import OpenSearchException


class RAGService:
    """
    Retrieval-Augmented Generation Service
    """
    
    def __init__(self):
        self.index_name = settings.OPENSEARCH_INDEX
        self.client = self._create_client()
        self.top_k = settings.RAG_TOP_K
        self.similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD
    
    def _create_client(self) -> AsyncOpenSearch:
        """
        Create authenticated OpenSearch client
        """
        session = Session()
        credentials = session.get_credentials()
        auth = AWSV4SignerAuth(credentials, settings.AWS_REGION, "es")
        
        # Extract host from endpoint
        host = settings.OPENSEARCH_ENDPOINT.replace("https://", "").replace("http://", "")
        
        return AsyncOpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30
        )
    
    async def retrieve_relevant_documents(
        self,
        query: str,
        stock_symbol: Optional[str] = None,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant documents using vector search
        """
        try:
            # Generate query embedding
            from app.services.bedrock_service import BedrockService
            bedrock_service = BedrockService()
            query_embedding = await bedrock_service.generate_embedding(query)
            
            # Build search query
            search_body = self._build_search_query(
                query_embedding=query_embedding,
                stock_symbol=stock_symbol,
                top_k=top_k or self.top_k,
                filters=filters
            )
            
            # Execute search
            response = await self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            # Process results
            documents = self._process_search_results(response)
            
            logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}")
            
            return {
                "documents": documents,
                "sources": [doc.get("metadata", {}) for doc in documents],
                "total_hits": response["hits"]["total"]["value"]
            }
            
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            raise OpenSearchException(
                message="Failed to retrieve documents",
                details={"error": str(e)}
            )
    
    def _build_search_query(
        self,
        query_embedding: List[float],
        stock_symbol: Optional[str],
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build OpenSearch query with vector search and filters
        """
        query = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": top_k
                                }
                            }
                        }
                    ],
                    "filter": []
                }
            },
            "_source": ["content", "metadata", "stock_symbol", "document_type", "timestamp"]
        }
        
        # Add stock symbol filter
        if stock_symbol:
            query["query"]["bool"]["filter"].append({
                "term": {"stock_symbol.keyword": stock_symbol.upper()}
            })
        
        # Add custom filters
        if filters:
            for key, value in filters.items():
                query["query"]["bool"]["filter"].append({
                    "term": {f"{key}.keyword": value}
                })
        
        # Add minimum score threshold
        query["min_score"] = self.similarity_threshold
        
        return query
    
    def _process_search_results(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process OpenSearch results into structured format
        """
        documents = []
        
        for hit in response.get("hits", {}).get("hits", []):
            source = hit["_source"]
            documents.append({
                "content": source.get("content", ""),
                "metadata": source.get("metadata", {}),
                "stock_symbol": source.get("stock_symbol"),
                "document_type": source.get("document_type"),
                "timestamp": source.get("timestamp"),
                "score": hit["_score"]
            })
        
        return documents
    
    async def index_document(
        self,
        document_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        stock_symbol: Optional[str] = None
    ):
        """
        Index a document with its embedding
        """
        try:
            document = {
                "content": content,
                "embedding": embedding,
                "metadata": metadata,
                "stock_symbol": stock_symbol,
                "document_type": metadata.get("type"),
                "timestamp": metadata.get("timestamp")
            }
            
            await self.client.index(
                index=self.index_name,
                id=document_id,
                body=document
            )
            
            logger.info(f"Indexed document: {document_id}")
            
        except Exception as e:
            logger.error(f"Document indexing error: {e}")
            raise OpenSearchException(
                message="Failed to index document",
                details={"error": str(e), "document_id": document_id}
            )
    
    async def close(self):
        """
        Close OpenSearch client connection
        """
        await self.client.close()