# Quickstart Guide: Advanced Cloud Deployment

## Overview
This guide provides instructions to quickly set up and run the Advanced Cloud Deployment application with event-driven architecture and Dapr integration.

## Prerequisites
- Docker and Docker Compose
- Kubernetes cluster (Minikube for local, DOKS for cloud)
- Dapr CLI installed
- Python 3.13+ and Node.js 20+
- DigitalOcean account (for cloud deployment)
- Redpanda Cloud account (free tier)

## Local Development Setup

### 1. Clone and Initialize
```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Initialize Dapr
dapr init
```

### 2. Set Up Environment Variables
```bash
# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Update with your specific configuration
# For Neon PostgreSQL: DATABASE_URL
# For Redpanda: KAFKA_BROKERS
# For authentication: JWT secrets
```

### 3. Start Local Infrastructure
```bash
# Start all services with Docker Compose
cd docker/compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Run Applications Separately
```bash
# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
dapr run --app-id backend --app-port 8000 --dapr-http-port 3500 -- uvicorn main:app --reload

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

## Event-Driven Architecture Setup

### 1. Configure Kafka/Redpanda
```bash
# For local development, use Docker Compose:
docker-compose -f docker/compose/docker-compose.dev.yml up -d redpanda

# For cloud, configure with Redpanda Cloud credentials
```

### 2. Set Up Event Topics
```bash
# Create required topics
docker exec -t redpanda-0 rpk topic create task-events --brokers=localhost:9092
docker exec -t redpanda-0 rpk topic create task-reminders --brokers=localhost:9092
docker exec -t redpanda-0 rpk topic create task-updates --brokers=localhost:9092
docker exec -t redpanda-0 rpk topic create task-audit --brokers=localhost:9092
```

### 3. Start Event Consumers
```bash
# Start the event consumer services
dapr run --app-id audit-service -- python events/consumers/audit-consumer.py
dapr run --app-id recurrence-service -- python events/consumers/recurrence-consumer.py
dapr run --app-id notification-service -- python events/consumers/notification-consumer.py
```

## Dapr Integration

### 1. Install Dapr on Kubernetes (for deployment)
```bash
# For Minikube/local
minikube start
dapr init -k

# Verify Dapr is running
kubectl get pods -n dapr-system
```

### 2. Deploy Dapr Components
```bash
# Apply Dapr configuration
kubectl apply -f k8s/dapr-components/
```

### 3. Run with Dapr Sidecars
```bash
# Run backend with Dapr sidecar
dapr run --app-id backend \
         --app-port 8000 \
         --dapr-http-port 3500 \
         --dapr-grpc-port 50001 \
         -- uvicorn main:app --host 0.0.0.0 --port 8000

# Run frontend with Dapr sidecar
dapr run --app-id frontend \
         --app-port 3000 \
         --dapr-http-port 3501 \
         -- npm run dev
```

## Database Setup

### 1. Run Database Migrations
```bash
# Navigate to backend directory
cd backend

# Run migrations to create extended schema
alembic revision --autogenerate -m "Add advanced features columns"
alembic upgrade head

# Or directly execute SQL for initial setup:
psql $DATABASE_URL -f migrations/001-initial-schema.sql
psql $DATABASE_URL -f migrations/002-advanced-features.sql
```

### 2. Seed Initial Data (Optional)
```bash
# Run seeding script
python scripts/seed_data.py
```

## Testing the Application

### 1. Unit Tests
```bash
# Backend tests
cd backend
pytest tests/unit/

# Frontend tests
cd frontend
npm test
```

### 2. Integration Tests
```bash
# Run integration tests
cd backend
pytest tests/integration/

# E2E tests
cd frontend
npm run test:e2e
```

### 3. Contract Tests
```bash
# Test API contracts
cd backend
pytest tests/contract/
```

## Cloud Deployment (DigitalOcean Kubernetes)

### 1. Prepare for Cloud Deployment
```bash
# Build Docker images
docker build -t your-dockerhub/todo-backend:latest -f docker/backend.Dockerfile .
docker build -t your-dockerhub/todo-frontend:latest -f docker/frontend.Dockerfile .

# Push to container registry
docker push your-dockerhub/todo-backend:latest
docker push your-dockerhub/todo-frontend:latest
```

