# High-Level Design (HLD)

## Overview
The Nifty Stock Intelligence Platform is an AWS-native AI application that provides conversational stock analysis for Indian equities using:
- Real-time market and news ingestion
- Technical, fundamental, and sentiment analysis
- Amazon Bedrock for LLM reasoning
- OpenSearch for vector retrieval (RAG)
- React frontend + FastAPI backend

## Business Goals
- Showcase AI/cloud architecture on GitHub
- Demonstrate reusable AWS reference implementation
- Provide realistic stock intelligence chatbot experience
- Remain cost-conscious for demo/test usage

## Logical Architecture
1. **Frontend Layer**
   - React SPA hosted on S3 + CloudFront

2. **Application Layer**
   - FastAPI backend on ECS Fargate
   - Handles chat, orchestration, analysis APIs, document upload

3. **AI Layer**
   - Amazon Bedrock Claude 3.5 Sonnet for reasoning
   - Titan Embeddings for semantic retrieval

4. **Knowledge Layer**
   - OpenSearch vector index
   - S3 raw/processed document storage
   - DynamoDB metadata and session storage

5. **Data Ingestion Layer**
   - EventBridge scheduled Lambda ingestion
   - S3-triggered ETL Lambda
   - Optional document upload processor (Textract)

6. **Security & Ops**
   - Cognito authentication
   - WAF
   - CloudWatch, X-Ray, SNS alarms

## Key Design Principles
- AWS-native where practical
- Modular Terraform
- Stateless backend
- Event-driven ingestion
- Cost-aware defaults
- Portfolio-quality documentation
