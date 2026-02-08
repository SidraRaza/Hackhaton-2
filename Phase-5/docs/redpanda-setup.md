# Redpanda Cloud Setup Guide

## Overview
This document provides instructions for setting up Redpanda Cloud for the Advanced Cloud Deployment Phase. Redpanda serves as our Kafka-compatible event streaming platform for the event-driven architecture.

## Prerequisites
- DigitalOcean account with available credits
- Redpanda Cloud account (free tier available)
- `rpk` CLI tool installed (`curl -L https://redpanda.com/releases/rpk/latest/install.sh | bash`)

## Creating a Redpanda Cloud Cluster

### 1. Sign Up for Redpanda Cloud
1. Visit [Redpanda Cloud](https://cloud.redpanda.com/)
2. Sign up using your preferred method (Google, GitHub, or email)
3. Verify your email address
4. Complete the onboarding process

### 2. Create a Free-Tier Cluster
1. From the dashboard, click "Create Cluster"
2. Select the "Free" plan
3. Choose a region closest to your users
4. Configure cluster settings:
   - Name: `todo-phase5-cluster`
   - Region: Select based on user location
   - Tier: Free
5. Click "Create Cluster"
6. Wait for cluster to be provisioned (typically 2-3 minutes)

### 3. Get Connection Details
1. Once the cluster is ready, click on it to view details
2. Navigate to the "Connect" tab
3. Copy the connection details:
   - Bootstrap servers
   - SASL mechanism (if enabled)
   - Username and password (if using SASL)

### 4. Create Required Topics
Use the following command to create the required topics for the todo application:

```bash
# Create task events topic
rpk topic create task-events \
  --brokers=<YOUR_BROKERS> \
  --partitions=3 \
  --config retention.ms=604800000  # 7 days

# Create task reminders topic
rpk topic create task-reminders \
  --brokers=<YOUR_BROKERS> \
  --partitions=2 \
  --config retention.ms=2592000000  # 30 days

# Create task updates topic
rpk topic create task-updates \
  --brokers=<YOUR_BROKERS> \
  --partitions=3 \
  --config retention.ms=86400000  # 1 day

# Create task audit topic
rpk topic create task-audit \
  --brokers=<YOUR_BROKERS> \
  --partitions=1 \
  --config cleanup.policy=compact \
  --config retention.ms=31536000000  # 365 days
```

## Local Development Configuration

### 1. Docker Compose for Local Development
For local development, you can use Redpanda in Docker:

```yaml
# docker-compose.redpanda.yml
version: '3.8'
services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:v23.2.15
    command:
      - redpanda
      - start
      - --smp
      - '1'
      - --memory
      - 1G
      - --reserve-memory
      - 0M
      - --overprovisioned
      - --node-id
      - '0'
      - --kafka-addr
      - PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092
      - --advertise-kafka-addr
      - PLAINTEXT://redpanda:29092,OUTSIDE://localhost:9092
    ports:
      - "9092:9092"
      - "9644:9644"
```

### 2. Environment Variables
Set the following environment variables in your `.env` files:

```bash
# For local development
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# For Redpanda Cloud (replace with your actual values)
KAFKA_BOOTSTRAP_SERVERS=pkc-abc123.us-west-2.aws.confluent.cloud:9092
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=your_username
KAFKA_SASL_PASSWORD=your_password
```

## Integration with Dapr

### 1. Dapr Component Configuration
Create a Dapr component for Kafka/Redpanda integration:

```yaml
# .dapr/components/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "pkc-abc123.us-west-2.aws.confluent.cloud:9092"  # Replace with your brokers
  - name: consumerGroup
    value: "todo-group"
  - name: authType
    value: "password"
  - name: username
    value: "your_username"  # Replace with your username
  - name: password
    value: "your_password"  # Replace with your password
  - name: publishTopicConfigs
    value: |
      {
        "compression.type": "snappy",
        "acks": "all"
      }
```

## Event Schema Registry

### 1. Setting up Schema Registry (Optional)
If using Redpanda's schema registry:

1. In the Redpanda Cloud console, navigate to "Schema Registry"
2. Enable schema registry for your cluster
3. Use the provided endpoint URL for schema validation

### 2. Schema Registry Configuration
```bash
# Example for registering a schema
curl -X POST \
  https://your-cluster-sr.redpanda.com/subjects/task-created-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schema": "{...}",  # Your JSON schema
    "schemaType": "JSON"
  }'
```

## Security Best Practices

### 1. Credential Management
- Never hardcode credentials in source code
- Use environment variables or Dapr secret stores
- Rotate credentials regularly
- Use the principle of least privilege

### 2. Network Security
- Enable SSL/TLS encryption
- Use private networking when possible
- Implement IP whitelisting if available in your plan

## Monitoring and Observing

### 1. Checking Cluster Health
```bash
# Check cluster info
rpk cluster info --brokers <YOUR_BROKERS>

# List topics
rpk topic list --brokers <YOUR_BROKERS>

# Check consumer group status
rpk group list --brokers <YOUR_BROKERS>
```

### 2. Observing Event Flow
```bash
# Consume events from a topic
rpk topic consume task-events --brokers <YOUR_BROKERS> -f '%v\n'

# Produce a test event
echo '{"event_type": "test", "data": {"message": "hello world"}}' | rpk topic produce task-events --brokers <YOUR_BROKERS>
```

## Troubleshooting

### 1. Common Issues

**Connection Refused Errors**:
- Verify bootstrap servers are correct
- Check firewall settings
- Ensure security protocol matches cluster configuration

**Authentication Failures**:
- Verify username/password are correct
- Check that SASL mechanism matches cluster settings
- Ensure credentials have appropriate permissions

**Topic Creation Failures**:
- Verify you have topic creation permissions
- Check if cluster is in a read-only state
- Ensure topic name follows naming conventions

### 2. Debugging Tools
```bash
# Test connection
rpk cluster info --brokers <YOUR_BROKERS> --verbose

# Check logs in Redpanda Cloud console
# Use the monitoring dashboard to observe cluster metrics
```

## Cost Management

### 1. Free Tier Limitations
- 5GB storage
- 100MBps throughput
- 3 topics maximum
- 100,000 partitioned reads/writes per day

### 2. Optimizing Usage
- Set appropriate retention periods for each topic
- Use compression to reduce storage needs
- Monitor usage through Redpanda Cloud dashboard
- Plan for upgrade when approaching limits

## Next Steps
1. Complete Redpanda Cloud setup following the steps above
2. Update application configuration with cluster details
3. Test event publishing and consumption locally
4. Verify integration with Dapr components
5. Deploy to staging environment with cloud Redpanda