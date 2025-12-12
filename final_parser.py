import pandas as pd
from chase_scraper import scrape_chase
from nerdwallet_scraper import scrape_nerdwallet
import re
import string
import statistics

class Parsing:
    def __init__(self, card_df):
        self.card_df = card_df

    def clean_text(self, text_str):
        """
        Removes explanatory sentences that break the parser
        """
        # Handle case where rewards might be a list
        if isinstance(text_str, list):
            text_str = " ".join(text_str)
    
        #split sentences based off...
        sentences = re.split(r'(?<=[.!?])\s+', text_str)

        # Phrases that indicate explanations
        useless_sentences = [
            "that means",
            "for example",
            "in other words",
            "this means",
            "this lets",
            "this gives",
            "you'll get",
            "you will get",
            "you can",
            "you may",
            "to calculate",
            "this allows",
            "this provides"
        ]

        # Filter out sentences that mention "APR" (case-insensitive)
        sentences = [s for s in sentences if "apr" not in s.lower()]

        #for the new cleaneed text
        cleaned = []

        for s in sentences:
            lower = s.strip().lower()
            if not any(lower.startswith(junk) for junk in useless_sentences):
                cleaned.append(s)

        #returns a cleaned string of the text
        return " ".join(cleaned)

    
    def reward_type(self, text_str):
        """
        Parse a reward text string and extract
            - changing reward words
            - timing of the changing reward
        """

        # Handle case where rewards might be a list
        if isinstance(text_str, list):
            text_str = " ".join(text_str)
    
        # The key words to find tiered or trigger rewards
        changing_reward_list = ["after", "first", "beyond", "over"]

        # Key words to find when these triggers are implemented
        time_list = ["year", "month", "day", "months", "years", "days", 
                     "quarter", "quarterly", "annually", "each month", "each year"]
        
        # limits so it doesn't overestimate
        VALID_LIMITS = {
            "day": 365,
            "days": 365,
            "month": 36,
            "months": 36,
            "year": 5,
            "years": 5,
            "quarter": 12,
            "quarterly": 12,
        }

        # Make the text string clean by lowering, splitting the words
        lower_text_str = text_str.lower().split()

        # One list to store the trigger words and a dictionary to store the numbers/timing
        found_triggers = []
        timing_triggers = {}

        i = 0

        while i < len(lower_text_str):
            clean_word = lower_text_str[i].strip(string.punctuation)

            # Detect "up to"
            if clean_word == "up" and (i + 1) < len(lower_text_str):
                next_word = lower_text_str[i + 1].strip(string.punctuation)
                if next_word == "to":
                    trigger = "up to"
                    found_triggers.append(trigger)

                    number_found = None
                    timing_unit = None

                    # Search for numbers and timing units after this trigger
                    for j in range(i + 2, len(lower_text_str)):

                        word_j = lower_text_str[j].strip(string.punctuation).replace(',', '').replace('$', '')

                        #accept numbers that are immediately followed by a timing unit
                        if re.match(r'^\d+(\.\d+)?$', word_j):

                            #Look ahead to next token to see if it's a time unit
                            if j + 1 < len(lower_text_str):
                                next_unit = lower_text_str[j + 1].strip(string.punctuation)

                                if next_unit in time_list:
                                    number_found = float(word_j)
                                    timing_unit = next_unit

                                    #Ignore unrealistic values
                                    if timing_unit in VALID_LIMITS and number_found > VALID_LIMITS[timing_unit]:
                                        break

                                    timing_triggers.setdefault(trigger, []).append({
                                        "number": number_found,
                                        "unit": timing_unit
                                    })
                                    break

                        #Skip all other numbers ($300, 5%, 1500, 2024, 10x, etc.)
                        continue

                    i += 2
                    continue

            #Detect other changing reward words
            elif clean_word in changing_reward_list:
                trigger = clean_word
                found_triggers.append(trigger)

                number_found = None
                timing_unit = None

                for j in range(i + 1, len(lower_text_str)):

                    word_j = lower_text_str[j].strip(string.punctuation).replace(',', '').replace('$', '')

                    #Accept only numbers that are followed by a time unit
                    if re.match(r'^\d+(\.\d+)?$', word_j):

                        if j + 1 < len(lower_text_str):
                            next_unit = lower_text_str[j + 1].strip(string.punctuation)

                            if next_unit in time_list:
                                number_found = float(word_j)
                                timing_unit = next_unit

                                if timing_unit in VALID_LIMITS and number_found > VALID_LIMITS[timing_unit]:
                                    break

                                timing_triggers.setdefault(trigger, []).append({
                                    "number": number_found,
                                    "unit": timing_unit
                                })
                                break

                        continue

                i += 1
                continue

            i += 1

        return found_triggers, timing_triggers
    
    def annual_fee_parse(self, text_str):
        """
        Parses through the annual fee and makes it so it's only one singular integer
        """
        # Handle case where rewards might be a list
        if isinstance(text_str, list):
            text_str = " ".join(text_str)

        #what characters are valid in the annual fee
        valid_annual_fee = "0123456789-"

        #new string and list to get the annual fee
        clean_annual_list = []
        clean_annual_string = ""
 
        index = 0
        first_num = 0.0
        second_num = 0.0

        #goes through the text string and appends all of the valid characters  
        for letter in text_str:
            if letter in valid_annual_fee:
                clean_annual_list.append(letter)
        
        #if it has a start with 0 and than x.. remove the zero at the beginning and just take the second number
        if len(clean_annual_list) > 2 and clean_annual_list[0] == "0":
            clean_annual_list.pop(0)

        
        #make into a string
        for letter in clean_annual_list:
            clean_annual_string = clean_annual_string + letter

        #split it and get the median of two numbers if it's a range
        for letter in clean_annual_string:
            if letter == "-":
                first, second = clean_annual_string.split("-") #split based off -
                median = statistics.median([float(first), float(second)])

                return median

        #returns a singular float
        return float(clean_annual_string)

    def extract_rate_data(self, match):
        """
        Process a match into a unit
        """
        
        dollar1, num1, dollar2, num2, unit = match.groups()

        # Remove commas
        num1 = num1.replace(",", "")
        if num2:
            num2 = num2.replace(",", "")

        # Determine numeric value
        if num2: 
            #median if theres two numbers
            value = statistics.median([float(num1), float(num2)])
        else:
            value = float(num1)

        #map for the units
        unit_map = {
            "$": "$", "%": "percent", "x": "multiplier",
            "point": "points", "points": "points",
            "mile": "miles", "miles": "miles"
        }
    
        unit_final = None

        if dollar1 or dollar2:
            unit_final = "$"
        elif unit:
            unit_final = unit_map.get(unit.lower(), unit.lower()) 
        else:
            # Default
            unit_final = "points" 

        #return a dict with the rate and unit
        return {"rate": value, "unit": unit_final}

    def reward_specification(self, text_str):
        """
        Parse a reward text string and extract (Category, Rate, Unit) as a single object.
        """

        if isinstance(text_str, list):
            text_str = " ".join(text_str)

        text_lower = text_str.lower()
        final_rewards = []
    
        #the reward categories that exist
        reward_focus_dict = {
            "travel": ["travel", "hotel", "vacation", "flight", "airline", "miles", "rental", "tsa", "lyft", "uber"],
            "dining": ["dining", "restaurant", "takeout", "dashpass", "doordash"],
            "entertainment": ["entertainment", "streaming", "netflix"],
            "groceries": ["groceries", "supermarket"],
            "other stores": ["drugstore"],
            "transit": ["gas", "transit"],
            "other": ["other"],
            "every": ["every", "everything", "all", "unlimited"]
        }

        #pattern to make sure everything is valid, get the numbers, and get the units
        pattern = re.compile(
            r"(?:earn|get|receive|reward|back|points|miles|credit)?\s*?"
            r"(\$)?(\d[\d,]*(?:\.\d+)?)"
            r"(?:\s*-\s*(\$)?(\d[\d,]*(?:\.\d+)?))?"
            r"\s*(%|x|points?|mile|miles|points per \$|points for every \$|points per dollar|points for each dollar)?\b",
            re.IGNORECASE
        )

        #find all of the matches to the pattern in the text
        for match in pattern.finditer(text_str):
            match_start = match.start()
        
            # Get context- look 50 characters in the future
            context_window = text_str[max(0, match_start - 50):match_start].lower()

            # Extract the Category based on the context window
            category_found = None
            for category, keyword_list in reward_focus_dict.items():
                if any(keyword in context_window for keyword in keyword_list):
                    category_found = category
                    break
        
            # If no specific category found, check the text after the number
            if not category_found:
                post_match_text = text_str[match.end():min(len(text_str), match.end() + 100)].lower()
                for category, keyword_list in reward_focus_dict.items():
                    if any(keyword in post_match_text for keyword in keyword_list):
                        category_found = category
                        break
        
            # If still no specific category, default every
            if not category_found:
                category_found = "every"

            #use the helper function to get the rate data
            rate_data = self.extract_rate_data(match)
        
            #Check text right after the match to exclude time-based numbers
            post_match_index = match.end()
            post_text = text_str[post_match_index:post_match_index+20].lower()
        
            if re.match(r"\s*(day|days|month|months|year|years|quarter)\b", post_text, re.IGNORECASE):
                continue
            
            #add everything to the dict
            final_rewards.append({
                "category": category_found, 
                "rate": rate_data['rate'], 
                "unit": rate_data['unit']
            })

        #Finally a dictionary with the category, rate, and unit inside and removes duplicates
        return list({frozenset(d.items()): d for d in final_rewards}.values())

    def CleanParsedData(self, df):
        """
        The parser sometimes picks up obviously wrong data. This will filter it out. 
        """

        #make a copu of the df
        df_clean = df.copy()
    
        for idx, row in df_clean.iterrows():
            if row["structured_rewards"]: 
                cleaned_rewards = []
                for num_dict in row["structured_rewards"]:
                    rate = num_dict["rate"]
                    unit = num_dict["unit"]
                
                    #skip unwanted stuff
                    if unit in ["points", "miles", "$", "percent", "multiplier"]:
                        #years
                        if 1900 < rate < 2100 or 2024 < rate < 2030:
                            continue
                        #multipliers exceeding 20
                        if unit == "multiplier" and rate > 20:
                            continue
                        #percents exceeding 100
                        if unit == "percent" and rate > 100:
                            continue
                        #credit exceeding 10k
                        if unit == "$" and rate > 10000:
                            continue
                        #skip small dollar amounts
                        if unit == "$" and rate < 1:
                            continue
                        #make sure the points/miles are reasonable
                        if unit in ["points", "miles"] and rate > 200000:
                            continue
                
                    cleaned_rewards.append(num_dict)
                df_clean.at[idx, "structured_rewards"] = cleaned_rewards
    
        return df_clean

    def NewDataFrame(self):
        """
        Returns a new data frame with additional columns
        """
        #create a copy of the original df
        df = self.card_df.copy()

        #initalize new columns for the df
        df["structured_rewards"] = None
        df["timing_triggers"] = None

        for idx, row in df.iterrows():
            rewards = row["rewards"]
            annual_fee = row["annual_fee"]

            #clean the reward 
            rewards = self.clean_text(rewards)
            df.at[idx, "rewards"] = rewards

            # Parse rewards
            structured_rewards = self.reward_specification(rewards) 
            df.at[idx, "structured_rewards"] = structured_rewards

            # Parse triggers
            triggers, timing = self.reward_type(rewards)
            df.at[idx, "timing_triggers"] = timing

            #change annual fee to be clean
            clean_annual_fee = self.annual_fee_parse(annual_fee)
            df.at[idx, 'annual_fee'] = clean_annual_fee


        #return the new dataframe
        return self.CleanParsedData(df)

#for me to debug stuff
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)


df = scrape_chase()
print(df['rewards'])

parsed = Parsing(df)
new_df = parsed.NewDataFrame()

print(new_df['rewards'])

new_df.to_csv('chase_dataframe.csv')

df = scrape_nerdwallet()
print(df['annual_fee'])

new_df = parsed.NewDataFrame()

print(new_df['annual_fee'])
