import re

UNITS = {
    "cash back": "cash back", "rewards": "rewards", "miles": "miles", "point": "points",
    "points": "points", "membership rewards": "membership rewards points", "mr points": "membership rewards points"
}

TYPES = {
    "X": "Multiplier", "%": "Percentage", "per_unit": "Per Unit", "flat": "Flat Amount"
}

CATEGORIES = {
    "Travel": ["chase travel", "capital one travel", "amex travel", "cititravel.com", "travel center", "amextravel.com", "capital one entertainment", "purchases on travel"],
    "Hotels & Lodging": ["hotel", "hotels", "lodging", "hyatt stays", "marriott bonvoy", "hilton portfolio", "ihg hotels & resorts", "vacation rental", "prepaid hotel bookings"],
    "Car/Transit": ["rental car", "rental cars", "transit", "taxis", "rideshare", "parking", "tolls", "trains", "buses", "local transit", "commuting"],
    "Groceries & Dining": ["dining", "restaurants", "takeout", "delivery services", "supermarkets", "grocery store", "grocery stores", "wholesale club", "wholesale clubs", "amazon fresh", "whole foods market", "uber eats"],
    "Gas & Utilities": ["gas station", "gas stations", "ev charging station", "streaming subscription", "streaming subscriptions", "select streaming services", "select streaming", "phone plans", "cable and streaming service", "popular streaming services"],
    "Retail & Entertainment": ["entertainment", "drugstore", "drugstores", "online retail purchases", "online groceries", "online retail", "amazon.com", "partner merchants", "local transit", "online retail purchases"],
    "Flights/Airlines": ["flights", "air travel", "airlines", "airline", "delta purchases", "united purchases", "southwest airlines", "united purchases"],
    "All Purchases": ["all other", "every purchase", "all purchases", "everything else", "everywhere else", "other purchases", "eligible purchases", "all other eligible purchases", "on all purchases", "unlimited cash rewards"],
    "Caps & Limits": ["up to", "per year", "quarterly maximum", "then 1%", "first year", "after the first year", "combined purchases", "first year"]
}

REWARD_CHECK_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*([X%]|x\s+points|x\s+miles)") 
FILTER_KEYWORDS = ["annual fee", "deposit", "credit line", "refundable", "minimum deposit"]
FILTER_PATTERN = re.compile(r"|".join(FILTER_KEYWORDS))

def normalize_unit(unit_str):
    if not unit_str: return "rewards"
    unit_str = unit_str.lower().strip()
    if "membership rewards" in unit_str: return "membership rewards points"
    for key, normalized in UNITS.items():
        if key in unit_str: return normalized
    if "cash" in unit_str: return "cash back"
    if "point" in unit_str: return "points"
    if "mile" in unit_str: return "miles"
    return "rewards"

def detect_category(clause_lower):
    for cat, keywords in CATEGORIES.items():
        if any(k.lower() in clause_lower for k in keywords): return cat
    return "Other"

def clean_rate(s: str) -> list[tuple]:
    results = []
    s_lower = s.lower().replace("®", "").replace("℠", "").replace("™", "")
    clauses = [s]
    
    for clause in clauses:
        clause_lower = clause.lower()

        m_list = re.findall(
            r"(\d+(?:\.\d+)?)\s*(?:[X%]|x\s+points|x\s+miles|cash\s+back)\s*(.+?)(?:\.|$)", 
            clause, re.IGNORECASE
        )
        if m_list:
            for number_str, unit_phrase in m_list:
                val = float(number_str)
                
                if '%' in clause:
                    rate_type = 'Percentage'
                else:
                    rate_type = 'Multiplier'
                
                unit = normalize_unit(unit_phrase)
                category = detect_category(clause_lower)
                
                results.append((val, rate_type, unit, category))
            
            continue

        m_per_unit = re.search(
            r"(\d+(?:\.\d+)?)\s*([a-zA-Z\s]+)\s*(per\s+\$1\s+spent|per\s+\$1|per\s+dollar\s+spent)", 
            clause, re.IGNORECASE
        )
        if m_per_unit:
            val = float(m_per_unit.group(1))
            unit = normalize_unit(m_per_unit.group(2))
            rate_type = TYPES['per_unit']
            category = detect_category(clause_lower)
            results.append((val, rate_type, unit, category))
            
            continue 
            
    return results

def clean_rewards_list(raw_rewards_list: list[str]) -> list[tuple]:
    final_rewards = []
    
    for raw_reward_string in raw_rewards_list:
        s_lower = raw_reward_string.lower()
        has_reward_rate = REWARD_CHECK_PATTERN.search(raw_reward_string)
        is_deposit_string = FILTER_PATTERN.search(s_lower)
        
        if is_deposit_string and not has_reward_rate:
            continue

        parsed_list = clean_rate(raw_reward_string)
        
        final_parsed_list = [
            r for r in parsed_list 
            if r[3] != "Caps & Limits" 
        ]
        
        final_rewards.extend(final_parsed_list)
        
    return final_rewards

def clean_annual_fee(s):
    nums = re.findall(r"\d+", s)
    if len(nums) == 1:
        return int(nums[0])
    elif "intro" in s:
        return int(nums[1])
    else:
        return int(nums[0])