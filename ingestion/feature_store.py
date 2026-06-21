# ==========================================================
# FEATURE STORE
# Institutional Feature Management
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


# ==========================================================
# FEATURE METADATA
# ==========================================================

@dataclass
class FeatureMetadata:

    feature_name: str

    version: str

    created_at: datetime

    owner: str

    description: str


# ==========================================================
# FEATURE REGISTRY
# ==========================================================

class FeatureRegistry:

    def __init__(self):

        self.registry = {}

    def register(
        self,
        metadata: FeatureMetadata
    ):

        self.registry[
            metadata.feature_name
        ] = metadata

    def get(
        self,
        feature_name
    ):

        return self.registry.get(
            feature_name
        )
    
# ==========================================================
# FEATURE CATALOG
# ==========================================================

class FeatureCatalog:

    def __init__(self):

        self.features = {}

    def add_feature(
        self,
        name,
        dataframe
    ):

        self.features[name] = dataframe

    def get_feature(
        self,
        name
    ):

        return self.features.get(name)

    def list_features(
        self
    ):

        return list(
            self.features.keys()
        )
    
# ==========================================================
# FEATURE VERSION ENGINE
# ==========================================================

class FeatureVersionEngine:

    @staticmethod
    def create_version(
        major,
        minor
    ):

        return f"{major}.{minor}"

    @staticmethod
    def latest_version(
        versions
    ):

        versions = sorted(
            versions,
            reverse=True
        )

        return versions[0]
    
# ==========================================================
# MASTER FEATURE STORE
# ==========================================================

class FeatureStore:

    def __init__(self):

        self.registry = (
            FeatureRegistry()
        )

        self.catalog = (
            FeatureCatalog()
        )

    def register_feature(
        self,
        name,
        dataframe,
        owner,
        description,
        version="1.0"
    ):

        metadata = FeatureMetadata(

            feature_name=name,

            version=version,

            created_at=datetime.now(),

            owner=owner,

            description=description

        )

        self.registry.register(
            metadata
        )

        self.catalog.add_feature(
            name,
            dataframe
        )

    def get_feature(
        self,
        name
    ):

        return self.catalog.get_feature(
            name
        )

    def list_features(
        self
    ):

        return self.catalog.list_features()