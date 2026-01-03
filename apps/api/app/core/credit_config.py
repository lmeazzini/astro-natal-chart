"""
Credit system configuration.

Defines credit limits per plan and credit costs per feature.
"""

from app.models.enums import FeatureType, PlanType

# Credit limits per plan (None = unlimited)
PLAN_CREDIT_LIMITS: dict[str, int | None] = {
    PlanType.FREE.value: 10,
    PlanType.STARTER.value: 50,
    PlanType.PRO.value: 200,
    PlanType.UNLIMITED.value: None,  # Unlimited
}

# Credit costs per feature
FEATURE_CREDIT_COSTS: dict[str, int] = {
    FeatureType.INTERPRETATION_BASIC.value: 1,
    FeatureType.INTERPRETATION_FULL.value: 3,
    FeatureType.PDF_REPORT.value: 2,
    FeatureType.SYNASTRY.value: 2,
    FeatureType.SOLAR_RETURN.value: 2,
    FeatureType.SATURN_RETURN.value: 2,
    FeatureType.LONGEVITY.value: 3,  # Updated: complex calculation
    FeatureType.GROWTH.value: 2,  # New: growth suggestions
    FeatureType.PROFECTIONS.value: 1,
    FeatureType.TRANSITS.value: 1,
}

# Plan prices in BRL cents (for display purposes)
PLAN_PRICES_BRL: dict[str, int] = {
    PlanType.FREE.value: 0,
    PlanType.STARTER.value: 3000,  # R$ 30,00
    PlanType.PRO.value: 10000,  # R$ 100,00
    PlanType.UNLIMITED.value: 50000,  # R$ 500,00
}


def get_credit_limit(plan_type: str) -> int | None:
    """Get credit limit for a plan type.

    Args:
        plan_type: Plan type string (free, starter, pro, unlimited)

    Returns:
        Credit limit or None for unlimited plans.
    """
    return PLAN_CREDIT_LIMITS.get(plan_type, PLAN_CREDIT_LIMITS[PlanType.FREE.value])


def get_feature_cost(feature_type: str) -> int:
    """Get credit cost for a feature.

    Args:
        feature_type: Feature type string

    Returns:
        Credit cost for the feature, defaults to 1 if not found.
    """
    return FEATURE_CREDIT_COSTS.get(feature_type, 1)


def is_unlimited_plan(plan_type: str) -> bool:
    """Check if a plan type has unlimited credits.

    Args:
        plan_type: Plan type string

    Returns:
        True if the plan has unlimited credits.
    """
    return PLAN_CREDIT_LIMITS.get(plan_type) is None
