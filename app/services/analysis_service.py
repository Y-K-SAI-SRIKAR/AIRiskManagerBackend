from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.analysis import AnalysisResult
from app.models.analysis_batch import AnalysisBatch


class AnalysisService:

    # ==========================================================
    # Single Analysis
    # ==========================================================

    def save_analysis(
        self,
        db: Session,
        result: dict[str, Any],
    ) -> AnalysisResult:

        decision = result.get(
            "decision",
            {},
        )

        evidence = result.get(
            "evidence",
            {},
        )

        transaction_id = result.get(
            "transaction_id"
        )

        customer_id = result.get(
            "customer_id"
        )

        # ------------------------------------------------------
        # Validate required analysis identifiers
        # ------------------------------------------------------

        if not transaction_id:
            raise ValueError(
                "Analysis result is missing transaction_id."
            )

        if not customer_id:
            raise ValueError(
                "Analysis result is missing customer_id."
            )

        # ------------------------------------------------------
        # Look for existing analysis
        # ------------------------------------------------------

        existing = db.scalar(
            select(AnalysisResult).where(
                AnalysisResult.transaction_id
                == transaction_id
            )
        )

        # ------------------------------------------------------
        # Update existing analysis
        # ------------------------------------------------------

        if existing:

            existing.success = bool(
                result.get(
                    "success",
                    False,
                )
            )

            existing.risk_level = decision.get(
                "risk_level"
            )

            existing.action = decision.get(
                "action"
            )

            existing.confidence = decision.get(
                "confidence"
            )

            existing.ml_risk_score = evidence.get(
                "ml_risk_score"
            )

            existing.anomaly_detected = evidence.get(
                "anomaly_detected"
            )

            existing.velocity_risk = evidence.get(
                "velocity_risk"
            )

            existing.customer_risk = evidence.get(
                "customer_risk"
            )

            existing.transaction_risk = evidence.get(
                "transaction_risk"
            )

            existing.triggered_rules = evidence.get(
                "triggered_rules",
                [],
            )

            existing.explanation = result.get(
                "explanation"
            )

            existing.analysis_metadata = result.get(
                "metadata",
                {},
            )

            try:

                db.commit()

                db.refresh(existing)

                return existing

            except Exception:

                db.rollback()

                raise

        # ------------------------------------------------------
        # Create new analysis
        # ------------------------------------------------------

        analysis = AnalysisResult(
            transaction_id=transaction_id,
            customer_id=customer_id,

            success=bool(
                result.get(
                    "success",
                    False,
                )
            ),

            risk_level=decision.get(
                "risk_level"
            ),

            action=decision.get(
                "action"
            ),

            confidence=decision.get(
                "confidence"
            ),

            ml_risk_score=evidence.get(
                "ml_risk_score"
            ),

            anomaly_detected=evidence.get(
                "anomaly_detected"
            ),

            velocity_risk=evidence.get(
                "velocity_risk"
            ),

            customer_risk=evidence.get(
                "customer_risk"
            ),

            transaction_risk=evidence.get(
                "transaction_risk"
            ),

            triggered_rules=evidence.get(
                "triggered_rules",
                [],
            ),

            explanation=result.get(
                "explanation"
            ),

            analysis_metadata=result.get(
                "metadata",
                {},
            ),
        )

        try:

            db.add(analysis)

            db.commit()

            db.refresh(analysis)

            return analysis

        except IntegrityError as exc:

            db.rollback()

            raise ValueError(
                "Analysis could not be saved because "
                "the transaction already has an analysis "
                "or violates a database constraint."
            ) from exc

        except Exception:

            db.rollback()

            raise

    # ==========================================================
    # Batch Analysis
    # ==========================================================

    def save_batch_analysis(
        self,
        db: Session,
        batch_id: str,
        transaction_count: int,
        input_s3_location: str,
        result: dict[str, Any],
    ) -> AnalysisBatch:

        summary = result.get(
            "summary",
            {},
        )

        model = result.get(
            "model",
            {},
        )

        artifacts = result.get(
            "artifacts",
            {},
        )

        # ------------------------------------------------------
        # Validate batch ID
        # ------------------------------------------------------

        if not batch_id:
            raise ValueError(
                "batch_id is required."
            )

        # ------------------------------------------------------
        # Prevent duplicate batch records
        # ------------------------------------------------------

        existing = db.scalar(
            select(AnalysisBatch).where(
                AnalysisBatch.batch_id
                == batch_id
            )
        )

        if existing:
            raise ValueError(
                f"Batch analysis already exists for batch_id "
                f"'{batch_id}'."
            )

        # ------------------------------------------------------
        # Create batch analysis
        # ------------------------------------------------------

        analysis = AnalysisBatch(
            batch_id=batch_id,

            job_id=result.get(
                "job_id"
            ),

            transaction_count=transaction_count,

            success=bool(
                result.get(
                    "success",
                    False,
                )
            ),

            status=result.get(
                "status"
            ),

            total_transactions=summary.get(
                "total_transactions"
            ),

            fraud_transactions=summary.get(
                "fraud_transactions"
            ),

            legitimate_transactions=summary.get(
                "legitimate_transactions"
            ),

            fraud_rate=summary.get(
                "fraud_rate"
            ),

            average_fraud_probability=summary.get(
                "average_fraud_probability"
            ),

            production_threshold=summary.get(
                "production_threshold"
            ),

            model_name=model.get(
                "name"
            ),

            model_alias=model.get(
                "alias"
            ),

            model_version=model.get(
                "version"
            ),

            model_type=model.get(
                "type"
            ),

            xgb_weight=model.get(
                "xgb_weight"
            ),

            nn_weight=model.get(
                "nn_weight"
            ),

            input_s3_location=input_s3_location,

            result_download_url=artifacts.get(
                "result_download_url"
            ),

            report_download_url=artifacts.get(
                "report_download_url"
            ),

            analysis_metadata=result.get(
                "metadata",
                {},
            ),
        )

        # ------------------------------------------------------
        # Persist batch safely
        # ------------------------------------------------------

        try:

            db.add(analysis)

            db.commit()

            db.refresh(analysis)

            return analysis

        except IntegrityError as exc:

            db.rollback()

            raise ValueError(
                "Batch analysis could not be saved because "
                "the batch_id already exists or violates "
                "a database constraint."
            ) from exc

        except Exception:

            db.rollback()

            raise
    
    # ======================================================
    # List Single Analyses
    # ======================================================

    def get_analyses(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AnalysisResult]:

        return list(
            db.scalars(
                select(AnalysisResult)
                .order_by(
                    AnalysisResult.created_at.desc()
                )
                .offset(skip)
                .limit(limit)
            )
        )

    # ======================================================
    # Get Single Analysis
    # ======================================================

    def get_analysis(
        self,
        db: Session,
        transaction_id: str,
    ) -> AnalysisResult | None:

        return db.scalar(
            select(AnalysisResult).where(
                AnalysisResult.transaction_id
                == transaction_id
            )
        )

    # ======================================================
    # List Batch Analyses
    # ======================================================

    def get_batch_analyses(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AnalysisBatch]:

        return list(
            db.scalars(
                select(AnalysisBatch)
                .order_by(
                    AnalysisBatch.created_at.desc()
                )
                .offset(skip)
                .limit(limit)
            )
        )

    # ======================================================
    # Get Batch Analysis
    # ======================================================

    def get_batch_analysis(
        self,
        db: Session,
        batch_id: str,
    ) -> AnalysisBatch | None:

        return db.scalar(
            select(AnalysisBatch).where(
                AnalysisBatch.batch_id
                == batch_id
            )
        )

analysis_service = AnalysisService()