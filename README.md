# 🚀 Nifty Stock Intelligence Platform

[![Terraform](https://img.shields.io/badge/Terraform-1.5+-623CE4?logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900?logo=amazon-aws)](https://aws.amazon.com/)
[![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-AI-FF9900?logo=amazon-aws)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://reactjs.org/)
[![OpenSearch](https://img.shields.io/badge/OpenSearch-2.11-005EB8?logo=opensearch)](https://opensearch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/Docs-Complete-brightgreen)](docs/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **AI-Powered Real-Time Stock Analysis & Prediction Engine for Indian Equity Markets**

An enterprise-grade, AWS-native platform that leverages Amazon Bedrock (Claude 3.5 Sonnet), Retrieval-Augmented Generation (RAG), and multi-dimensional analysis to deliver comprehensive stock intelligence for Nifty 100-250 stocks with market cap > ₹5,000 crores.

---

## ✨ Features

### 🤖 AI-Powered Analysis
- **Claude 3.5 Sonnet Integration**: Advanced reasoning for financial analysis
- **RAG Architecture**: Grounded responses using OpenSearch vector search
- **Multi-Modal Analysis**: Technical + Fundamental + Sentiment fusion
- **Real-Time Insights**: Live data from NSE/BSE, news APIs, and financial sources

### 📊 Comprehensive Stock Intelligence
- **Technical Analysis**: RSI, MACD, Moving Averages, Support/Resistance, Chart Patterns
- **Fundamental Analysis**: P/E, ROE, Debt/Equity, Growth Metrics, Peer Comparison
- **Sentiment Analysis**: News aggregation, NLP-based sentiment scoring
- **Risk Assessment**: Clear risk factors, stop-loss recommendations, confidence levels

### 💬 Interactive Chatbot
- **Conversational Interface**: Natural language queries about stocks
- **Context-Aware**: Maintains conversation history across sessions
- **Source Citations**: Transparent references to data sources
- **Multi-Turn Conversations**: Follow-up questions with context retention

### 🏗️ Enterprise Architecture
- **AWS-Native**: ECS Fargate, Lambda, DynamoDB, OpenSearch, Bedrock
- **Infrastructure as Code**: Complete Terraform implementation
- **Auto-Scaling**: Dynamic scaling based on load
- **High Availability**: Multi-AZ deployment with auto-recovery
- **Security**: WAF, Cognito authentication, encryption at rest/transit
- **Observability**: CloudWatch, X-Ray tracing, comprehensive logging

---

## 🏛️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  Web Browser → CloudFront CDN → S3 Static Website (React)       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  API Gateway → WAF → Application Load Balancer                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                             │
│  ECS Fargate (FastAPI) → Orchestration → RAG Service            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      AI/ML Layer                                 │
│  Amazon Bedrock (Claude 3.5 Sonnet + Titan Embeddings)         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Knowledge Base Layer                           │
│  OpenSearch Serverless (Vector DB) ← Lambda ETL                 │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│                   Data Ingestion Layer                           │
│  EventBridge → Lambda → NSE/BSE APIs → S3 Data Lake            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                               │
│  DynamoDB (Chat) | S3 (Documents) | ElastiCache (Cache)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **AWS Account** with Bedrock access
- **Tools**: AWS CLI v2.13+, Terraform v1.5+, Docker v24+, Node.js v18+, Python 3.11+
- **IAM Permissions**: Administrator access or equivalent

### 1. Clone Repository

```bash
git clone https://github.com/LearningGallery/nifty-stock-intelligence.git
cd nifty-stock-intelligence
```

### 2. Configure AWS

```bash
aws configure
# Enter your AWS credentials
# Region: ap-south-1 (recommended for India)
```

### 3. Enable Bedrock Model Access

```bash
# AWS Console → Bedrock → Model access
# Enable: Claude 3.5 Sonnet, Titan Text Embeddings v2
```

### 4. Deploy Infrastructure

```bash
cd terraform

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
vim terraform.tfvars  # Update with your values

# Initialize and deploy
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Save outputs
terraform output > ../deployment-outputs.txt
```

**Deployment Time:** ~20 minutes (OpenSearch takes longest)

### 5. Deploy Application

```bash
# Backend
cd ../backend
export ECR_REPO=$(terraform output -raw backend_ecr_repository_url)
docker build -t nsip-backend .
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin ${ECR_REPO}
docker tag nsip-backend:latest ${ECR_REPO}:latest
docker push ${ECR_REPO}:latest

# Update ECS service
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw backend_service_name) \
  --force-new-deployment

# Frontend
cd ../frontend
npm install
npm run build
aws s3 sync dist/ s3://$(terraform output -raw frontend_bucket_name)/ --delete
aws cloudfront create-invalidation \
  --distribution-id $(terraform output -raw cloudfront_distribution_id) \
  --paths "/*"
```

### 6. Access Application

```bash
# Get frontend URL
terraform output frontend_url

# Open in browser
open $(terraform output -raw frontend_url)
```

### 7. Test API

```bash
# Health check
curl https://$(terraform output -raw alb_dns_name)/health | jq

# Test stock search
curl "https://$(terraform output -raw alb_dns_name)/api/v1/stocks/search?query=TCS" | jq
```

---

## 📁 Project Structure

```
nifty-stock-intelligence/
├── terraform/                      # Infrastructure as Code
│   ├── main.tf                    # Root configuration
│   ├── variables.tf               # Input variables
│   ├── outputs.tf                 # Output values
│   ├── modules/                   # Terraform modules
│   │   ├── networking/            # VPC, subnets, routing
│   │   ├── ecs-cluster/           # ECS Fargate cluster
│   │   ├── backend-service/       # FastAPI backend
│   │   ├── opensearch/            # Vector database
│   │   ├── dynamodb/              # Chat storage
│   │   ├── cognito/               # Authentication
│   │   ├── lambda-ingestor/       # Data ingestion
│   │   ├── cloudfront/            # CDN
│   │   ├── waf/                   # Web application firewall
│   │   └── monitoring/            # CloudWatch dashboards
│   └── environments/              # Environment configs
│       ├── dev.tfvars
│       └── prod.tfvars
│
├── backend/                        # FastAPI Application
│   ├── app/
│   │   ├── main.py               # Application entry point
│   │   ├── api/v1/               # API endpoints
│   │   │   ├── chat.py           # Chat API
│   │   │   ├── stocks.py         # Stock data API
│   │   │   ├── analysis.py       # Analysis API
│   │   │   └── health.py         # Health checks
│   │   ├── services/             # Business logic
│   │   │   ├── orchestration.py  # Main orchestrator
│   │   │   ├── bedrock_service.py # LLM integration
│   │   │   ├── rag_service.py     # RAG implementation
│   │   │   ├── technical_analysis.py
│   │   │   ├── fundamental_analysis.py
│   │   │   └── sentiment_analysis.py
│   │   ├── models/               # Pydantic models
│   │   ├── prompts/              # LLM prompts
│   │   └── utils/                # Helper functions
│   ├── tests/                    # Unit tests
│   ├── Dockerfile                # Container definition
│   └── requirements.txt          # Python dependencies
│
├── frontend/                       # React Application
│   ├── src/
│   │   ├── App.jsx               # Main app component
│   │   ├── pages/                # Page components
│   │   │   ├── HomePage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── AnalysisPage.jsx
│   │   │   └── ExplorePage.jsx
│   │   ├── components/           # Reusable components
│   │   │   ├── Chat/
│   │   │   ├── Analysis/
│   │   │   └── Layout/
│   │   ├── services/             # API clients
│   │   ├── store/                # State management (Zustand)
│   │   └── styles/               # Tailwind CSS
│   ├── package.json
│   └── vite.config.js
│
├── ingestor/                       # Lambda Functions
│   ├── src/
│   │   ├── handler.py            # Ingestion handler
│   │   ├── etl_handler.py        # ETL handler
│   │   ├── data_fetchers/        # API integrations
│   │   │   ├── nse_fetcher.py
│   │   │   ├── news_fetcher.py
│   │   │   └── screener_fetcher.py
│   │   └── processors/           # Data processing
│   │       ├── document_processor.py
│   │       ├── chunker.py
│   │       └── embedder.py
│   └── requirements.txt
│
├── docs/                           # Documentation
│   ├── architecture/              # Architecture docs
│   │   ├── HIGH-LEVEL-DESIGN.md
│   │   ├── LOW-LEVEL-DESIGN.md
│   │   └── AI-ARCHITECTURE.md
│   ├── adr/                       # Architecture decisions
│   │   ├── 001-bedrock-llm-selection.md
│   │   ├── 002-rag-pattern-implementation.md
│   │   └── ...
│   ├── guides/                    # User guides
│   │   ├── DEPLOYMENT.md
│   │   ├── RUNBOOK.md
│   │   └── TROUBLESHOOTING.md
│   ├── security/
│   │   ├── SECURITY.md
│   │   └── RESPONSIBLE-AI.md
│   └── data/
│       └── DATA-MODEL.md
│
├── scripts/                        # Utility scripts
│   ├── deploy.sh                 # Deployment automation
│   ├── build-images.sh           # Docker builds
│   └── run-tests.sh              # Test runner
│
├── .github/workflows/             # CI/CD pipelines
│   ├── terraform-plan.yml
│   ├── terraform-apply.yml
│   └── docker-build.yml
│
├── README.md                      # This file
├── LICENSE                        # MIT License
├── CONTRIBUTING.md                # Contribution guide
└── CHANGELOG.md                   # Version history
```

---

## 🛠️ Technology Stack

### Infrastructure & Cloud
- **AWS Services**: ECS Fargate, Lambda, DynamoDB, OpenSearch, S3, CloudFront, Cognito
- **IaC**: Terraform v1.5+
- **Container**: Docker
- **Networking**: VPC, ALB, NAT Gateway, VPC Endpoints

### AI & Machine Learning
- **LLM**: Amazon Bedrock - Claude 3.5 Sonnet
- **Embeddings**: Amazon Titan Text Embeddings v2
- **Vector DB**: Amazon OpenSearch Serverless
- **RAG**: Custom implementation with semantic search

### Backend
- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11
- **Analysis**: pandas, numpy, pandas-ta, TA-Lib
- **NLP**: transformers, NLTK, TextBlob
- **Async**: asyncio, aiohttp, aioboto3

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Charts**: Recharts

### Data & Storage
- **Database**: DynamoDB (NoSQL)
- **Cache**: Amazon ElastiCache (Redis)
- **Object Storage**: Amazon S3
- **Vector Search**: OpenSearch with k-NN

### Security
- **Authentication**: Amazon Cognito
- **Secrets**: AWS Secrets Manager
- **WAF**: AWS WAF v2
- **Encryption**: KMS, TLS 1.2+

### Observability
- **Logging**: CloudWatch Logs
- **Metrics**: CloudWatch Metrics
- **Tracing**: AWS X-Ray
- **Dashboards**: CloudWatch Dashboards

---

## 📊 Current Scope

### ✅ Implemented Features

- [x] Complete AWS infrastructure via Terraform
- [x] Interactive chatbot with conversation history
- [x] Real-time stock analysis (Technical + Fundamental + Sentiment)
- [x] RAG-based document retrieval
- [x] OpenSearch vector indexing
- [x] Automated data ingestion pipeline
- [x] User authentication (Cognito)
- [x] Responsive React frontend
- [x] Auto-scaling ECS backend
- [x] CloudWatch monitoring & alerts
- [x] Comprehensive documentation

### 🚧 Roadmap (Future Enhancements)

- [ ] **Portfolio Management**: Track user stock holdings
- [ ] **Price Alerts**: Configurable notifications
- [ ] **Comparison Tool**: Side-by-side stock comparison
- [ ] **Historical Backtesting**: Test strategies on historical data
- [ ] **Advanced Charts**: Interactive TradingView-style charts
- [ ] **Mobile App**: React Native iOS/Android apps
- [ ] **Watchlists**: Custom stock monitoring lists
- [ ] **Earnings Calendar**: Track upcoming results
- [ ] **Insider Trading Alerts**: Monitor promoter activity
- [ ] **Options Analysis**: Options chain analysis
- [ ] **Multi-Language Support**: Hindi, regional languages
- [ ] **WhatsApp Integration**: Chatbot via WhatsApp
- [ ] **API Monetization**: Paid API access for developers

---

## 💰 Cost Estimation

### Development Environment (Low Usage)

| Service | Configuration | Monthly Cost (USD) |
|---------|--------------|-------------------|
| ECS Fargate | 1 task, 1vCPU, 2GB | $30 |
| OpenSearch | 1 node, t3.medium | $50 |
| DynamoDB | On-demand, minimal | $5 |
| S3 + CloudFront | 10GB storage, 100GB transfer | $5 |
| Lambda | 100K invocations/month | $2 |
| Bedrock | ~1M tokens/month | $50 |
| NAT Gateway | Single NAT | $32 |
| ElastiCache | cache.t3.micro | $12 |
| Other (ALB, Cognito, etc.) | - | $10 |
| **Total** | | **~$196/month** |

### Production Environment (Moderate Usage)

| Service | Configuration | Monthly Cost (USD) |
|---------|--------------|-------------------|
| ECS Fargate | 4 tasks, 1vCPU, 2GB | $120 |
| OpenSearch | 2 nodes, r6g.large | $300 |
| DynamoDB | On-demand, 10M requests | $15 |
| S3 + CloudFront | 100GB storage, 1TB transfer | $30 |
| Lambda | 1M invocations/month | $5 |
| Bedrock | ~10M tokens/month | $500 |
| NAT Gateway | 2 NATs (HA) | $64 |
| ElastiCache | cache.r6g.large | $100 |
| Other (ALB, WAF, Cognito) | - | $50 |
| **Total** | | **~$1,184/month** |

**Cost Optimization Tips:**
- Use single NAT Gateway in dev ($32/month savings)
- Switch to Claude Haiku for simple queries (cheaper)
- Implement aggressive caching (reduce Bedrock calls)
- Use Fargate Spot for non-critical workloads (70% savings)
- Archive old S3 data to Glacier
- Schedule scale-down during off-hours

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

### Architecture
- [High-Level Design](docs/architecture/HIGH-LEVEL-DESIGN.md)
- [Low-Level Design](docs/architecture/LOW-LEVEL-DESIGN.md)
- [AI Architecture](docs/architecture/AI-ARCHITECTURE.md)
- [Runtime Architecture](docs/architecture/RUNTIME-ARCHITECTURE.md)

### Architecture Decision Records (ADRs)
- [ADR-001: Bedrock LLM Selection](docs/adr/001-bedrock-llm-selection.md)
- [ADR-002: RAG Pattern Implementation](docs/adr/002-rag-pattern-implementation.md)
- [ADR-003: OpenSearch vs Pinecone](docs/adr/003-opensearch-vs-pinecone.md)
- [ADR-004: ECS Fargate vs Lambda](docs/adr/004-ecs-fargate-vs-lambda.md)
- [View All ADRs →](docs/adr/)

### Guides
- [Deployment Guide](docs/guides/DEPLOYMENT.md) - Step-by-step deployment
- [Operations Runbook](docs/guides/RUNBOOK.md) - Day-to-day operations
- [Troubleshooting Guide](docs/guides/TROUBLESHOOTING.md) - Common issues
- [API Documentation](docs/guides/API-DOCUMENTATION.md) - API reference
- [User Guide](docs/guides/USER-GUIDE.md) - End-user documentation

### Security & Compliance
- [Security Overview](docs/security/SECURITY.md)
- [Responsible AI Practices](docs/security/RESPONSIBLE-AI.md)
- [Compliance](docs/security/COMPLIANCE.md)

### Data Models
- [Database Schemas](docs/data/DATA-MODEL.md)
- [API Schemas](docs/data/API-SCHEMAS.md)

---

## 🔒 Security

### Security Features

- **Authentication**: Amazon Cognito with MFA support
- **Authorization**: IAM roles with least-privilege principle
- **Encryption at Rest**: S3, DynamoDB, OpenSearch (KMS)
- **Encryption in Transit**: TLS 1.2+ for all communications
- **Network Security**: Private subnets, security groups, NACLs
- **WAF**: AWS WAF with rate limiting and geo-blocking
- **Secrets Management**: AWS Secrets Manager
- **Vulnerability Scanning**: Automated ECR image scanning
- **Audit Logging**: CloudTrail for all API calls

### Responsible AI

- **Transparency**: Clear source citations
- **Accuracy**: RAG-grounded responses
- **Disclaimers**: Prominent "not financial advice" warnings
- **Bias Mitigation**: Multi-source data aggregation
- **Hallucination Prevention**: Fact-checking against retrieved documents
- **User Control**: Option to see raw data sources

### Reporting Security Issues

Please report security vulnerabilities to: **im-abutalha** via LinkedIn or create a private security advisory on GitHub.

**Do not** disclose security issues publicly until they have been addressed.

---

## 🧪 Testing

### Run Tests Locally

```bash
# Backend tests
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test

# Integration tests
./scripts/run-tests.sh
```

### CI/CD Pipeline

GitHub Actions workflows automatically:
- Run unit tests on PRs
- Perform static code analysis (flake8, mypy, eslint)
- Scan Docker images for vulnerabilities
- Run Terraform validation
- Deploy to dev environment on merge to `develop`
- Deploy to prod on release tags

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/LearningGallery/nifty-stock-intelligence.git
cd nifty-stock-intelligence

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install

# Frontend setup
cd ../frontend
npm install

# Run locally
# Backend: uvicorn app.main:app --reload
# Frontend: npm run dev
```

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- **Python**: Follow PEP 8, use Black formatter, type hints required
- **JavaScript**: ESLint + Prettier, functional components preferred
- **Terraform**: Use modules, follow naming conventions
- **Documentation**: Update docs for any public API changes
- **Tests**: Maintain >80% code coverage

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Abu Talha**
- GitHub: [@LearningGallery](https://github.com/LearningGallery)
- LinkedIn: [Im-AbuTalha](https://www.linkedin.com/in/im-abutalha/)

---

## 🙏 Acknowledgments

- **AWS** for Bedrock and cloud infrastructure
- **Anthropic** for Claude 3.5 Sonnet
- **NSE/BSE** for stock market data
- **Open Source Community** for amazing tools and libraries

---

## 📞 Support & Contact

### Getting Help

1. **Documentation**: Check [docs/](docs/) first
2. **Issues**: [GitHub Issues](https://github.com/LearningGallery/nifty-stock-intelligence/issues)
3. **Discussions**: [GitHub Discussions](https://github.com/LearningGallery/nifty-stock-intelligence/discussions)
4. **LinkedIn**: [Im-AbuTalha](https://www.linkedin.com/in/im-abutalha/)

### Business Inquiries

For consulting, customization, or enterprise support, please reach out via LinkedIn.

---

## ⚖️ Disclaimer

**IMPORTANT:** This platform is for **educational and informational purposes only**. It does NOT constitute financial advice, investment recommendations, or an offer to buy or sell securities.

**Please Note:**
- Always consult a SEBI-registered financial advisor before making investment decisions
- Past performance does not guarantee future results
- Stock markets are subject to risks and volatility
- Conduct your own due diligence before investing
- Only invest funds you can afford to lose

The developers and contributors are not responsible for any financial losses incurred from using this platform.

---

## 📈 Project Status

![GitHub last commit](https://img.shields.io/github/last-commit/LearningGallery/nifty-stock-intelligence)
![GitHub issues](https://img.shields.io/github/issues/LearningGallery/nifty-stock-intelligence)
![GitHub pull requests](https://img.shields.io/github/issues-pr/LearningGallery/nifty-stock-intelligence)
![GitHub stars](https://img.shields.io/github/stars/LearningGallery/nifty-stock-intelligence?style=social)

**Status**: ✅ Production-Ready (v1.0.0)  
**Last Updated**: January 15, 2024  
**Active Development**: Yes

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=LearningGallery/nifty-stock-intelligence&type=Date)](https://star-history.com/#LearningGallery/nifty-stock-intelligence&Date)

---

<div align="center">

**Made with ❤️ in India for Indian Markets**

If you find this project helpful, please consider giving it a ⭐️

[⬆ Back to Top](#-nifty-stock-intelligence-platform)

</div>
