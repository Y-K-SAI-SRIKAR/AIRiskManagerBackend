import csv
import io
from typing import Any

import httpx


class FileService:

    async def download_csv(
        self,
        file_url: str,
    ) -> bytes:
        """
        Download a CSV file from a presigned URL.
        """

        if not file_url:
            raise ValueError(
                "file_url cannot be empty."
            )

        async with httpx.AsyncClient(
            timeout=300.0
        ) as client:

            response = await client.get(
                file_url
            )

        response.raise_for_status()

        content = response.content

        if not content:
            raise ValueError(
                "Downloaded CSV file is empty."
            )

        return content

    def parse_single_transaction(
        self,
        file_content: bytes,
    ) -> dict[str, Any]:
        """
        Parse exactly one transaction from CSV.
        """

        try:
            text = file_content.decode(
                "utf-8-sig"
            )
        except UnicodeDecodeError as exc:
            raise ValueError(
                "CSV file must be UTF-8 encoded."
            ) from exc

        reader = csv.DictReader(
            io.StringIO(text)
        )

        if not reader.fieldnames:
            raise ValueError(
                "CSV file has no header."
            )

        rows = list(reader)

        if len(rows) != 1:
            raise ValueError(
                "Single transaction analysis requires "
                "exactly one transaction row."
            )

        row = rows[0]

        if not row.get("transaction_id"):
            raise ValueError(
                "transaction_id is required."
            )

        return row


file_service = FileService()