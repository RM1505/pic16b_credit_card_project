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
    # pick issuer or default
    issuer_table = POINTS_TO_CASH.get(issuer, POINTS_TO_CASH["default"])

    # try issuer-specific valuation
    if unit in issuer_table:
        return issuer_table[unit]

    # fallback to default valuation for this unit
    return POINTS_TO_CASH["default"].get(unit, 0.01)

def get_dicts(df):
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
    breakdown = {}

    for k in cats:
        c = chosen[k]                      # card chosen for category k
        spend = spending[k]                # dollars spent in that category
        rate = cards[c]["rates"].get(k, 0.0)
        trig = trigger_bonus[(c, k)]       # from your precomputed trigger table
        reward_val = spend * rate + trig
        fee_val = fees[c] if c in held else 0   # fee counted once if held
        breakdown[k] = {
            "card": c,
            "spend": spend,
            "rate": rate,
            "trigger_bonus": trig,
            "raw_reward": spend * rate,
            "total_reward": reward_val,
            "fee": fee_val,
            "net_contribution": reward_val - fee_val,
            "equation": f"{spend} * {rate} + {trig} - {fee_val}"
        }
    return breakdown

def trigger_bonuses(card_list, cards, spending, cats):
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
    cards[card] = {"min_score": int, "rates": {category: rate}}
    fees[card]  = annual fee
    spending[category] = spend in that category
    """
    # For Trigger-Based: 
    # Given spending amount in a category you can determine if they will hit a trigger and just add that to reward
    # Note: its hard to account for triggers that might not stack. for ex if you spend 100 get 20 but if you spend 200 and get 40 you shouldnt apply both.
    # Im gonna assume that if you exceed the spend for a trigger that ur gonna get that bonus
    
    # For point distribution: TODO
    # Take point equivalents by category consider combinations with constraint as points earned. Create card copies

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
    if pulp.LpStatus[pulp.LpStatusOptimal] != 'Optimal' and pulp.LpStatus[prob.status] != 'Optimal':
        return "No optimal solution found", 0.0, set(), {}

    total = pulp.value(reward - fee)
    chosen = {k: max(card_list, key=lambda c: pulp.value(x[(c,k)])) for k in cats}
    held   = {c for c in card_list if pulp.value(y[c]) > 0.5}
    
    breakdown = summarize(cats, chosen, spending, cards, trigger_bonus, fees, held)
    return chosen, total, held, breakdown

