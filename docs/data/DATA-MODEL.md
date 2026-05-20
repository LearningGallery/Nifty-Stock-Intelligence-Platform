# Data Model

## Chat Session Entity
- session_id (PK)
- created_at
- updated_at
- user_id
- metadata
- ttl

## Chat Message Entity
- session_id (PK)
- message_id (SK)
- role
- content
- timestamp
- metadata
- ttl

## Document Metadata Entity
- document_id (PK)
- version (SK)
- stock_symbol
- document_type
- ingestion_timestamp
- s3_path
- metadata
- ttl

## Citation / Source Mapping
Stored in OpenSearch document metadata:
- source
- url
- timestamp
- stock_symbol
- document_type

## Storage Rationale
- DynamoDB for operational low-latency access
- OpenSearch for semantic retrieval
- S3 for durable object storage
