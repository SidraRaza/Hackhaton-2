# Phase V: Advanced Cloud Deployment

## Overview
This repository contains the implementation of Phase V: Advanced Cloud Deployment of the Todo application, transforming it into a production-grade, event-driven, cloud-native AI system with advanced features (priorities, tags, search, recurring tasks, due dates) deployed on DigitalOcean Kubernetes with Kafka and Dapr integration.

## 🚀 Features

### Advanced Task Management
- **Priority System**: Low/Medium/High priority levels with filtering/sorting
- **Tag Management**: Create, assign, filter tasks by tags with autocomplete
- **Search & Filter**: Full-text search on title/description with multiple filters
- **Sorting**: Multi-column sorting with primary/secondary criteria
- **Recurring Tasks**: Daily/weekly/monthly/yearly/custom patterns with series management
- **Due Dates & Reminders**: Date/time picker with browser notifications

### Event-Driven Architecture
- **Kafka Integration**: All operations emit events via Redpanda Cloud
- **Event Schemas**: Standardized event envelope with metadata and idempotency
- **Event Consumers**: Dedicated services for audit, notifications, and recurrence
- **Resilience**: Retry mechanisms and dead letter queues

### Dapr Integration
- **Pub/Sub**: Kafka component for event streaming
- **State Store**: PostgreSQL component for conversation state
- **Service Invocation**: Resilient patterns with retry and circuit breaker
- **Secret Management**: Secure handling of sensitive data
- **Bindings**: Cron bindings for scheduled operations

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│   Dapr Sidecar   │────│   Todo Backend  │
│   (Next.js)     │    │   (Dapr Runtime) │    │   (FastAPI)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                    │
                           ┌──────────────────┐
                           │   Kubernetes     │
                           │   (DOKS)         │
                           └──────────────────┘
                                    │
        ┌─────────────┬─────────────┼─────────────┐
        │             │             │             │
   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │PostgreSQL│   │  Kafka  │   │ Redis   │   │Monitoring│
   │  (Neon) │   │(Redpanda│   │         │   │(Prometheus│
   └─────────┘   │   Cloud)│   │         │   │ ,Grafana)│
                 └─────────┘   └─────────┘   └─────────┘
```

## 🛠️ Tech Stack

- **Frontend**: Next.js 14+, React 19+, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLModel, Python 3.13+
- **Database**: Neon Serverless PostgreSQL
- **Events**: Kafka (Redpanda Cloud)
- **Runtime**: Dapr (Distributed Application Runtime)
- **Orchestration**: Kubernetes (DOKS)
- **Package Management**: Helm Charts
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, Loki

## 📁 Project Structure

```
├── backend/                 # FastAPI application with advanced features
│   ├── models/             # Extended data models with advanced fields
│   ├── services/           # Business logic and Dapr integration
│   ├── api/               # API endpoints with priority, tags, search, etc.
│   ├── events/            # Event schemas and consumers
│   └── tests/             # Unit and integration tests
├── frontend/               # Next.js frontend with enhanced UI
├── k8s/                   # Kubernetes manifests for deployment
├── helm/                  # Helm charts for packaging
├── docker/                # Docker configurations
├── specs/                 # Feature specifications
├── events/                # Event schemas and consumers
├── dapr/                  # Dapr component configurations
├── monitoring/            # Monitoring stack configurations
├── docs/                  # Documentation
└── .github/workflows/     # CI/CD pipeline configurations
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Kubernetes cluster (DigitalOcean DOKS)
- Dapr installed and initialized
- Redpanda Cloud account
- Neon PostgreSQL account

### Local Development
```bash
# Clone the repository
git clone <repository-url>

# Navigate to the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the development server
uvicorn src.main:app --reload
```

### Deployment
```bash
# Deploy Dapr to Kubernetes
dapr init -k

# Apply Kubernetes manifests
kubectl apply -k k8s/base/

# Deploy with Helm
helm install todo-app ./helm/todo-app --values ./helm/todo-app/values-production.yaml
```

## 🧪 Testing

### Run unit tests
```bash
cd backend
pytest tests/unit/
```

### Run integration tests
```bash
cd backend
pytest tests/integration/
```

### Run end-to-end tests
```bash
cd backend
pytest tests/e2e/
```

## 🔒 Security

- JWT-based authentication
- Role-based access control
- Encrypted data transmission (TLS)
- Dapr secret management
- Input validation and sanitization
- Rate limiting and protection against abuse

## 📊 Monitoring

- **Metrics**: Prometheus for collecting application and infrastructure metrics
- **Visualization**: Grafana for dashboards and alerting
- **Logging**: Loki for centralized log aggregation
- **Alerting**: AlertManager for notification management

## 🔄 CI/CD

The project uses GitHub Actions for continuous integration and deployment:
- Automated testing on pull requests
- Security scanning with Trivy
- Multi-environment deployments (staging, production)
- Image building and pushing to registry
- Manual approval for production deployments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Hackathon Team** - Initial work on the Advanced Cloud Deployment

---

Made with ❤️ for the Hackathon II