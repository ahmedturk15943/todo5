"""Dapr Secrets Store client wrapper for secure credential management."""

import httpx
from typing import Any, Dict, Optional


class DaprSecretsClient:
    """Client for Dapr Secrets Store component."""

    def __init__(self, dapr_port: int = 3500, store_name: str = "secretstore"):
        """Initialize Dapr Secrets Store client.

        Args:
            dapr_port: Dapr sidecar HTTP port (default: 3500)
            store_name: Name of Dapr Secrets Store component (default: "secretstore")
        """
        self.dapr_url = f"http://localhost:{dapr_port}"
        self.store_name = store_name

    async def get_secret(
        self,
        secret_name: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, str]]:
        """Get secret from Dapr secrets store.

        Args:
            secret_name: Name of the secret
            metadata: Optional metadata for secret retrieval

        Returns:
            Secret value(s) as dictionary or None if not found
        """
        url = f"{self.dapr_url}/v1.0/secrets/{self.store_name}/{secret_name}"

        params = {}
        if metadata:
            for key, value in metadata.items():
                params[f"metadata.{key}"] = value

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    timeout=5.0
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Failed to get secret {secret_name}: {e}")
            return None

    async def get_database_connection_string(self) -> Optional[str]:
        """Get database connection string from secrets.

        Returns:
            Connection string or None if not found
        """
        secret = await self.get_secret("postgres-secret")

        if secret and "connectionString" in secret:
            return secret["connectionString"]
        return None

    async def get_api_key(self, service_name: str) -> Optional[str]:
        """Get API key for external service.

        Args:
            service_name: Name of the service (e.g., "gemini", "openai")

        Returns:
            API key or None if not found
        """
        secret_name = f"{service_name}-api-key"
        secret = await self.get_secret(secret_name)

        if secret and "key" in secret:
            return secret["key"]
        return None
