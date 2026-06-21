from __future__ import annotations

import mlflow
import pandas as pd


class MLflowManager:

    def __init__(self):

        mlflow.set_tracking_uri(
            "sqlite:///mlflow.db"
        )

        mlflow.set_experiment(
            "Institutional_Quant"
        )

    def start_run(
        self,
        run_name: str
    ):

        return mlflow.start_run(
            run_name=run_name
        )

    @staticmethod
    def log_params(
        params: dict
    ):

        mlflow.log_params(
            params
        )

    @staticmethod
    def log_metrics(
        metrics: dict
    ):

        mlflow.log_metrics(
            metrics
        )

    @staticmethod
    def log_metric(
        key,
        value
    ):

        mlflow.log_metric(
            key,
            value
        )
        
    @staticmethod
    def log_dataframe(
        df: pd.DataFrame,
        artifact_name: str
    ):

        path = (
            f"/tmp/{artifact_name}.csv"
        )

        df.to_csv(
            path,
            index=False
        )

        mlflow.log_artifact(
            path
        )

    @staticmethod
    def register_model(
        model_uri,
        model_name
    ):

        mlflow.register_model(
            model_uri,
            model_name
        )