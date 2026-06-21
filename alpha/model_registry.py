# ==========================================================
# MODEL REGISTRY
# Institutional Model Governance
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


# ==========================================================
# MODEL METADATA
# ==========================================================

@dataclass
class ModelMetadata:

    model_name: str

    version: str

    created_at: datetime

    owner: str

    status: str

    description: str


# ==========================================================
# MODEL REGISTRY
# ==========================================================

class ModelRegistry:

    def __init__(self):

        self.models = {}

    def register(
        self,
        metadata: ModelMetadata
    ):

        key = (

            metadata.model_name,

            metadata.version

        )

        self.models[key] = metadata

    def get_model(
        self,
        model_name,
        version
    ):

        return self.models.get(

            (model_name, version)

        )

    def list_models(self):

        return list(
            self.models.keys()
        )
    
# ==========================================================
# MODEL PERFORMANCE
# ==========================================================

class ModelPerformanceTracker:

    def __init__(self):

        self.performance = {}

    def record(

        self,

        model_name,

        version,

        metrics

    ):

        key = (

            model_name,

            version

        )

        self.performance[key] = metrics

    def get(

        self,

        model_name,

        version

    ):

        return self.performance.get(

            (model_name, version)

        )

    def leaderboard(self):

        rows = []

        for key, metrics in self.performance.items():

            rows.append({

                "Model": key[0],

                "Version": key[1],

                **metrics

            })

        return pd.DataFrame(rows)
    
# ==========================================================
# MODEL PROMOTION
# ==========================================================

class ModelPromotionEngine:

    def __init__(self):

        self.production_model = None

    def promote(

        self,

        model_name,

        version

    ):

        self.production_model = {

            "Model": model_name,

            "Version": version

        }

    def current_production(self):

        return self.production_model


# ==========================================================
# MODEL COMPARISON
# ==========================================================

class ModelComparisonEngine:

    @staticmethod
    def compare(

        performance_df,

        metric="Sharpe"

    ):

        return (

            performance_df

            .sort_values(

                metric,

                ascending=False

            )

        )
    
# ==========================================================
# MASTER MODEL REGISTRY
# ==========================================================

class ModelRegistryEngine:

    def __init__(self):

        self.registry = ModelRegistry()

        self.performance = (

            ModelPerformanceTracker()

        )

        self.promotion = (

            ModelPromotionEngine()

        )

    def register_model(

        self,

        model_name,

        version,

        owner,

        description

    ):

        metadata = ModelMetadata(

            model_name=model_name,

            version=version,

            created_at=datetime.now(),

            owner=owner,

            status="RESEARCH",

            description=description

        )

        self.registry.register(
            metadata
        )

    def record_performance(

        self,

        model_name,

        version,

        metrics

    ):

        self.performance.record(

            model_name,

            version,

            metrics

        )

    def promote_model(

        self,

        model_name,

        version

    ):

        self.promotion.promote(

            model_name,

            version

        )

    def leaderboard(self):

        return (

            self.performance

            .leaderboard()

        )