"""
RAG Prompt Templates for Document Retrieval
"""

RAG_QUERY_TEMPLATE = """Based on the following retrieved documents about {stock_symbol}, answer the user's question.

## Retrieved Documents:
{documents}

## User Question:
{question}

## Instructions:
- Use information from the retrieved documents
- Cite specific sources when possible
- If documents don't contain enough information, acknowledge this
- Combine multiple sources for comprehensive answer
- Maintain accuracy - don't fabricate information

Answer:"""

---

DOCUMENT_RELEVANCE_TEMPLATE = """Determine if the following document is relevant to answering the user's query about {stock_symbol}.

## Document:
Title: {doc_title}
Content: {doc_content}
Source: {doc_source}
Date: {doc_date}

## User Query:
{user_query}

Is this document relevant? (Yes/No)
Relevance Score (0-10):
Reason:"""
