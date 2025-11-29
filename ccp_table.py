from typing import Dict

# Nerdwallet BASELINE values (conservative estimates)
CPP_TABLE_BASELINE: Dict[str, Dict[str, float]] = {
    "default": {
        "points": 1.0,
        "miles":  1.0,
    },
    "American Express": {
        "points": 0.6,
        "miles": 0.875 # Average of 0.75 and 1
    },
    "Capital One": {
        "points": 0.5,
        "miles": 1.0,
    },
    "Chase": {
        "points": 1.0,
        "miles": 1.25, # Average of 1.0 and 1.5
    },
    "Citi": {
        "points": 0.75, # Average of 0.5 and 1
        "miles": 1.0,
    }
}

# Nerdwallet OPTIMISTIC Values
CPP_TABLE_OPTIMISTIC: Dict[str, Dict[str, float]] = {
    "default": {
        "points": 1.0,
        "miles":  1.0,
    },
    "American Express": {
        "points": 1.6,
    },
    "Capital One": {
        "miles": 1.6,
    },
    "Chase": {
        "points": 1.8,
    },
    "Citi": {
        "points": 1.6,
    }
}

def get_cpp(card: Dict[str, str], unit: str, cpp_table: Dict[str, Dict[str, float]] = CPP_TABLE) -> float:
    """
    Decide cents-per-point for a given card and reward unit.

    Priority:
      1. Card-name overrides
      2. Issuer-specific overrides
      3. Default table
      4. Otherwise 0.0
    """
    unit = unit.lower()
    name = card.get("name", "")
    issuer = card.get("issuer", "")

    # 1) Card-specific "overrides" issuer default values
    if name in cpp_table and unit in cpp_table[name]:
        return cpp_table[name][unit]

    # 2) Issuer-specific
    if issuer in cpp_table and unit in cpp_table[issuer]:
        return cpp_table[issuer][unit]

    # 3) Default/fallback
    if "default" in cpp_table and unit in cpp_table["default"]:
        return cpp_table["default"][unit]

    # 4) Unknown
    return 0.0
