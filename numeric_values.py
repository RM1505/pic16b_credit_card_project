"""
Numeric reward valuation that works for ANY time period:
monthly, annual, varying by month (sum multiple periods manually)

Given:
  - card dict from clean_cards.json
  - SpendProfile with spending for the period

This computes:
  numeric_rewards_for_this_period
  Note: no annual fee is subtracted here, fees are handled elsewhere
"""
from typing import Dict
from spend_profile import SpendProfile, CATEGORY_TO_BUCKET
from cpp_table import get_cpp

def row_to_dollar_rate(card: dict, value: float, 
    rate_type: str, unit: str) -> float | None:
    """
    Convert a single clean_rewards row into dollars of reward per $1 of spend.

    Returns
    ---------
    float or None
    """
    unit = str(unit).lower()
    rate = str(rate_type)

    # 1) Percentage cash back / rewards (e.g. 2% cash back)
    if rate == "Percentage" and unit in ("cash back", "rewards"):
        return float(value) / 100.0

    # 2) Multiplier / per-unit miles/points (e.g. 10x miles)
    if rate in ("Multiplier", "Per Unit"):
        cpp = get_cpp(card, unit)  # cents per point/mile
        return float(value) * (cpp / 100.0)

    return None

def card_to_category_rates(card: dict) -> dict:
    """
    Build {category_name: dollars_per_1_dollar_spent} from clean_rewards.

    Parameters
    -------------
    card: dict (clean_rewards: [value, rate_type, unit, category])

    Returns
    --------
    dict
    """
    clean_rewards = card.get("clean_rewards", []) or []
    out = {}

    for row in clean_rewards:
        value, rate_type, unit, category = row
        rate = row_to_dollar_rate(card, value, rate_type, unit)
        cat = str(category)

        # If multiple rows share a cateogy, keep the highest rate
        if cat not in out or (rate is not None and rate > out[cat]):
            out[cat] = rate

    return out

def value_card_numeric(card: dict, sp: SpendProfile) -> float:
    """
    Compute numeric rewards for the specified period

    Returns
    ---------
    float (dollar equivalent of rewards)
    """
    category_rates = card_to_category_rates(card)

    if not category_rates:
        return 0.0

    total_spend = (sp.travel + sp.groceries_dining + sp.gas_utilities + sp.other)

    total_value = 0.0

    for reward_cat, per_dollar in category_rates.items():
        bucket = CATEGORY_TO_BUCKET.get(reward_cat)

        if bucket is None:
            # "All Purchases" → whole budget, otherwise other spend bucket
            if reward_cat == "All Purchases":
                base_spend = total_spend
            else:
                base_spend = sp.other
        else:
            base_spend = getattr(sp, bucket, 0.0)

        if base_spend > 0 and per_dollar is not None:
            total_value += per_dollar * base_spend

    return total_value