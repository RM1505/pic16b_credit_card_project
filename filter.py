import pandas as pd

class Parse:
    def __init__(self, cards):
        """
        puts the attributes from the credit card objects and separates them into a text
        """
        #this is where the credit card object attributes will all be saved
        self.card_name = [card.name for card in cards]
        self.annual_fee = [card.annual_fee for card in cards]
        self.welcome_amount = [card.welcome_amount for card in cards]
        self.apr = [card.apr for card in cards]
        self.rewards = [card.rewards for card in cards]

        #this is the new list after they're parsed
        self.parsed_rewards = []
        self.parsed_annual_fee = []
        self.parsed_welcome_amount = []

    def ParseThrough(self):
        """
        Create a new lists for everything that needs parsing
        """
        #parse through the rewards and build a new list
        for text_str in self.rewards:
            self.parsed_rewards.append(self.RewardParsing(text_str))

        #parse through the annual fee and build a new list
        for text_str in self.annual_fee:
            self.parsed_annual_fee.append(self.CleanAnnual(text_str))

        #parse through welcome amount and build a new list
        for text_str in self.welcome_amount:
            self.parsed_welcome_amount.append(self.CleanWelcome(text_str))
         
    def RewardParsing(self, text_str):
        """
        This function takes the card.rewards, and parses through them for key information
        It returns a dictionary with the reward focus, type, and the rate with the unit
        """
        # Handle case where rewards might be a list instead of a string
        if isinstance(text_str, list):
            text_str = " ".join(text_str)
        
        # keywords to find in data to split into categories
        reward_focus_dict = {
        "travel" : ["travel", "hotel", "vacation", "flight", "airline", "miles", "rental", "TSA"],
        "dining" : ["dining", "restaurant", "takeout"],
        "entertainment" : ["entertainment", "streaming", ],
        "groceries" : ["groceries", "supermarket"],
        "other stores" : ["drugstore"],
        "transit" : ["gas", "transit"],
        "other" : ["other"],
        "every" : ["every", "everything", "all"]}

        # keywords for the reward types you can get
        reward_type_list = ["miles", "cash back", "points", "credit"]

        #list of numbers for the reward rates
        number_chars = "0123456789,.$"

        #set to store the reward focus
        categories_set = set()
        
        #list to store the reward type
        reward_list = []
        
        #list to store numbers found in total
        found_numbers = []

        #string to store the number you're on and the unit you're on
        current_number = ""
        current_unit = "points"

        #lower all capitals
        text_list = text_str.lower()

        #search the text string for categories and then add them to a list
        for category, keyword_list in reward_focus_dict.items():
            for keyword in keyword_list:
                if keyword in text_list:
                    categories_set.add(category)
                
        #search for the type of reward
        for reward in reward_type_list:
            if reward in text_list:
                reward_list.append(reward)

        #find the corresponding number in the sentence
        for char in text_str:
            #if a number exists, add it to the string
            if char in number_chars:
                current_number += char
            elif char == '$' and current_number:
                current_unit = '$'
            elif char == '%' and current_number:
                current_unit = '%'
            elif char == 'x' and current_number:
                current_unit = 'x'
            else:
                #if a current number exists and the next number isn't part of the number_cars append it to found_numbers and reset current_number
                if current_number:
                
                    #clean the number string by deleting , and $
                    cleaned_number = current_number.replace(',', '').replace('$', '').strip()
                    
                    #add the number and unit to string
                    if cleaned_number and cleaned_number != '.':
                        #store dict in the list
                        found_numbers.append({'rate': cleaned_number, 'unit': current_unit})

                    current_number = ""
                    current_unit = "points"
                
        #if the sentence ends with a number...
        if current_number:
            # clean the number string by deleting , and $
             cleaned_number = current_number.replace(',', '').replace('$', '').strip()

            # add the number and unit to string
            if cleaned_number and cleaned_number != '.':
                # store dict in the list
                found_numbers.append({'rate': cleaned_number, 'unit': current_unit}) 
                
        #returns a dictionary containing a list of the categories, a designation for the reward in the form of a list, and a string of the rate of the reward   
        return {
        "focus": list(categories_set),
        "type": reward_list,
        "rate with unit": found_numbers
    }

    def CleanWelcome(self, text_str):
        """
        This function cleans the welcome bonus amount and extracts the numerical value
        Returns the highest numerical value found as float
        """

        #if the card doesn't have a welcome amount return 0
        if text_str == None or text_str == "None" or text_str == "none" or text_str == "N/A":
            return [0]

        #list to store numbers found in total
        found_numbers = []

        #list of numbers for the welcome rates
        number_chars = "0123456789,.$"

        #string to store the number you're on and the unit you're on
        current_number = ""
        current_unit = "points"

        #clean the text by lowering all capitals
        cleaned_text = text_str.lower()

        #find the corresponding number in the sentence
        for char in text_str:
            #if a number exists, add it to the string
            if char in number_chars:
                current_number += char
            elif char == '$' and current_number:
                current_unit = '$'
            elif char == '%' and current_number:
                current_unit = '%'
            elif char == 'x' and current_number:
                current_unit = 'x'
            else:
                #if a current number exists and the next number isn't part of the number_cars append it to found_numbers and reset current_number
                if current_number:
                
                    #clean the number string by deleting , and $
                    cleaned_number = current_number.replace(',', '').replace('$', '').strip()

                    #add the number and unit to string
                    if cleaned_number and cleaned_number != '.':
                        #store dict in the list
                        found_numbers.append({'rate': cleaned_number, 'unit': current_unit})

                    current_number = ""
                    current_unit = "points"
                
        #if the sentence ends with a number...
        if current_number:
            # clean the number string by deleting , and $
            cleaned_number = current_number.replace(',', '').replace('$', '').strip()

            # add the number and unit to string
            if cleaned_number and cleaned_number != '.':
                # store dict in the list
                found_numbers.append({'rate': cleaned_number, 'unit': current_unit}) 

        #Returns a dict of all of the numbers and their units
        return found_numbers

    
    def CleanAnnual(self, text_str):
        """
        This function takes the annual rate and outputs the most relevant number for the annual rate as an int
        """
        #clean the text by splitting it into words and lowering all capitals
        cleaned_text = text_str.lower().split()
        cleaned_text2 = text_str.lower()

        #make a string for the annual rate
        annual_rate = ""

        #list for if the annual rate changed
        annual_list = []
    
        #list of numbers for the reward rates
        number_chars = "0123456789,."

        #if the cleaned_text only has one word...
        if len(cleaned_text) == 1:
            fee_str = cleaned_text[0]

            if fee_str == '0' or fee_str == '0.0':
                return 0.0

            #for each character, add it to the annual rate
            for char in fee_str:
                annual_rate += char 

        #if it's not just one word...
        else:
            for char in cleaned_text2 :
                if char in number_chars:
                    annual_rate  += char
                else: 
                    if annual_rate:
                        annual_list.append(annual_rate)
            annual_rate = annual_list[-1] 

        #if it cant find any numbers...
        if not annual_rate:
            return 0

        #clean the text...
        annual_rate = annual_rate.replace('$', '').replace(',', '').strip()

        #returns the annual_rate as a singular float
        return float(annual_rate)

    def MakeDataFrame(self):
        """
        Make a dataframe of all the data
        """

        #run the parse through function to parse through all the data
        self.ParseThrough()
        
        #compile all of the lists in a dictionary
        data = {
            'card_name': self.card_name,
            'annual_fee': self.parsed_annual_fee,
            'welcome_amount': self.parsed_welcome_amount,
            'apr': self.apr,
            'rewards': self.parsed_rewards
            
        }

        #make a data frame out of the data
        df = pd.DataFrame(data)

        #return a data frame of everything
        return df



                

    
    
        
