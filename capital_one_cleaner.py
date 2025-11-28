import re

units = [
    "miles",
    "points",
    "cash back",
    "cashback",
    "cash rewards",
    "rewards",
    "percent back",
    "cents",
    "cent",
    "¢",
    "dollars"
]

types = {
    "X": "Multiplier",
    "%": "Percentage",
    "per_unit": "Per Unit",
    "flat": "Flat Amount"
}


categories = {
    "Travel": ["chase travel", "capital one travel", "amex travel", "cititravel.com", "travel center", "amextravel.com", "capital one entertainment", "purchases on travel", "hotel", "flight", "vacation", "travel", "rental car", "rental cars", "flights", "air travel", "airlines", "airline", "delta purchases", "united purchases", "southwest airlines", "united purchases","hotel", "hotels", "lodging", "hyatt stays", "marriott bonvoy", "hilton portfolio", "ihg hotels & resorts", "vacation rental", "prepaid hotel bookings", "rental car", "rental cars", "transit", "taxis", "rideshare"],
    "Groceries & Dining": ["dining", "restaurants", "takeout", "delivery services", "supermarkets", "grocery store", "grocery stores", "wholesale club", "wholesale clubs", "amazon fresh", "whole foods market", "uber eats", "grocery store", "dining", "food delivery", "restaurant", "entertainment", "streaming service"],
    "Gas & Utilities": ["gas station", "gas stations", "ev charging station", "phone plans", "cable and streaming service"],
    "Retail & Entertainment": ["entertainment", "drugstore", "drugstores", "online retail purchases", "online groceries", "online retail", "amazon.com", "partner merchants", "local transit", "online retail purchases", "T-Mobile", "REI", "Williams-Sonoma", "Pottery Barn", "West Elm", "Bass Pro Shops", "Cabela’s", "BJ’s", "Kohl’s", "streaming subscription", "streaming subscriptions", "select streaming services", "select streaming","popular streaming services"],
    "All Purchases": ["all other", "every purchase", "all purchases", "everything else", "everywhere else", "other purchases", "eligible purchases", "all other eligible purchases", "on all purchases", "unlimited cash rewards", "all other", "every purchase", "all purchases", "everything else", "everywhere else", "anywhere", "business", "other purchases", "anywhere mastercard is accepted"],
    "Caps & Limits": ["up to", "per year", "quarterly maximum", "then 1%", "first year", "after the first year", "combined purchases", "first year"]
}

FILTER_KEYWORDS = ["annual fee", "deposit", "credit line", "refundable", "initial credit line"]
FILTER_PATTERN = re.compile(r"|".join(FILTER_KEYWORDS))

def clean_annual_fee(s):
    nums = re.findall(r"\d+", s)
    if len(nums) == 1:
        return int(nums[0])
    elif "intro for the first year" in s:
        return int(nums[1])
    else:
        raise ValueError

def detect_category(clause_lower):
    for cat, keywords in categories.items():
        if any(k.lower() in clause_lower for k in keywords):
            return cat
    return "Other"

def normalize_unit(unit):
    if unit in ["or"]:
        return "dollars"
    if unit in ["¢", "cent", "cents"]:
        return "cents off"
    return unit

def clean_rate(s):
    pattern = r"(?<!\d\.)\b(?=\d+(?:\.\d+)?(?:X|%|\s+[a-zA-Z]))"
    clauses = re.split(pattern, s)
    clauses = [c.strip() for c in clauses if re.search(r"(\d|\$|¢)", c)]
    
    results = []

    for clause in clauses:
        clause_lower = clause.lower()

        m = re.search(r"(\d+(?:\.\d+)?)[¢c]?\s*off\/?(gallon|gal)", clause_lower)
        if m:
            number, _ = m.groups()
            results.append((float(number), "Flat Amount", "cents off per gallon", "Gas"))
            continue

        m_list = re.findall(r"(\d+(?:\.\d+)?)\s*([X%])\s*(?:in\s+)?([a-zA-Z\s]+)?", clause)
        
        if m_list:
            for number_str, symbol, unit_str_or_none in m_list:
                reward_type = types[symbol]

                unit = "cash back" 
                
                if unit_str_or_none:
                    found_units = [u for u in units if u in unit_str_or_none.lower()]
                    if found_units:
                        unit = found_units[0]
                        
                if unit == "cash back": 
                    full_clause_units = [u for u in units if u in clause_lower]
                    if full_clause_units:
                         unit = full_clause_units[-1]

                results.append((float(number_str), reward_type, unit, detect_category(clause_lower)))
            
            continue

        if "deposit" in clause_lower or "credit line" in clause_lower or "refundable" in clause_lower:
            deposit_matches = re.findall(r"\$?(\d+(?:\.\d+)?)", clause_lower)
            if deposit_matches:
                for val_str in set(deposit_matches):
                    val = float(val_str)
                    
                    if "initial credit" in clause_lower:
                        unit_label = "initial credit"
                    elif "deposit" in clause_lower or "refundable" in clause_lower:
                        unit_label = "minimum deposit"
                    else:
                        unit_label = "dollars"
                        
                    results.append((val, "Flat Amount", unit_label, detect_category(clause_lower)))
            continue

        m = re.search(
            r"(\d+(?:\.\d+)?)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+per\s+([\w$]+)",
            clause_lower
        )
        if m:
            number, unit, per_unit = m.groups()
            unit = normalize_unit(unit)
            results.append((float(number), "Per Unit", unit, detect_category(clause_lower)))
            continue

        m = re.search(
            r"(\d+(?:\.\d+)?)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
            clause_lower
        )
        if m:
            number, unit = m.groups()
            unit = normalize_unit(unit)
            if float(number) > 1 and not re.search(r"(\s|\.)\d+$", clause_lower):
                 results.append((float(number), "Flat Amount", unit, detect_category(clause_lower)))
            continue

    return results
 
def flatten_rewards(list_of_lists):
    """
    Flattens a list of lists into a single list.
    e.g., [[a, b], [c, d]] -> [a, b, c, d]
    """
    return [item for sublist in list_of_lists for item in sublist]

REWARD_CHECK_PATTERN = re.compile(r"\d+(?:\.\d+)?\s*[X%]")

def clean_rewards_list(lst):
    final_rewards = []

    for raw_reward_string in lst:
        s_lower = raw_reward_string.lower()

        is_deposit_string = FILTER_PATTERN.search(s_lower)

        has_reward_rate = REWARD_CHECK_PATTERN.search(raw_reward_string)

        if is_deposit_string and not has_reward_rate:
            continue

        parsed_list = clean_rate(raw_reward_string)

        final_rewards.extend(parsed_list)
        
    return final_rewards