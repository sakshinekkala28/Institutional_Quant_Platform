# ==========================================================
# AUDIT LOGGER
# Institutional Audit Framework
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import json
import uuid


# ==========================================================
# AUDIT EVENT
# ==========================================================

@dataclass
class AuditEvent:

    event_id: str

    event_type: str

    timestamp: datetime

    user: str

    details: dict


# ==========================================================
# EVENT FACTORY
# ==========================================================

class AuditEventFactory:

    @staticmethod
    def create(

        event_type,

        user,

        details

    ):

        return AuditEvent(

            event_id=str(
                uuid.uuid4()
            ),

            event_type=event_type,

            timestamp=datetime.utcnow(),

            user=user,

            details=details

        )
    
# ==========================================================
# RUN METADATA LOGGER
# ==========================================================

class RunMetadataLogger:

    @staticmethod
    def build_metadata(

        model_name,

        model_version,

        config_version,

        rebalance_date

    ):

        return {

            "Model_Name":
            model_name,

            "Model_Version":
            model_version,

            "Config_Version":
            config_version,

            "Rebalance_Date":
            rebalance_date,

            "Run_Timestamp":
            datetime.utcnow()

        }


# ==========================================================
# ENVIRONMENT LOGGER
# ==========================================================

class EnvironmentLogger:

    @staticmethod
    def capture():

        return {

            "Python_Version":
            "3.x",

            "Platform":
            "Production",

            "Environment":
            "Institutional"

        }
    
# ==========================================================
# SNAPSHOT LOGGER
# ==========================================================

class SnapshotLogger:

    @staticmethod
    def portfolio_snapshot(
        portfolio
    ):

        return portfolio.copy()

    @staticmethod
    def trade_snapshot(
        trades
    ):

        return trades.copy()

    @staticmethod
    def risk_snapshot(
        risk_report
    ):

        return risk_report.copy()

    @staticmethod
    def governance_snapshot(
        governance_report
    ):

        return governance_report.copy()


# ==========================================================
# EVENT STORE
# ==========================================================

class EventStore:

    def __init__(self):

        self.events = []

    def append(
        self,
        event
    ):

        self.events.append(event)

    def to_dataframe(self):

        rows = []

        for e in self.events:

            rows.append({

                "Event_ID":
                e.event_id,

                "Type":
                e.event_type,

                "Timestamp":
                e.timestamp,

                "User":
                e.user,

                "Details":
                json.dumps(
                    e.details,
                    default=str
                )

            })

        return pd.DataFrame(rows)
    
# ==========================================================
# MASTER AUDIT LOGGER
# ==========================================================

class AuditLogger:

    def __init__(self):

        self.store = EventStore()

    def log(

        self,

        event_type,

        user,

        details

    ):

        event = (

            AuditEventFactory

            .create(

                event_type,

                user,

                details

            )

        )

        self.store.append(
            event
        )

    def export(self):

        return (

            self.store

            .to_dataframe()

        )

    def log_rebalance(

        self,

        model_name,

        model_version,

        config_version,

        holdings

    ):

        self.log(

            "REBALANCE",

            "SYSTEM",

            {

                "Model":
                model_name,

                "Version":
                model_version,

                "Config":
                config_version,

                "Holdings":
                holdings

            }

        )

    def log_governance(

        self,

        approved

    ):

        self.log(

            "GOVERNANCE",

            "SYSTEM",

            {

                "Approved":
                approved

            }

        )