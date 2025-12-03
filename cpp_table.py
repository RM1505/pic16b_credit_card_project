from typing import Dict

# According to NerdWallet, using optimistic values
CPP_TABLE: Dict[str, Dict[str, float]]= {
    "default": {
        "miles": 0.01,
        "points": 0.01
    },

    "American Express": {
        "miles": 0.016,
        "points": 0.006
    },

    "Capital One": {
        "miles": 0.016,
        "points": 0.005
    },

    "Chase": {
        "miles": 0.018,
        "points": 0.008
    },

    "Citi": {
        "miles": 0.016,
        "points": 0.01,
    },

    "Bank of America": {
        "miles": 0.01,
        "points": 0.006
    },

    "Wells Fargo": {
        "miles": 0.01,
        "points": 0.01
    },

    "U.S. Bank": {
        "miles": 0.015,
        "points": 0.012,
    },

    "Discover": {
        "miles": 0.01,
        "points":  0.01
    }
}
