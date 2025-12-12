import pulp
import pandas as pd
from typing import Dict

POINTS_TO_CASH: Dict[str, Dict[str, float]]= {
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

def get_conversion_rate(issuer: str, unit: str) -> float:
     """
    Return the cash-equivalent conversion rate for a reward unit issued by a
    given card issuer.

    Parameters
    ----------
    issuer : str
        Name of the card issuer (e.g., "Chase", "American Express").
    unit : str
        Reward unit type (e.g., "points", "miles").

    Returns
    -------
    float
        Dollar value per reward unit. Falls back to issuer-default or global
        default if a specific mapping is unavailable.
    """
    # pick issuer or default
    issuer_table = POINTS_TO_CASH.get(issuer, POINTS_TO_CASH["default"])

    # try issuer-specific valuation
    if unit in issuer_table:
        return issuer_table[unit]

    # fallback to default valuation for this unit
    return POINTS_TO_CASH["default"].get(unit, 0.01)

def get_dicts(df):
        """
    Parse a cleaned rewards dataset into structured dictionaries used by the
    optimization model.

    For each card, this function extracts:
      - per-category cash-equivalent reward rates
      - trigger-based reward bonuses
      - minimum credit score requirements (if provided)
      - annual fees

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing cleaned card metadata and reward definitions.

    Returns
    -------
    Tuple[dict, dict]
        cards_dict : dict
            Mapping card -> { "min_score", "rates", "triggers" }.
        fees_dict : dict
            Mapping card -> annual fee.
    """
    cards_dict = {}
    fees_dict = {}

    for _, row in df.iterrows():
        card_name = row["name"]
        issuer = row["issuer"]        # ADDED FOR ANGELA FRAMEWORK
        fees_dict[card_name] = row["clean_annual_fee"]

        rates = {}
        triggers = {}

        for reward in row["clean_rewards"]:
            if not reward:
                continue

            value = reward[0]
            rtype = reward[1]
            unit = reward[2]             # "miles", "points", etc.
            category = reward[3]         # direct category from  dataset

            # issuer based conversion
            conversion = get_conversion_rate(issuer, unit)
            cash_rate = value * conversion

            if rtype in ("Multiplier", "Per Unit", "Percentage"):
                # keep best rate for this category
                rates[category] = max(rates.get(category, 0), cash_rate)

            elif rtype == "Trigger":
                # placeholder for future
                triggers.setdefault(category, []).append((row["min_spend"], cash_rate))

        cards_dict[card_name] = {
            "min_score": 0,
            "rates": rates,
            "triggers": triggers,
        }

    return cards_dict, fees_dict


def summarize(cats, chosen, spending, cards, trigger_bonus, fees, held):
    """
    Generate a human-readable breakdown of the optimization solution.

    For each spending category, this function reports:
      - assigned card (if any)
      - spending amount
      - reward rate
      - trigger bonus
      - total reward contribution

    Annual fees are subtracted exactly once per held card, at the card's
    first appearance in the category list, to avoid double-counting while
    preserving an intuitive per-category presentation.

    Parameters
    ----------
    cats : list
        List of spending categories.
    chosen : dict
        Mapping category -> assigned card (or None).
    spending : dict
        Annual spending by category.
    cards : dict
        Card metadata including reward rates.
    trigger_bonus : dict
        Precomputed trigger bonuses keyed by (card, category).
    fees : dict
        Annual fees per card.
    held : set
        Set of cards selected by the optimization model.

    Returns
    -------
    dict
        Per-category breakdown of rewards and net contributions.
    """
    breakdown = {}
    fee_charged = set() # cards we already charged fee to

    for k in cats:
        c = chosen.get(k)   # may be None
        spend = spending[k]

        if c is None:
            breakdown[k] = {
                "card": None,
                "spend": spend,
                "rate": 0.0,
                "trigger_bonus": 0.0,
                "raw_reward": 0.0,
                "total_reward": 0.0,
                "fee": 0.0,
                "net_contribution": 0.0,
                "equation": "unassigned"
            }
            continue

        rate = cards[c]["rates"].get(k, 0.0)
        trig = trigger_bonus[(c, k)]
        raw = spend * rate
        reward_val = raw + trig

        fee_val = 0.0
        if c in held and c not in fee_charged:
            fee_val = float(fees.get(c, 0.0))
            fee_charged.add(c)

        breakdown[k] = {
            "card": c,
            "spend": spend,
            "rate": rate,
            "trigger_bonus": trig,
            "raw_reward": raw,
            "total_reward": reward_val,
            "fee": fee_val,
            "net_contribution": reward_val - fee_val,
            "equation": f"{spend} * {rate} + {trig} - {fee_val}"
        }

    return breakdown


def trigger_bonuses(card_list, cards, spending, cats):
    """
    Precompute trigger-based reward bonuses for each (card, category) pair.

    Given fixed category-level spending, this function evaluates whether
    trigger conditions (e.g., minimum spend thresholds) are met and returns
    the corresponding bonus amounts. These bonuses are treated as constants
    in the optimization model to preserve linearity.

    Parameters
    ----------
    card_list : list
        List of candidate cards.
    cards : dict
        Card metadata including trigger definitions.
    spending : dict
        Annual spending by category.
    cats : list
        List of spending categories.

    Returns
    -------
    dict
        Mapping (card, category) -> trigger bonus value.
    """
    bonuses={}
    for c in card_list:
        trig_dict = cards[c].get("triggers", {})  # may be missing
        for k in cats:
            total_bonus = 0.0
            if k in trig_dict:
                s = spending[k]
                for min_spend, bonus in trig_dict[k]:
                    if s >= min_spend:
                        total_bonus += bonus
            bonuses[(c, k)] = total_bonus
    return bonuses

def optimize_cardspace(cards, fees, spending, score):
    """
    Solve the credit card portfolio and spending allocation problem.

    This function formulates and solves a mixed-integer linear program that
    selects an optimal subset of credit cards and assigns each spending
    category to at most one card in order to maximize net annual rewards.
    Rewards include base category multipliers and precomputed trigger bonuses,
    minus annual card fees.

    Constraints enforce:
      - at most one card per spending category
      - cards can only be used if held
      - held cards must be used in at least one category
      - eligibility based on minimum credit score

    Parameters
    ----------
    cards : dict
        Mapping card -> reward structure and eligibility data.
    fees : dict
        Mapping card -> annual fee.
    spending : dict
        Annual spending by category.
    score : int
        User's credit score.

    Returns
    -------
    Tuple
        chosen : dict
            Mapping category -> selected card (or None).
        total : float
            Optimal net annual reward value.
        held : set
            Set of cards selected by the model.
        breakdown : dict
            Per-category reward breakdown for the solution.
    """
    prob = pulp.LpProblem("Maximize_Rewards", pulp.LpMaximize)
    cats = list(spending.keys())
    card_list = list(cards.keys())

    #eligibility filter from score
    eligible = {c: 1 if score >= cards[c].get("min_score", 0) else 0 for c in card_list}

    #decision vars

        #card selection indicator
    y = {c: pulp.LpVariable(f"hold_{c}", 0, 1, pulp.LpBinary) for c in card_list}

        #category decision 
    x = {(c,k): pulp.LpVariable(f"use_{c}_{k}", 0, 1, pulp.LpBinary)
         for c in card_list for k in cats}

    # Precompute trigger bonuses per (card, category)
    # If spending in k exceeds min_spend for a trigger, include its bonus.
    trigger_bonus = trigger_bonuses(card_list, cards, spending, cats)


    #objective: rewards - fees
    reward = pulp.lpSum((spending[k] * cards[c]["rates"].get(k, 0.0) + trigger_bonus[(c, k)]) * x[(c,k)] 
                        for c in card_list for k in cats)
    fee = pulp.lpSum(fees[c] * y[c] for c in card_list)
    prob += reward - fee

    #at most one card per category
    for k in cats:
        prob += pulp.lpSum(x[(c,k)] for c in card_list) <= 1

    #can only use a card if you hold it
    for c in card_list:
        for k in cats:
            prob += x[(c,k)] <= y[c]
            

    for c in card_list:
        #can only hold if eligible by score
        prob += y[c] <= eligible[c]
        # If a card is held, it must be used in at least one category. (Avoids treating 0 fee cards as free)
        prob += pulp.lpSum(x[(c,k)] for k in cats) >= y[c]


    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    #corrected optimality check
    if pulp.LpStatus[prob.status] != "Optimal":
        return None, 0.0, set(), {}, {}

    total = pulp.value(reward - fee)
    chosen = {} #realized if all x[(c,k)] = 0 itll just choose the first card.
    for k in cats:
        picked = [c for c in card_list if pulp.value(x[(c,k)]) > 0.5]
        chosen[k] = picked[0] if picked else None

    held   = {c for c in card_list if pulp.value(y[c]) > 0.5}
    
    breakdown = summarize(cats, chosen, spending, cards, trigger_bonus, fees, held)
    return chosen, total, held, breakdown

