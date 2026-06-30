"""
====================================================================
Institutional Quant Platform

Drift Detector

Author : Institutional Quant Platform

Purpose
-------
Institutional data and model drift detection.

Detects

• Feature Drift
• Prediction Drift
• Population Stability Index (PSI)
• Distribution Shift
• Mean Shift
• Variance Shift

Used By

• Monitoring
• Dashboard
• Alert Engine
• ML Pipeline

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class DriftResult:
    """
    Drift detection result.
    """

    metric: str

    score: float

    threshold: float

    drift_detected: bool

    metadata: dict

    def summary(

        self,

    ) -> dict:

        return {

            "Metric":

                self.metric,

            "Score":

                self.score,

            "Threshold":

                self.threshold,

            "DriftDetected":

                self.drift_detected,

            "Metadata":

                self.metadata,

        }


class DriftDetector:
    """
    Institutional drift detector.
    """

    # =====================================================
    # PSI
    # =====================================================

    @staticmethod
    def population_stability_index(

        reference,

        current,

        bins: int = 10,

    ) -> float:

        reference = np.asarray(

            reference,

            dtype=float,

        )

        current = np.asarray(

            current,

            dtype=float,

        )

        breakpoints = np.percentile(

            reference,

            np.linspace(

                0,

                100,

                bins + 1,

            ),

        )

        expected = np.histogram(

            reference,

            bins=breakpoints,

        )[0]

        actual = np.histogram(

            current,

            bins=breakpoints,

        )[0]

        expected = (

            expected

            / max(

                expected.sum(),

                1,

            )

        )

        actual = (

            actual

            / max(

                actual.sum(),

                1,

            )

        )

        expected = np.clip(

            expected,

            1e-8,

            None,

        )

        actual = np.clip(

            actual,

            1e-8,

            None,

        )

        psi = np.sum(

            (

                actual

                -

                expected

            )

            *

            np.log(

                actual

                /

                expected

            )

        )

        return float(

            psi

        )

    # =====================================================
    # MEAN SHIFT
    # =====================================================

    @staticmethod
    def mean_shift(

        reference,

        current,

    ) -> float:

        return float(

            abs(

                np.mean(

                    current

                )

                -

                np.mean(

                    reference

                )

            )

        )

    # =====================================================
    # VARIANCE SHIFT
    # =====================================================

    @staticmethod
    def variance_shift(

        reference,

        current,

    ) -> float:

        return float(

            abs(

                np.var(

                    current

                )

                -

                np.var(

                    reference

                )

            )

        )

    # =====================================================
    # FEATURE DRIFT
    # =====================================================

    @classmethod
    def feature_drift(

        cls,

        reference,

        current,

        threshold: float = 0.25,

    ) -> DriftResult:

        psi = cls.population_stability_index(

            reference,

            current,

        )

        return DriftResult(

            metric="Feature Drift",

            score=psi,

            threshold=threshold,

            drift_detected=psi > threshold,

            metadata={

                "Method":

                    "PSI",

            },

        )

    # =====================================================
    # PREDICTION DRIFT
    # =====================================================

    @classmethod
    def prediction_drift(

        cls,

        reference_predictions,

        live_predictions,

        threshold: float = 0.10,

    ) -> DriftResult:

        shift = cls.mean_shift(

            reference_predictions,

            live_predictions,

        )

        return DriftResult(

            metric="Prediction Drift",

            score=shift,

            threshold=threshold,

            drift_detected=shift > threshold,

            metadata={

                "Method":

                    "Mean Shift",

            },

        )

    # =====================================================
    # DISTRIBUTION DRIFT
    # =====================================================

    @classmethod
    def distribution_drift(

        cls,

        reference,

        current,

        threshold: float = 0.20,

    ) -> DriftResult:

        variance = cls.variance_shift(

            reference,

            current,

        )

        return DriftResult(

            metric="Distribution Drift",

            score=variance,

            threshold=threshold,

            drift_detected=variance > threshold,

            metadata={

                "Method":

                    "Variance Shift",

            },

        )

    # =====================================================
    # FULL REPORT
    # =====================================================

    @classmethod
    def report(

        cls,

        reference,

        current,

    ) -> dict:

        feature = cls.feature_drift(

            reference,

            current,

        )

        distribution = cls.distribution_drift(

            reference,

            current,

        )

        return {

            "FeatureDrift":

                feature.summary(),

            "DistributionDrift":

                distribution.summary(),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}()"

        )

    __str__ = __repr__