### 2. Set Up DigitalOcean Kubernetes
```bash
# Create cluster via DigitalOcean console or CLI
doctl kubernetes cluster create advanced-todo-cluster --region nyc1 --node-pool "name=default;size=s-2vcpu-4gb;count=3"

# Connect to cluster
doctl kubernetes cluster kubeconfig save advanced-todo-cluster
```

### 3. Deploy to DOKS
```bash
# Install Dapr on DOKS
dapr init -k

# Deploy application using Helm
helm install todo-app helm/todo-app/ \
  --values helm/todo-app/values-production.yaml \
  --namespace todo-app --create-namespace

# Deploy Dapr components
kubectl apply -f k8s/dapr-components/
```

### 4. Configure Ingress and TLS
```bash
# Set up LoadBalancer/Ingress
kubectl apply -f k8s/overlays/production/ingress.yaml

# Configure TLS with cert-manager (if available)
kubectl apply -f k8s/overlays/production/certificates.yaml
```

## CI/CD Pipeline Setup

### 1. Configure GitHub Actions
```bash
# The workflow files are located at:
# .github/workflows/ci-cd.yml
# .github/workflows/security-scan.yml
# .github/workflows/deploy.yml

# Set up required secrets in GitHub:
# - DOCKERHUB_USERNAME
# - DOCKERHUB_TOKEN
# - DIGITALOCEAN_ACCESS_TOKEN
# - REDPANDA_API_KEY
# - REDPANDA_API_SECRET
```

### 2. Pipeline Stages
The CI/CD pipeline includes:
- Build: Docker image build and scan
- Test: Unit, integration, and contract tests
- Security: Vulnerability scanning
- Deploy: Staging deployment
- Verify: Health checks and smoke tests
- Promote: Production deployment

## Monitoring & Observability

### 1. Set Up Monitoring Stack
```bash
# Deploy Prometheus and Grafana to Kubernetes
kubectl apply -f monitoring/prometheus/
kubectl apply -f monitoring/grafana/

# Deploy Loki for logging
kubectl apply -f monitoring/loki/
```

### 2. Configure Alerts
```bash
# Set up Alertmanager configuration
kubectl apply -f monitoring/alertmanager/
```

## Advanced Features Configuration

### 1. Enable Priority System
The priority system is enabled by default with three levels:
- Low (green)
- Medium (yellow)
- High (red)

### 2. Configure Tags System
Tags are managed through the UI and API:
- Create tags via POST /api/tags
- Assign tags to tasks via task creation/update

### 3. Set Up Recurring Tasks
The recurrence engine handles:
- Daily, weekly, monthly, yearly patterns
- Custom cron expressions
- End conditions (count, date, indefinite)

### 4. Configure Reminders
Reminder system includes:
- Multiple reminder times per task
- Browser notifications
- Email notifications (configurable)

## Troubleshooting

### Common Issues

1. **Dapr Sidecar Not Starting**
   ```bash
   # Check Dapr logs
   dapr logs <app-id>

   # Restart Dapr
   dapr uninstall --all
   dapr init
   ```

2. **Kafka Connection Issues**
   ```bash
   # Verify Kafka is running
   docker exec -t redpanda-0 rpk topic list

   # Check broker connectivity
   docker exec -t redpanda-0 rpk cluster info
   ```

3. **Database Connection Problems**
   ```bash
   # Test connection
   psql $DATABASE_URL -c "SELECT 1;"

   # Check if migrations ran successfully
   alembic current
   ```

4. **Kubernetes Deployment Failures**
   ```bash
   # Check pod status
   kubectl get pods --all-namespaces

   # Check logs
   kubectl logs <pod-name> -n <namespace>

   # Check events
   kubectl get events --sort-by=.metadata.creationTimestamp
   ```

### Useful Commands
```bash
# Check Dapr status
dapr status -k

# List Dapr applications
dapr list -k

# Get Dapr sidecar logs
dapr logs <app-id> -k

# Check Kubernetes resources
kubectl get all -n todo-app

# Port forward for local testing
kubectl port-forward svc/backend-service 8000:80 -n todo-app
```

## Next Steps
1. Review the complete API documentation
2. Set up monitoring dashboards
3. Configure backup and disaster recovery
4. Implement performance optimizations
5. Set up automated scaling