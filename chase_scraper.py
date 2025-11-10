from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re
from tqdm import tqdm
from scraper_core import link2soup, CreditCard

def scrape_chase():
    BASE = "https://creditcards.chase.com"
    LINK = "https://creditcards.chase.com/all-credit-cards?CELL=6TKX"
    
    soup = link2soup(LINK)
    
    card_containers = soup.select("div.cmp-cardsummary__inner-container")
    
    cards = []
    
    for card in tqdm(card_containers):
        title_container = card.select("div.cmp-cardsummary__inner-container__title h2 a")[0]
        name = re.sub(r"\bLinks to product page\b", "", title_container.get_text(), flags=re.I).strip()
        url = urljoin(BASE, title_container.get("href"))
    
        summary_container = card.select("div.cmp-cardsummary__inner-container--summary")[0]
        
        offer_block = summary_container.select_one("div.cmp-cardsummary__inner-container--card-member-offer p")
        for el in offer_block.select("s, strike, .strikeThrough, [style*='line-through']"):
            el.decompose()
        welcome_offer = offer_block.get_text(" ", strip=True)
        apr = summary_container.select("div.cmp-cardsummary__inner-container--purchase-apr p")[0].get_text()
        annual_fee = summary_container.select("div.cmp-cardsummary__inner-container--annual-fee p")[0].get_text()
        
        card_soup = link2soup(url)
        reward_container_options = [
            "div.cmp-rewardsbenefits__item p",
            "div#container-43fa1cda69 h3, div#container-43fa1cda69 div.cmp-reward__element",
            "div.container.responsivegrid.aem-GridColumn.aem-GridColumn--default--12 h3:not([class]), div.aem-Grid.aem-Grid--12.aem-Grid--default--12 div.cmp-reward__element"
        ]
        rewards = []
        for div in reward_container_options:
            if rewards == []:
                rewards = card_soup.select(div)
        if rewards == []:
            print(f"FML:{name}")
    
        text_rewards = []
        for reward in rewards:
            text_rewards.append(reward.text.strip())
            
        credit_card = CreditCard("chase", name, annual_fee, welcome_offer, apr, text_rewards)
        
        cards.append(credit_card)

    return cards