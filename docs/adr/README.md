# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the Nifty Stock Intelligence Platform.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [001](001-bedrock-llm-selection.md) | Selection of Amazon Bedrock and Claude 3.5 Sonnet | Accepted |
| [002](002-rag-pattern-implementation.md) | RAG Pattern Implementation with OpenSearch | Accepted |
| [003](003-opensearch-vs-pinecone.md) | OpenSearch vs Pinecone for Vector Storage | Accepted |
| [004](004-ecs-fargate-vs-lambda.md) | ECS Fargate vs Lambda for Backend | Accepted |
| [005](005-dynamodb-vs-rds.md) | DynamoDB vs RDS for Chat Storage | Accepted |
| [006](006-cognito-authentication.md) | Amazon Cognito for Authentication | Accepted |
| [007](007-technical-analysis-library.md) | pandas-ta for Technical Analysis | Accepted |
| [008](008-data-ingestion-pattern.md) | Event-Driven Data Ingestion Pattern | Accepted |

## ADR Template

Each ADR follows this structure:
- **Title**: Short descriptive title
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: What is the issue we're addressing?
- **Decision**: What is the change we're proposing?
- **Consequences**: What becomes easier or harder as a result?
- **Alternatives Considered**: What other options were evaluated?
