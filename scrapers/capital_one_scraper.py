from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re
from tqdm import tqdm
from scrapers.scraper_core import link2soup
import pandas as pd
from cleaners.capital_one_cleaner import clean_annual_fee, clean_rewards_list

score_conversion = {
    "Good-Excellent": "Very Good",
    "Rebuilding": "Poor"
}

def scrape_capital_one(score = False, clean = False) -> pd.DataFrame:
    """
    Gets credit card data from Capital One.

    Args:
        clean(bool): Whether to clean the data after scraping. Defaults to False.
        score(bool): Whether to include credit score information. Defaults to False.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped credit card data.
    """

    soup = link2soup("https://www.capitalone.com/credit-cards/compare/")
    card_container = soup.select("card-product-all-cards-list-item")
    card_container = card_container[0:-1] #have some weird formatting with an extra block

    cards = {
        "name" : [],
        "issuer" : [],
        "annual_fee" : [],
        "rewards" : []
    }
    if score:
        cards["score"] = []

    for card in tqdm(card_container):
        name = re.sub(r'[^ -~]', '', card.select("a.product-name.ng-star-inserted")[0].text) #clear out weird characters
        cards["name"].append(name)
        rewards = [r for r in re.sub("Rewards", "", card.select("div.feature.ng-star-inserted")[0].text).strip().split(". ") if r]
        cards["rewards"].append(rewards)
        
        annual_fee = re.sub("Annual Fee", "", card.select("div.feature.ng-star-inserted")[1].text)
        cards["annual_fee"].append(annual_fee)

        if score:
            credit_score = card.select("button.credit-level-button")[0].text
            credit_score = re.sub(" Credit", "", credit_score)
            credit_score = credit_score.strip()               
            credit_score = credit_score.replace("\xa0", "")   
            credit_score = credit_score.replace("–", "-")     
            credit_score = credit_score.title()               
            credit_score = score_conversion.get(credit_score, credit_score)
            
            cards["score"].append(credit_score)

        
        cards["issuer"].append("Capital One")

    df = pd.DataFrame(cards)

    if clean:
        df["clean_annual_fee"] = df["annual_fee"].apply(clean_annual_fee)
        df["clean_rewards"] = df["rewards"].apply(clean_rewards_list)
        
    return df