from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re
from tqdm import tqdm
from scraper_core import link2soup
import pandas as pd

def scrape_capital_one():
    soup = link2soup("https://www.capitalone.com/credit-cards/compare/")
    card_container = soup.select("card-product-all-cards-list-item")
    card_container = card_container[0:-1] #have some weird formatting with an extra block

    cards = {
        "name" : [],
        "issuer" : [],
        "annual_fee" : [],
        "rewards" : []
    }

    for card in tqdm(card_container):
        name = re.sub(r'[^ -~]', '', card.select("a.product-name.ng-star-inserted")[0].text) #clear out weird characters
        cards["name"].append(name)
        rewards = [r for r in re.sub("Rewards", "", card.select("div.feature.ng-star-inserted")[0].text).strip().split(".") if r]
        cards["rewards"].append(rewards)
        
        annual_fee = re.sub("Annual Fee", "", card.select("div.feature.ng-star-inserted")[1].text)
        cards["annual_fee"].append(annual_fee)
        
        cards["issuer"].append("Capital One")

    df = pd.DataFrame(cards)
    return df