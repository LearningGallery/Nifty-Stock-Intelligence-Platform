"""
Document Chunker
Splits documents into smaller chunks for embedding
"""
import hashlib
from typing import Dict, Any, List
from datetime import datetime


class DocumentChunker:
    """
    Chunks documents into smaller pieces for vector indexing
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Split document into overlapping chunks
        """
        # For simplicity, split by tokens (words)
        words = content.split()
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            # Generate unique ID
            chunk_id = self._generate_chunk_id(
                content=chunk_text,
                metadata=metadata,
                index=chunk_index
            )
            
            chunks.append({
                'id': chunk_id,
                'content': chunk_text,
                'metadata': {
                    **metadata,
                    'chunk_index': chunk_index,
                    'chunk_size': len(chunk_words)
                }
            })
            
            # Move to next chunk with overlap
            start += (self.chunk_size - self.chunk_overlap)
            chunk_index += 1
        
        return chunks
    
    def _generate_chunk_id(
        self,
        content: str,
        metadata: Dict[str, Any],
        index: int
    ) -> str:
        """
        Generate unique chunk ID
        """
        unique_string = f"{metadata.get('symbol')}_{metadata.get('type')}_{index}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(unique_string.encode()).hexdigest()
