from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re
from tqdm import tqdm
from scraper_core import link2soup
import pandas as pd

def scrape_chase():
    BASE = "https://creditcards.chase.com"
    LINK = "https://creditcards.chase.com/all-credit-cards?CELL=6TKX"
    
    soup = link2soup(LINK)
    
    card_containers = soup.select("div.cmp-cardsummary__inner-container")
    
    cards = {
        "name" : [],
        "issuer" : [],
        "annual_fee" : [],
        "rewards" : []
    }

    
    for card in tqdm(card_containers):
        title_container = card.select("div.cmp-cardsummary__inner-container__title h2 a")[0]
        name = re.sub(r"(®|Links to product page)", "", title_container.get_text(), flags=re.I).strip()
        cards["name"].append(name)
        
        url = urljoin(BASE, title_container.get("href"))
    
        summary_container = card.select("div.cmp-cardsummary__inner-container--summary")[0]
        
        annual_fee = summary_container.select("div.cmp-cardsummary__inner-container--annual-fee p")[0].get_text()
        annual_fee = re.sub(r"†|Opens pricing and terms in new window", "", annual_fee)
        annual_fee = re.split(r"[.;]", annual_fee)[0]
        cards["annual_fee"].append(annual_fee)
        
        card_soup = link2soup(url)
        rewards = [re.sub(r"\n\n|\*", " ", r.text).strip()
                   for r in card_soup.select("div.cmp-rewardsbenefits__item p, \
                   div#container-43fa1cda69 h3, \
                   div#container-43fa1cda69 div.cmp-reward__element, \
                   div.container.responsivegrid.aem-GridColumn.aem-GridColumn--default--12 div#container-43fa1cda69 h3:not([class]), \
                   div.aem-Grid.aem-Grid--12.aem-Grid--default--12 div.cmp-reward__element, \
                   div.rewards-and-benifits--business div.cmp-rewardsbenefits__content div")]
        rewards = [re.sub(r"®|\xa0|†|opens.*","",r, flags = re.I) for r in rewards if r]
        rewards = [re.sub(r"Min\. of \(.*?\) and \d+(\.\d+)?", "", r) for r in rewards]

        prefixes_to_remove = ("after", "NEW", "This product", "The new cardmember", "LIMITED", "This credit card", "This card product")
        filtered = [s for s in rewards if not s.startswith(prefixes_to_remove)]

        #words_to_remove = ("APR")
        #filtered_again = [s for s in filtered if not any(sub in s for sub in words_to_remove)]
        
        cards["rewards"].append(filtered)

        cards["issuer"].append("Chase")

    df = pd.DataFrame(cards)
    return df