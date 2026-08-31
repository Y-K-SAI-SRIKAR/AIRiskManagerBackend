import csv
import io
from typing import Any


class CSVService:

    # ======================================================
    # Required ML features
    # ======================================================

    REQUIRED_FEATURES = {
        "TransactionDT",
        "TransactionAmt",
        "ProductCD",
        "card1",
        "card2",
        "card3",
        "card4",
        "card5",
        "card6",
        "addr1",
        "addr2",
        "dist1",
        "P_emaildomain",
        "R_emaildomain",
        "C2",
        "C3",
        "C9",
        "D1",
        "D3",
        "D5",
        "D11",
        "D15",
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
        "M6",
        "M7",
        "M8",
        "M9",
        "V1",
        "V3",
        "V5",
        "V6",
        "V12",
        "V14",
        "V20",
        "V23",
        "V26",
        "V29",
        "V35",
        "V38",
        "V41",
        "V45",
        "V47",
        "V52",
        "V53",
        "V56",
        "V62",
        "V65",
        "V67",
        "V68",
        "V83",
        "V86",
        "V89",
        "V107",
        "V111",
        "V117",
        "V120",
        "V123",
        "V169",
        "V173",
        "V174",
        "V197",
        "V199",
        "V220",
        "V222",
        "V223",
        "V235",
        "V239",
        "V240",
        "V247",
        "V257",
        "V262",
        "V271",
        "V281",
        "V283",
        "V284",
        "V286",
        "V287",
        "V289",
        "V290",
        "V301",
        "V302",
        "V305",
        "V312",
        "V315",
        "id_01",
        "id_02",
        "id_05",
        "id_06",
        "id_11",
        "id_12",
        "id_13",
        "id_15",
        "id_16",
        "id_17",
        "id_19",
        "id_20",
        "id_28",
        "id_29",
        "id_31",
        "id_35",
        "id_36",
        "id_37",
        "id_38",
        "TransactionHour",
        "TransactionDay",
        "TransactionWeek",
        "TransactionWeekday",
        "TransactionAmt_Log",
        "card1_freq",
        "EmailDomainMatch",
        "P_email_Missing",
        "R_email_Missing",
        "CardType",
    }

    # These are allowed in the dataset but are not sent
    # to the inference model.

    OPTIONAL_DATASET_COLUMNS = {
        "isFraud",
        "TransactionAmt_Bin",
    }

    # ======================================================
    # Internal CSV reader
    # ======================================================

    def _read_csv(
        self,
        file_content: bytes,
    ) -> list[dict[str, Any]]:

        if not file_content:

            raise ValueError(
                "CSV file is empty."
            )

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

        if not rows:

            raise ValueError(
                "CSV file contains no transaction rows."
            )

        # --------------------------------------------------
        # Normalize headers
        # --------------------------------------------------

        normalized_headers = [
            header.strip()
            for header in reader.fieldnames
        ]

        rows = [
            {
                normalized_headers[index]:
                    value
                for index, value
                in enumerate(row.values())
            }
            for row in rows
        ]

        return rows

    # ======================================================
    # Validate schema
    # ======================================================

    def _validate_schema(
        self,
        rows: list[dict[str, Any]],
    ) -> None:

        if not rows:

            raise ValueError(
                "CSV contains no transaction rows."
            )

        actual_columns = set(
            rows[0].keys()
        )

        # --------------------------------------------------
        # Missing model features
        # --------------------------------------------------

        missing = (
            self.REQUIRED_FEATURES
            - actual_columns
        )

        if missing:

            raise ValueError(
                "CSV format is invalid. "
                "Please upload a CSV matching the supported "
                "transaction format."
            )

        # --------------------------------------------------
        # Unexpected columns
        # --------------------------------------------------

        allowed = (
            self.REQUIRED_FEATURES
            | self.OPTIONAL_DATASET_COLUMNS
        )

        unexpected = (
            actual_columns
            - allowed
        )

        if unexpected:

            raise ValueError(
                "Unexpected CSV columns: "
                + ", ".join(
                    sorted(unexpected)
                )
            )

    # ======================================================
    # Single transaction
    # ======================================================

    def validate_single(
        self,
        file_content: bytes,
    ) -> dict[str, Any]:

        rows = self._read_csv(
            file_content
        )

        if len(rows) != 1:

            raise ValueError(
                "Single transaction analysis requires "
                "exactly one transaction row."
            )

        self._validate_schema(
            rows
        )

        return rows[0]

    # ======================================================
    # Batch transactions
    # ======================================================

    def validate_batch(
        self,
        file_content: bytes,
    ) -> list[dict[str, Any]]:

        rows = self._read_csv(
            file_content
        )

        self._validate_schema(
            rows
        )

        return rows


csv_service = CSVService()