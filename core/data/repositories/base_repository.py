"""
====================================================================
Institutional Quant Platform

Base Repository

Author : Institutional Quant Platform

Purpose
-------
Institutional Repository Framework.

Responsibilities

• Load Data
• Save Data
• Validate Data
• Audit
• Logging
• Metadata
• Repository Lifecycle

Inherited By

• PortfolioRepository
• ConstraintRepository
• RiskRepository
• AlphaRepository
• GovernanceRepository

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from pathlib import Path

from typing import Generic
from typing import TypeVar

import pandas as pd

from core.data.loaders.base_loader import (

    BaseLoader,

    LoadResult

)

from core.data.validators.base_validator import (

    BaseValidator,

    ValidationResult

)

from core.logging_manager import LoggingManager

# ==========================================================
# GENERICS
# ==========================================================

T = TypeVar(

    "T"

)

# ==========================================================
# LOGGER
# ==========================================================

logger = LoggingManager.get_logger(

    __name__

)

# ==========================================================
# BASE REPOSITORY
# ==========================================================


class BaseRepository(

    ABC,

    Generic[T]

):

    """
    Institutional Base Repository.
    """

    def __init__(

        self,

        loader: BaseLoader,

        validator: BaseValidator | None = None

    ) -> None:

        self.loader = loader

        self.validator = validator

        self._cache: T | None = None

    # ======================================================
    # LOAD
    # ======================================================

    def load(

        self,

        refresh: bool = False

    ) -> T:

        """
        Repository loading pipeline.

        before_load()

            ↓

        Loader

            ↓

        Validator

            ↓

        Cache

            ↓

        after_load()

        """

        if (

            self._cache is not None

            and

            not refresh

        ):

            logger.info(

                "Returning cached dataset."

            )

            return self._cache

        self.before_load()

        result = self.loader.load()

        data = result.data

        if (

            self.validator

            is not None

        ):

            validation = self.validator.validate(

                data

            )

            if (

                not validation.passed

            ):

                logger.warning(

                    "Validation produced %d issues.",

                    len(

                        validation.issues

                    )

                )

        self._cache = self._transform(

            data

        )

        self.after_load(

            self._cache

        )

        return self._cache

    # ======================================================
    # ABSTRACT
    # ======================================================

    @abstractmethod

    def _transform(

        self,

        dataframe: pd.DataFrame

    ) -> T:

        """
        Convert DataFrame
        into repository object.
        """

        raise NotImplementedError
    
    # ======================================================
    # RELOAD
    # ======================================================

    def reload(

        self

    ) -> T:

        """
        Reload repository.
        """

        return self.load(

            refresh=True

        )

    # ======================================================
    # CACHE
    # ======================================================

    def clear_cache(

        self

    ) -> None:

        """
        Clear cached object.
        """

        self._cache = None

        logger.info(

            "Repository cache cleared."

        )

    @property

    def cached(

        self

    ) -> bool:

        """
        Cache status.
        """

        return self._cache is not None

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(

        self

    ) -> ValidationResult[pd.DataFrame] | None:

        """
        Validate repository data.
        """

        if self.validator is None:

            return None

        dataframe = self.loader.load().data

        return self.validator.validate(

            dataframe

        )

    # ======================================================
    # METADATA
    # ======================================================

    def metadata(

        self

    ):

        """
        Loader metadata.
        """

        return self.loader.load().metadata

    # ======================================================
    # QUALITY
    # ======================================================

    def quality_report(

        self

    ):

        """
        Validation report.
        """

        validation = self.validate()

        if validation is None:

            return None

        return {

            "passed":

                validation.passed,

            "issues":

                len(

                    validation.issues

                ),

            "details":

                validation.issues

        }

    # ======================================================
    # CALLBACKS
    # ======================================================

    def before_load(

        self

    ) -> None:

        """
        Repository hook.
        """

        return None

    def after_load(

        self,

        data: T

    ) -> None:

        """
        Repository hook.
        """

        logger.info(

            "Repository loaded successfully."

        )

    # ======================================================
    # SAVE
    # ======================================================

    def save(

        self,

        *_,

        **__

    ) -> None:

        """
        Save hook.

        Concrete repositories
        override if required.
        """

        raise NotImplementedError(

            f"{self.__class__.__name__} "

            "does not implement save()."

        )

    # ======================================================
    # CONTEXT MANAGER
    # ======================================================

    def __enter__(

        self

    ) -> "BaseRepository[T]":

        return self

    def __exit__(

        self,

        exc_type,

        exc,

        traceback

    ) -> None:

        self.clear_cache()

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}"

            "("

            f"loader={self.loader.__class__.__name__}, "

            f"validator="

            f"{self.validator.__class__.__name__ if self.validator else 'None'}"

            ")"

        )

    __str__ = __repr__