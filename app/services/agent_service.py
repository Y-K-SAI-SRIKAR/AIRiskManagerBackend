from typing import Any, Dict

import httpx

from app.config import settings


class AgentService:
    """
    Service responsible for communicating with the deployed
    AI Risk Manager Agent.

    The Backend accepts CSV files from the frontend, converts
    the CSV row into the TransactionRequest structure expected
    by the Agent, and sends JSON to the Agent.
    """

    def __init__(self) -> None:
        self.base_url = settings.AGENT_URL.rstrip("/")
        self.timeout = settings.AGENT_TIMEOUT

    async def health(self) -> Dict[str, Any]:
        """
        Check Agent service health.
        """

        url = f"{self.base_url}/health"

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.get(url)

            response.raise_for_status()

            return response.json()

    async def analyze(
        self,
        transaction: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Send a single transaction to the Agent.

        The Agent /analyze endpoint expects JSON,
        NOT multipart/form-data.
        """

        url = f"{self.base_url}/analyze"

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.post(
                url,
                json=transaction,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )

            response.raise_for_status()

            return response.json()

    async def analyze_batch(
        self,
        file_content: bytes,
        filename: str,
    ) -> Dict[str, Any]:
        """
        Send the original CSV file to the Agent batch endpoint.

        The Agent /analyze/batch endpoint expects
        multipart/form-data with a file field.
        """

        url = f"{self.base_url}/analyze/batch"

        files = {
            "file": (
                filename,
                file_content,
                "text/csv",
            )
        }

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.post(
                url,
                files=files,
                headers={
                    "Accept": "application/json",
                },
            )

            response.raise_for_status()

            return response.json()


agent_service = AgentService()