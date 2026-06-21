# ==========================================================
# EXCEPTIONS
# Institutional Exception Framework
# ==========================================================

class PlatformException(Exception):

    """Base exception for platform"""

    pass


class ConfigurationError(
    PlatformException
):

    pass


class ValidationError(
    PlatformException
):

    pass


class DataError(
    PlatformException
):

    pass
# ==========================================================
# DATA EXCEPTIONS
# ==========================================================

class DataLoadError(
    DataError
):

    pass


class DataQualityError(
    DataError
):

    pass


class MissingColumnError(
    DataError
):

    pass


class EmptyDatasetError(
    DataError
):

    pass
# ==========================================================
# PORTFOLIO EXCEPTIONS
# ==========================================================

class PortfolioError(
    PlatformException
):

    pass


class PortfolioConstructionError(
    PortfolioError
):

    pass


class ConstraintViolationError(
    PortfolioError
):

    pass


# ==========================================================
# RISK EXCEPTIONS
# ==========================================================

class RiskError(
    PlatformException
):

    pass


class RiskLimitBreach(
    RiskError
):

    pass


class TrackingErrorBreach(
    RiskError
):

    pass
# ==========================================================
# GOVERNANCE EXCEPTIONS
# ==========================================================

class GovernanceError(
    PlatformException
):

    pass


class ApprovalRequiredError(
    GovernanceError
):

    pass


class ComplianceFailure(
    GovernanceError
):

    pass


# ==========================================================
# EXECUTION EXCEPTIONS
# ==========================================================

class ExecutionError(
    PlatformException
):

    pass


class SlippageLimitExceeded(
    ExecutionError
):

    pass


class MarketImpactExceeded(
    ExecutionError
):

    pass