
# Intelligence Reliability Platform

A production-grade observability and reliability platform for Large Language Models (LLMs). Built with FastAPI (Python) backend and React (Vite) frontend, this system provides comprehensive monitoring, evaluation, and assurance for AI-powered applications.

## 🏗️ Architecture Overview

The platform is structured around three core planes:

### Control Plane
- **Prompt Management**: Version-controlled behavioral prompts with risk levels and constraints
- **Semantic Versioning**: Track prompt evolution with MAJOR.MINOR.PATCH semantics
- **Behavioral Guards**: Model constraints and fallback policies

### Data Plane
- **Inference Router**: Multi-model fallback chains (OpenAI → Ollama → Mock)
- **Trace Logging**: Comprehensive inference metadata and performance metrics
- **Real-time Streaming**: Asynchronous evaluation pipelines

### Intelligence Plane
- **Ensemble Judging**: Parallel evaluation using GPT-4, GPT-3.5, and Mock judges
- **Hallucination Detection**: Multi-layer semantic auditing
- **Drift Monitoring**: Statistical analysis of quality trends

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm/yarn
- (Optional) Ollama for local LLM inference

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (`.env`):
```bash
OPENAI_API_KEY=your-openai-key-here
OLLAMA_URL=http://localhost:11434  # Optional for local models
```

4. Initialize database:
```bash
python -c "from app.db.init_db import init_db; init_db()"
```

5. Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## 🔧 Core Features

### 1. Prompt Management
- Create and version behavioral prompts
- Define risk levels (Low/Medium/High/Critical)
- Set model constraints and fallback chains
- Template-based variable interpolation

### 2. Multi-Model Inference
Support for multiple LLM providers:
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Ollama**: Local models (Llama, Mistral, etc.)
- **Mock**: Development/testing provider

Automatic fallback mechanism ensures inference continuity even when primary providers fail.

### 3. Automated Evaluation
Parallel evaluation pipeline with:
- **LLM-as-Judge**: GPT-4 evaluation with structured scoring
- **Hallucination Detection**: Semantic similarity and epistemic analysis
- **Quality Scoring**: Correctness, completeness, safety, clarity metrics

### 4. Real-time Monitoring
- Live dashboard with key metrics
- Inference trace explorer
- Performance analytics and cost tracking
- Drift detection and alerting

## 📊 API Endpoints

### Inference
```
POST /api/v1/inference/run
```
Run a prompt through configured LLM providers.

### Metrics
```
GET /api/v1/metrics/stats
GET /api/v1/metrics/by-version
```
Retrieve platform statistics and version-specific metrics.

### Traces
```
GET /api/v1/traces
GET /api/v1/traces/{trace_id}
GET /api/v1/traces/{trace_id}/evaluations
```
Access detailed inference logs and evaluation results.

### Prompts
```
GET /api/v1/prompts/
POST /api/v1/prompts/
```
Manage prompt versions and configurations.

## 🛠️ Development Workflow

### Adding New Providers
1. Extend `LLMProvider` base class in `backend/app/services/llm_providers/base.py`
2. Implement `run_inference()` method
3. Register in `inference_service.py`

### Custom Evaluators
1. Create evaluator class implementing evaluation interface
2. Register in `evaluation_service.py`
3. Add to evaluation DAG

### Database Schema Changes
1. Create migration in `backend/alembic/versions/`
2. Update SQLAlchemy models
3. Run `alembic upgrade head`

## 📈 Monitoring & Observability

### Key Metrics Tracked
- **Latency**: End-to-end inference time
- **Cost**: USD expenditure per inference
- **Quality Score**: Average judge evaluation
- **Hallucination Rate**: Semantic drift probability
- **Throughput**: Requests per second

### Alerting
Configurable thresholds for:
- High latency (>500ms)
- Cost anomalies
- Quality degradation
- Hallucination spikes

## 🔒 Security & Compliance

### Authentication
Role-based access control (RBAC) with:
- Admin: Full platform access
- Developer: Inference and evaluation access
- Viewer: Read-only dashboard access

### Data Protection
- Encrypted database storage
- Audit logs for all operations
- GDPR-compliant data retention policies

## 🧪 Testing

### Unit Tests
```bash
cd backend
pytest tests/
```

### Integration Tests
```bash
python scripts/run_prompt_test.py --prompt "Product Description" --version "1.0.0"
```

### Load Testing
```bash
locust -f locustfile.py
```

## 🚢 Deployment

### Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Kubernetes
Helm charts available in `deploy/helm/`

### Cloud Providers
- AWS: ECS/EKS with Terraform modules
- GCP: Cloud Run with Cloud SQL
- Azure: AKS with managed identities

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style
- Backend: Black formatter, mypy type checking
- Frontend: ESLint with Airbnb style guide
- Commits: Conventional commits format

## 📚 Documentation

- [API Reference](API_REFERENCE.md)
- [Architecture Deep Dive](ARCHITECTURE.md)
- [Deployment Guide](docs/deployment.md)
- [Contributor Guide](docs/contributing.md)

## 📞 Support

- Issues: [GitHub Issues](https://github.com/your-org/llm-reliability-platform/issues)
- Discussions: [GitHub Discussions](https://github.com/your-org/llm-reliability-platform/discussions)
- Email: support@your-org.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT model APIs
- Ollama community for local LLM support
- FastAPI team for excellent framework
- React team for frontend foundation

---

*Built with ❤️ for reliable AI systems*
