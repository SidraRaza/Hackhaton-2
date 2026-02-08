"""
Kafka/Redpanda Configuration for Phase V: Advanced Cloud Deployment

This module contains the configuration for connecting to Redpanda Cloud
and setting up Kafka producers and consumers for the event-driven architecture.
"""

from typing import Optional
from pydantic import BaseModel
import os


class KafkaConfig(BaseModel):
    """Configuration for Kafka/Redpanda connection"""

    # Kafka/Redpanda settings
    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    security_protocol: str = os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
    sasl_mechanism: Optional[str] = os.getenv("KAFKA_SASL_MECHANISM")
    sasl_username: Optional[str] = os.getenv("KAFKA_SASL_USERNAME")
    sasl_password: Optional[str] = os.getenv("KAFKA_SASL_PASSWORD")

    # Topic configuration
    task_events_topic: str = "task-events"
    task_reminders_topic: str = "task-reminders"
    task_updates_topic: str = "task-updates"
    task_audit_topic: str = "task-audit"

    # Consumer settings
    consumer_group: str = "todo-group"
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = True
    heartbeat_interval_ms: int = 3000
    session_timeout_ms: int = 30000

    # Producer settings
    acks: str = "all"
    retries: int = 3
    linger_ms: int = 5
    batch_size: int = 16384

    # Serialization
    value_serializer: str = "json"
    key_serializer: str = "string"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Default configuration instance
kafka_config = KafkaConfig()


def get_kafka_producer_config() -> dict:
    """Get configuration for Kafka producer"""
    config = {
        "bootstrap_servers": kafka_config.bootstrap_servers,
        "acks": kafka_config.acks,
        "retries": kafka_config.retries,
        "linger_ms": kafka_config.linger_ms,
        "batch_size": kafka_config.batch_size,
    }

    # Add security settings if configured
    if kafka_config.security_protocol.upper() != "PLAINTEXT":
        config.update({
            "security_protocol": kafka_config.security_protocol,
            "sasl_mechanism": kafka_config.sasl_mechanism,
            "sasl_plain_username": kafka_config.sasl_username,
            "sasl_plain_password": kafka_config.sasl_password,
        })

    return config


def get_kafka_consumer_config() -> dict:
    """Get configuration for Kafka consumer"""
    config = {
        "bootstrap_servers": kafka_config.bootstrap_servers,
        "group_id": kafka_config.consumer_group,
        "auto_offset_reset": kafka_config.auto_offset_reset,
        "enable_auto_commit": kafka_config.enable_auto_commit,
        "heartbeat_interval_ms": kafka_config.heartbeat_interval_ms,
        "session_timeout_ms": kafka_config.session_timeout_ms,
    }

    # Add security settings if configured
    if kafka_config.security_protocol.upper() != "PLAINTEXT":
        config.update({
            "security_protocol": kafka_config.security_protocol,
            "sasl_mechanism": kafka_config.sasl_mechanism,
            "sasl_plain_username": kafka_config.sasl_username,
            "sasl_plain_password": kafka_config.sasl_password,
        })

    return config


# Topic definitions
TOPIC_DEFINITIONS = {
    kafka_config.task_events_topic: {
        "partitions": 3,
        "replication_factor": 1,
        "configs": {
            "retention.ms": "604800000",  # 7 days
            "cleanup.policy": "delete",
            "compression.type": "lz4",
        }
    },
    kafka_config.task_reminders_topic: {
        "partitions": 2,
        "replication_factor": 1,
        "configs": {
            "retention.ms": "2592000000",  # 30 days
            "cleanup.policy": "delete",
            "segment.bytes": "1073741824",  # 1GB
        }
    },
    kafka_config.task_updates_topic: {
        "partitions": 3,
        "replication_factor": 1,
        "configs": {
            "retention.ms": "86400000",  # 1 day
            "cleanup.policy": "delete",
            "segment.ms": "3600000",  # 1 hour segments
        }
    },
    kafka_config.task_audit_topic: {
        "partitions": 1,
        "replication_factor": 1,
        "configs": {
            "retention.ms": "31536000000",  # 365 days
            "cleanup.policy": "compact",  # Keep latest value per key
            "delete.retention.ms": "86400000",
            "min.cleanable.dirty.ratio": "0.5",
        }
    }
}


def create_required_topics(admin_client):
    """Create required Kafka topics if they don't exist"""
    from kafka.admin import NewTopic

    existing_topics = admin_client.list_consumer_groups()

    topics_to_create = []
    for topic_name, topic_config in TOPIC_DEFINITIONS.items():
        # Check if topic already exists
        if topic_name not in existing_topics:
            new_topic = NewTopic(
                name=topic_name,
                num_partitions=topic_config["partitions"],
                replication_factor=topic_config["replication_factor"],
                topic_configs=topic_config["configs"]
            )
            topics_to_create.append(new_topic)

    if topics_to_create:
        admin_client.create_topics(topics_to_create)
        print(f"Created {len(topics_to_create)} new topics")
    else:
        print("All required topics already exist")


# Event schema definitions
EVENT_SCHEMA = {
    "task.created": {
        "type": "object",
        "required": ["event_id", "event_type", "timestamp", "source", "data"],
        "properties": {
            "event_id": {"type": "string", "format": "uuid"},
            "event_type": {"type": "string", "const": "task.created"},
            "event_version": {"type": "string", "default": "1.0"},
            "timestamp": {"type": "string", "format": "date-time"},
            "source": {"type": "string"},
            "data": {
                "type": "object",
                "required": ["task_id", "user_id", "title"],
                "properties": {
                    "task_id": {"type": "integer"},
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "due_date": {"type": "string", "format": "date-time"},
                    "recurrence_pattern": {"type": "string"},
                    "recurrence_config": {"type": "object"},
                    "tag_ids": {
                        "type": "array",
                        "items": {"type": "integer"}
                    }
                }
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "correlation_id": {"type": "string", "format": "uuid"},
                    "user_id": {"type": "string"},
                    "trace_id": {"type": "string"}
                }
            }
        }
    },
    "task.updated": {
        "type": "object",
        "required": ["event_id", "event_type", "timestamp", "source", "data"],
        "properties": {
            "event_id": {"type": "string", "format": "uuid"},
            "event_type": {"type": "string", "const": "task.updated"},
            "event_version": {"type": "string", "default": "1.0"},
            "timestamp": {"type": "string", "format": "date-time"},
            "source": {"type": "string"},
            "data": {
                "type": "object",
                "required": ["task_id", "user_id"],
                "properties": {
                    "task_id": {"type": "integer"},
                    "user_id": {"type": "string"},
                    "changes": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "old": {"type": "any"},
                                "new": {"type": "any"}
                            }
                        }
                    },
                    "updated_fields": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "correlation_id": {"type": "string", "format": "uuid"},
                    "user_id": {"type": "string"},
                    "trace_id": {"type": "string"}
                }
            }
        }
    }
    # Additional event schemas would be defined similarly
}