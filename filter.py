def RewardFocus(text_str):
    #key words to find in data to split into categories
    reward_focus_dict = {
    "travel" : ["travel", "hotel", "vacation", "flight", "airline", "miles", "rental", "TSA"],
    "dining" : ["dining", "restaurant", "takeout"],
    "entertainment" : ["entertainment", "streaming", ],
    "groceries" : ["groceries", "supermarket"],
    "other stores" : ["drugstore"],
    "transit" : ["gas", "transit"],
    "other" : ["other"]}

    #set to store the sentences
    categories_set = set()

    #lower all capitals
    text_list = text_str.lower()

    #search the text string for categories and the
    for category, keyword_list in reward_focus_dict.items():
        for keyword in keyword_list:
            if keyword in text_list:
                categories_set.add(category)
                
    #returns a list of the categories     
    return list(categories_set)

def RewardType(text_str):
    #key words for the reward types you can get
    reward_type_list = ["miles", "cash back", "points", "credit"]

    #set to store the sentences
    reward_list = []

    #lower all capitals
    text_list = text_str.lower()

    for reward in reward_type_list:
        if reward in text_list:
            reward_list.append(reward)
        

    #returns a designation for the reward in the form of a list
    return reward_list

def NumberAssociation(text_str):
    #list of numbers
    number_chars = "0123456789,.xX$"

    #numbers found in total
    found_numbers = []

    #number your on
    current_number = ""

    #mistakes to get reprocessed
    mistakes = ["x", "X", ".", ","]
    
    #find the corresponding number in the sentence
    for char in text_str:
        #if a number exists add it to the string
        if char in number_chars:
            current_number += char
        else:
            #if a current number exists and the next number isn't part of the number_cars append it to found_numbers and reset current_number
            if current_number:
                found_numbers.append(current_number)
                current_number = ""
                
    #parse through and check for mistakes
    for number in found_numbers:
        for mistake in mistakes:
            if number == mistake:
                found_numbers.remove(mistake)

    #return the numbers
    return found_numbers


                

    
    
        
