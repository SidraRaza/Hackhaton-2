"""
Dapr Secrets Service for Phase V: Advanced Cloud Deployment
Provides access to Dapr secret store for managing sensitive data
"""
import logging
from typing import Dict, Optional, Union
from dapr.clients import DaprClient

logger = logging.getLogger(__name__)


class DaprSecretsService:
    """
    Service for managing secrets through Dapr secret store
    Provides methods to securely access sensitive configuration data
    """

    def __init__(self, secret_store_name: str = "secrets-store"):
        """
        Initialize the Dapr Secrets Service

        Args:
            secret_store_name: Name of the Dapr secret store component to use
        """
        self.secret_store_name = secret_store_name

    def get_secret(self, key: str, metadata: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Get a secret from the Dapr secret store

        Args:
            key: Key of the secret to retrieve
            metadata: Optional metadata for the secret operation

        Returns:
            Secret value as string or None if not found
        """
        try:
            with DaprClient() as client:
                response = client.get_secret(
                    store_name=self.secret_store_name,
                    key=key,
                    metadata=metadata
                )

            # Extract the secret value from the response
            secrets = response.secrets
            if key in secrets:
                return secrets[key]

            return None

        except Exception as e:
            logger.error(f"Failed to get secret for key {key}: {str(e)}")
            return None

    def get_bulk_secrets(
        self,
        keys: Optional[list] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Get multiple secrets from the Dapr secret store

        Args:
            keys: Optional list of keys to retrieve (None means all accessible secrets)
            metadata: Optional metadata for the secret operation

        Returns:
            Dictionary mapping keys to their secret values
        """
        try:
            with DaprClient() as client:
                response = client.get_bulk_secret(
                    store_name=self.secret_store_name,
                    secret_names=keys,
                    metadata=metadata
                )

            # Extract secrets from the response
            secrets = {}
            for key, value in response.secrets.items():
                secrets[key] = value

            return secrets

        except Exception as e:
            logger.error(f"Failed to get bulk secrets: {str(e)}")
            return {}

    def get_database_url(self) -> Optional[str]:
        """
        Get the database URL from secrets

        Returns:
            Database URL string or None if not found
        """
        return self.get_secret("database-url")

    def get_kafka_brokers(self) -> Optional[str]:
        """
        Get the Kafka brokers configuration from secrets

        Returns:
            Kafka brokers string or None if not found
        """
        return self.get_secret("kafka-brokers")

    def get_jwt_secret(self) -> Optional[str]:
        """
        Get the JWT secret for token signing from secrets

        Returns:
            JWT secret string or None if not found
        """
        return self.get_secret("jwt-secret")

    def get_encryption_key(self) -> Optional[str]:
        """
        Get the encryption key from secrets

        Returns:
            Encryption key string or None if not found
        """
        return self.get_secret("encryption-key")

    def get_api_keys(self) -> Dict[str, str]:
        """
        Get various API keys from secrets

        Returns:
            Dictionary of API keys
        """
        api_keys = {}

        # Get specific API keys
        openai_key = self.get_secret("openai-api-key")
        if openai_key:
            api_keys["openai"] = openai_key

        google_key = self.get_secret("google-api-key")
        if google_key:
            api_keys["google"] = google_key

        slack_key = self.get_secret("slack-webhook-url")
        if slack_key:
            api_keys["slack"] = slack_key

        return api_keys

    def get_external_service_credentials(self) -> Dict[str, str]:
        """
        Get credentials for external services from secrets

        Returns:
            Dictionary of service credentials
        """
        credentials = {}

        # Get various service credentials
        redis_password = self.get_secret("redis-password")
        if redis_password:
            credentials["redis"] = redis_password

        pg_password = self.get_secret("postgres-password")
        if pg_password:
            credentials["postgres"] = pg_password

        aws_access_key = self.get_secret("aws-access-key-id")
        if aws_access_key:
            credentials["aws_access_key_id"] = aws_access_key

        aws_secret_key = self.get_secret("aws-secret-access-key")
        if aws_secret_key:
            credentials["aws_secret_access_key"] = aws_secret_key

        return credentials

    def get_smtp_config(self) -> Dict[str, str]:
        """
        Get SMTP configuration from secrets

        Returns:
            Dictionary with SMTP configuration
        """
        smtp_config = {}

        smtp_host = self.get_secret("smtp-host")
        if smtp_host:
            smtp_config["host"] = smtp_host

        smtp_port = self.get_secret("smtp-port")
        if smtp_port:
            smtp_config["port"] = smtp_port

        smtp_username = self.get_secret("smtp-username")
        if smtp_username:
            smtp_config["username"] = smtp_username

        smtp_password = self.get_secret("smtp-password")
        if smtp_password:
            smtp_config["password"] = smtp_password

        smtp_from_email = self.get_secret("smtp-from-email")
        if smtp_from_email:
            smtp_config["from_email"] = smtp_from_email

        return smtp_config

    def get_oauth_secrets(self) -> Dict[str, str]:
        """
        Get OAuth provider secrets from Dapr secrets store

        Returns:
            Dictionary with OAuth secrets
        """
        oauth_secrets = {}

        github_client_id = self.get_secret("github-client-id")
        if github_client_id:
            oauth_secrets["github_client_id"] = github_client_id

        github_client_secret = self.get_secret("github-client-secret")
        if github_client_secret:
            oauth_secrets["github_client_secret"] = github_client_secret

        google_client_id = self.get_secret("google-client-id")
        if google_client_id:
            oauth_secrets["google_client_id"] = google_client_id

        google_client_secret = self.get_secret("google-client-secret")
        if google_client_secret:
            oauth_secrets["google_client_secret"] = google_client_secret

        return oauth_secrets

    def get_third_party_api_secrets(self) -> Dict[str, str]:
        """
        Get third party API secrets from Dapr secrets store

        Returns:
            Dictionary with third party API secrets
        """
        third_party_secrets = {}

        # Add any other third-party API secrets here
        stripe_secret = self.get_secret("stripe-secret-key")
        if stripe_secret:
            third_party_secrets["stripe"] = stripe_secret

        paypal_secret = self.get_secret("paypal-client-secret")
        if paypal_secret:
            third_party_secrets["paypal"] = paypal_secret

        return third_party_secrets


# Global instance for easy access
dapr_secrets_service = DaprSecretsService()


def get_dapr_secrets_service() -> DaprSecretsService:
    """
    Get the global Dapr Secrets Service instance

    Returns:
        DaprSecretsService instance
    """
    return dapr_secrets_service