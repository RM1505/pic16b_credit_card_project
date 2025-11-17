#How many points per dollar each card earns in each category

import re
from typing import Dict
from filter import RewardFocus

def split_sentences(text: str) -> list[str]:
    """
    Roughly split rewards text into sentence-like chunks.
    """
    if isinstance(text, list):
        text = " ".join(str(t) for t in text)
    elif not isinstance(text, str):
        text = str(text)

    #Simple regex to simplify for future use
    text = text.replace("\n", ".")
    text2 = [text2.strip() for text2 in re.split(r"[.;]", text)]

    return [t for t in text2 if t]


def extract_multipliers(sentence: str) -> list[float]:
    """
    Extract numeric earn multipliers or percent-back values from a sentence.

    Examples this should catch:
      - "3x points"
      - "5X miles"
      - "5% cash back"
      - "1 % back on all other purchases"
    Returns a list of floats (e.g. [3.0, 5.0]).
    """
    s = sentence.lower()

    multipliers = []

    # Pattern 1: '3x', '4 x', '5×'
    for match in re.finditer(r"(\d+(\.\d+)?)\s*[x×]", s):
        value = float(match.group(1))
        multipliers.append(value)

    # Pattern 2: '5% cash back', '2 % back', etc.
    # Here we interpret '5% back' as equivalent to 5x for points-like logic FOR NOW
    for match in re.finditer(r"(\d+(\.\d+)?)\s*%", s):
        value = float(match.group(1))
        multipliers.append(value)

    return multipliers


def parse_earn_rates(rewards_text: str, default_other: float = 1.0) -> Dict[str, float]:
    """
    Parse raw rewards text into:
        category -> points_per_dollar_spent

    Uses:
      - RewardFocus(rewards_text) from filter.py to detect categories
      - Regex to extract multipliers (3x, 5x, 5% back, etc.)
    """
    if not rewards_text:
        return {"other": default_other}

    earn_rates: Dict[str, float] = {}

    sentences = split_sentences(rewards_text)

    for s in sentences:
        categories = RewardFocus(s) 

        multipliers = extract_multipliers(s)

        if multipliers:
            """Take the largest multiplier in the sentence. 
            If multiple multipliers and categories are found in the same sentence,
            the parser assigns the highest multiplier to all categories. This may
             overestimate some categories but avoids underestimating key bonus categories"""
            rate = max(multipliers)
        else:
            # If no explicit multiplier found, assume base 1x for those categories
            rate = default_other

        #Assign this rate to all categories mentioned in the sentence
        for c in categories:
            # Keep the maximum rate if category appears multiple times
            if c not in earn_rates or rate > earn_rates[c]:
                earn_rates[c] = rate

    #Ensure 'other' category always exists
    if "other" not in earn_rates:
        earn_rates["other"] = default_other

    return earn_rates
