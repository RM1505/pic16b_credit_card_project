from dataclasses import dataclass

@dataclass
class SpendProfile:
    """
    Values represent spending for the current period inputted by user.
    """
    travel: float
    groceries_dining: float
    gas_utilities: float
    other: float = 0.0  # everything else

# Mapping from clean_rewards categories in clean_cards.json to SpendProfile fields
CATEGORY_TO_BUCKET = {
    "Travel": "travel",
    "Groceries & Dining": "groceries_dining",
    "Gas & Utilities": "gas_utilities",
    "Retail & Entertainment": "other",
    "Other": "other",
    "All Purchases": None
}
