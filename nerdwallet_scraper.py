from bs4 import BeautifulSoup
import requests
from scraper_core import link2soup
import pandas as pd
import re
from tqdm import tqdm
from nerdwallet_cleaner import clean_rewards_list, clean_annual_fee

def scrape_nerdwallet(clean = False):
    main_soup = link2soup("https://www.nerdwallet.com/credit-cards")
    
    hrefs = [
        a["href"]
        for li in main_soup.select("ul#l3ListWrapper-0-0 > li.l3ListItem._3DKUn-t")
        if (a := li.find("a", href=True))
    ]

    cards = {
        "name" : [],
        "issuer" : [],
        "annual_fee" : [],
        "rewards" : []
    }
    
    for href in tqdm(hrefs):
        best_soup = link2soup(href)
        blocks = best_soup.select("div.MuiBox-root.css-1hlkqtw")
        
        for block in blocks:
            name = block.select("h3.MuiTypography-root.MuiTypography-body1.css-monr6r")[0].text
            
            table = block.select("div.MuiGrid-root.MuiGrid-container.MuiGrid-direction-xs-row.css-7zk183")
            first_row = table[0].select("div.MuiGrid-root.MuiGrid-direction-xs-row.css-43v8ft")
                
            annual_fee = None
            rewards = []
                
            for entry in first_row:
                if entry.select("div.MuiBox-root.css-dayuin")[0].text == "Annual fee":
                    annual_fee = entry.select("div.MuiBox-root.css-1ffk1vi")[0].text
        
            cards["annual_fee"].append(annual_fee)
            
            reward_block = block.select("details.MuiBox-root.css-171u67s")
            reward_block = reward_block[0].select("div.MuiBox-root.css-1wcs7fe")
            if reward_block != []:
                rewards = [
                    div.text+" "+div.find_next_sibling("span").text for div in reward_block[0].select("div.MuiBox-root")
                ]
            cards["rewards"].append(rewards)
            try:
                issuer = block.select("span.MuiTypography-root.MuiTypography-bodySmall.MuiTypography-alignCenter.css-1uw5l8w")[0].text
                issuer = re.sub(r"on | website", "", issuer).split("'")[0]
            except IndexError:
                issuer = re.split(r"[®™]", name)[0]

            name = re.sub(r"®|™", "", name)
            cards["name"].append(name)

            cards["issuer"].append(issuer)
            
    df = pd.DataFrame(cards)

    if clean:
        df["clean_annual_fee"] = df["annual_fee"].apply(clean_annual_fee)
        df["clean_rewards"] = df["rewards"].apply(clean_rewards_list)
    
    return df