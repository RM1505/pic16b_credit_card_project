import pandas as pd
from chase_scraper import scrape_chase
import re
import string

class Parsing_Chase:
    def __init__(self, card_df):
        self.card_df = card_df
    
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
        time_list = ["year", "month", "day", "months", "years", "days"]

        # Make the text string clean by lowering and splitting the words
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
                    trigger_index = i + 2

                    # Search for numbers and timing units after this trigger
                    number_found = None
                    timing_unit = None
                    for j in range(trigger_index, len(lower_text_str)):
                        word_j = lower_text_str[j].strip(string.punctuation).replace(',', '').replace('$', '')
                        if re.match(r'\d+(\.\d+)?', word_j):
                            number_found = word_j
                        elif lower_text_str[j].strip(string.punctuation) in time_list and number_found:
                            timing_unit = lower_text_str[j].strip(string.punctuation)
                            if trigger not in timing_triggers:
                                timing_triggers[trigger] = []
                            timing_triggers[trigger].append({"number": number_found, "time": timing_unit})
                            break
                    i += 2
                    continue

            # Detect other changing reward words
            elif clean_word in changing_reward_list:
                trigger = clean_word
                found_triggers.append(trigger)
                trigger_index = i + 1

                number_found = None
                timing_unit = None
                for j in range(trigger_index, len(lower_text_str)):
                    word_j = lower_text_str[j].strip(string.punctuation).replace(',', '').replace('$', '')
                    if re.match(r'\d+(\.\d+)?', word_j):
                        number_found = word_j
                    elif lower_text_str[j].strip(string.punctuation) in time_list and number_found:
                        timing_unit = lower_text_str[j].strip(string.punctuation)
                        if trigger not in timing_triggers:
                            timing_triggers[trigger] = []
                        timing_triggers[trigger].append({"number": number_found, "unit": timing_unit})
                        break

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
        valid_annual_fee = "0123456789"

        #new string and list to get the annual fee
        clean_annual_list = []
        clean_annual_string = ""

        #goes through the text string and appends all of the valid characters  
        for letter in text_str:
            if letter in valid_annual_fee:
                clean_annual_list.append(letter)
        
        #if it has a start with 0 and than x.. remove the zero at the beginning and just take the second number
        if  len(clean_annual_list) > 2 and clean_annual_list[0] == "0":
            clean_annual_list.pop(0)
        
        #make into a a string
        for letter in clean_annual_list:
            clean_annual_string = clean_annual_string + letter

        #returns a singular integer
        return int(clean_annual_string)

    def reward_specification(self, text_str):
        """
        Parse a reward text string and extract:
        - reward focus categories
        - reward type
        - list of numerical rewards as well as the unit
        """

        # Handle case where rewards might be a list
        if isinstance(text_str, list):
            text_str = " ".join(text_str)

        # Lowercase version for searching keywords
        text_lower = text_str.lower()

        #the reward categories that exist
        reward_focus_dict = {
            "travel":        ["travel", "hotel", "vacation", "flight", "airline", "miles", "rental", "tsa"],
            "dining":        ["dining", "restaurant", "takeout"],
            "entertainment": ["entertainment", "streaming"],
            "groceries":     ["groceries", "supermarket"],
            "other stores":  ["drugstore"],
            "transit":       ["gas", "transit"],
            "other":         ["other"],
            "every":         ["every", "everything", "all", "unlimited"]
        }

        #The reward types that exist
        reward_type_list = ["miles", "cash back", "points", "credit", "cash rewards"]

        #the numbers that exist
        number_chars = "0123456789,.$%x"

        categories_set = set()
        reward_list = []
        found_numbers = []

        current_number = ""
        current_unit = "points"

        #find the focus of the reward
        for category, keyword_list in reward_focus_dict.items():
            for keyword in keyword_list:
                if keyword in text_lower:
                    categories_set.add(category)

        #find the type of the reward
        for reward in reward_type_list:
            if reward in text_lower:
                reward_list.append(reward)

        #find the number and unit associated with the reward
        pattern = re.compile(r"(\d+(?:,\d+)?(?:\.\d+)?)(%|x| points)?")
        for match in pattern.finditer(text_str):
            rate, unit = match.groups()
            if unit is None:
                #default
                unit = "points"
            unit = unit.strip()
            found_numbers.append({"rate": rate, "unit": unit})

        return list(categories_set), reward_list, found_numbers

    def NewDataFrame(self):
        """
        Returns a new data frame with additional columns
        """
        #create a copy of the original df
        df = self.card_df.copy()

        #initalize new columns for the df
        df["categories"] = None
        df["reward_list"] = None
        df["found_numbers"] = None
        df["found_triggers"] = None
        df["timing_triggers"] = None

        for idx, row in df.iterrows():
            rewards = row["rewards"]
            annual_fee = row["annual_fee"]

            # Parse rewards
            categories, reward_list, numbers = self.reward_specification(rewards)
            df.at[idx, "categories"] = categories
            df.at[idx, "reward_list"] = reward_list
            df.at[idx, "found_numbers"] = numbers

            # Parse triggers
            triggers, timing = self.reward_type(rewards)
            df.at[idx, "found_triggers"] = triggers
            df.at[idx, "timing_triggers"] = timing

            #change annual fee to be clean
            clean_annual_fee = self.annual_fee_parse(annual_fee)
            df.at[idx, 'annual_fee'] = clean_annual_fee


        #return the new dataframe
        return df

#for me to debug stuff
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)


df = scrape_chase()
print(df['annual_fee'])

parsed = Parsing_Chase(df)
new_df = parsed.NewDataFrame()

print(new_df['annual_fee'])

new_df.to_csv('chase_dataframe.csv')
