from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re
from tqdm import tqdm
from scraper_core import link2soup, CreditCard 

def scrape_capital_one():
    soup = link2soup("https://www.capitalone.com/credit-cards/compare/")
    card_container = soup.select("card-product-all-cards-list-item")
    card_container = card_container[0:-1] #have some weird formatting with an extra block

    cards = []

    for card in tqdm(card_container):
        name = re.sub(r'[^ -~]', '', card.select("a.product-name.ng-star-inserted")[0].text) #clear out weird characters
        try:
            welcome_amount = card.select("div.short-desc.ng-star-inserted")[0].text
        except IndexError:
            welcome_amount = None
        rewards = re.sub("Rewards", "", card.select("div.feature.ng-star-inserted")[0].text)
        annual_fee = re.sub("Annual Fee", "", card.select("div.feature.ng-star-inserted")[1].text)
        apr = re.sub("Purchase Rate", "", card.select("div.feature.ng-star-inserted")[2].text)
        card_obj = CreditCard(name, annual_fee, welcome_amount, apr, rewards)
        cards.append(card_obj)

    return cards