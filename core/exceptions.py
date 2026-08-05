# ==========================================================
# EXCEPTIONS
# Institutional Exception Framework
# ==========================================================


class PlatformExceptionError(Exception):
    """Base exception for platform"""


class ConfigurationError(PlatformExceptionError):
    pass


class ValidationError(PlatformExceptionError):
    pass


class DataError(PlatformExceptionError):
    pass


# ==========================================================
# DATA EXCEPTIONS
# ==========================================================


class DataLoadError(DataError):
    pass


class DataQualityError(DataError):
    pass


class MissingColumnError(DataError):
    pass


class EmptyDatasetError(DataError):
    pass


# ==========================================================
# PORTFOLIO EXCEPTIONS
# ==========================================================


class PortfolioError(PlatformExceptionError):
    pass


class PortfolioConstructionError(PortfolioError):
    pass


class ConstraintViolationError(PortfolioError):
    pass


# ==========================================================
# RISK EXCEPTIONS
# ==========================================================


class RiskError(PlatformExceptionError):
    pass


class RiskLimitBreachError(RiskError):
    pass


class TrackingErrorBreachError(RiskError):
    pass


# ==========================================================
# GOVERNANCE EXCEPTIONS
# ==========================================================


class GovernanceError(PlatformExceptionError):
    pass


class ApprovalRequiredError(GovernanceError):
    pass


class ComplianceFailureError(GovernanceError):
    pass


# ==========================================================
# EXECUTION EXCEPTIONS
# ==========================================================


class ExecutionError(PlatformExceptionError):
    pass


class SlippageLimitExceededError(ExecutionError):
    pass


class MarketImpactExceededError(ExecutionError):
    pass
