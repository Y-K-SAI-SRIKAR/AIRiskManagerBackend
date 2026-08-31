import csv
import io


class CSVService:

    REQUIRED_TRANSACTION_COLUMNS = {
        "transaction_id",
        "customer_id",
        "amount",
        "currency",
        "timestamp",
    }

    def _read(
        self,
        file_content: bytes,
    ) -> list[dict]:

        try:
            text = file_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError(
                "CSV file must be UTF-8 encoded."
            )

        reader = csv.DictReader(
            io.StringIO(text)
        )

        if not reader.fieldnames:
            raise ValueError(
                "CSV file is empty or has no header."
            )

        rows = list(reader)

        if not rows:
            raise ValueError(
                "CSV file contains no transaction data."
            )

        return rows

    def validate_single(
        self,
        file_content: bytes,
    ) -> dict:

        rows = self._read(file_content)

        if len(rows) != 1:
            raise ValueError(
                "Single transaction analysis requires "
                "exactly one transaction row."
            )

        missing = (
            self.REQUIRED_TRANSACTION_COLUMNS
            - set(rows[0].keys())
        )

        if missing:
            raise ValueError(
                "Missing required transaction columns: "
                + ", ".join(sorted(missing))
            )

        transaction_id = rows[0].get(
            "transaction_id"
        )

        if not transaction_id:
            raise ValueError(
                "transaction_id cannot be empty."
            )

        return rows[0]

    def validate_batch(
        self,
        file_content: bytes,
    ) -> list[dict]:

        rows = self._read(file_content)

        missing = (
            self.REQUIRED_TRANSACTION_COLUMNS
            - set(rows[0].keys())
        )

        if missing:
            raise ValueError(
                "Missing required transaction columns: "
                + ", ".join(sorted(missing))
            )

        transaction_ids = set()

        for row in rows:

            transaction_id = row.get(
                "transaction_id"
            )

            if not transaction_id:
                raise ValueError(
                    "Every transaction must have "
                    "a transaction_id."
                )

            if transaction_id in transaction_ids:
                raise ValueError(
                    f"Duplicate transaction_id: "
                    f"{transaction_id}"
                )

            transaction_ids.add(
                transaction_id
            )

        return rows


csv_service = CSVService()