from bs4 import BeautifulSoup
import requests
from scrapers.scraper_core import link2soup
import pandas as pd
import re
from tqdm import tqdm
from cleaners.nerdwallet_cleaner import clean_rewards_list, clean_annual_fee
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

score_conversion = {
    "Rebuilding": "Poor",
    "Fair": "Fair",
    "Excellent": "Excellent",
    "Poor": "Poor",
    "Good - Excellent": "Very Good",
    "Poor - Fair": "Poor"
}


def scrape_nerdwallet(clean: bool = False, discluded_providers: list = [], score: bool = False)-> pd.DataFrame:
    """
    Gets credit card data from NerdWallet.

    Args:
        clean(bool): Whether to clean the data after scraping. Defaults to False.
        discluded_providers(list): A list of card issuers to exclude from the results. Defaults to [].
        score(bool): Whether to include credit score information. Defaults to False.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped credit card data.
    """

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

    if score:
        cards["score"] = []
    
    for href in tqdm(hrefs):
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(href)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiGrid-root.MuiGrid-container.MuiGrid-direction-xs-row.css-1a97p8s div.MuiBox-root.css-79elbk"))
        )
        html = driver.page_source
        
        best_soup = BeautifulSoup(html, "html.parser")
        blocks = best_soup.select("div.MuiBox-root.css-1hlkqtw")
        
        for block in blocks:
            name = block.select("h3.MuiTypography-root.MuiTypography-body1.css-monr6r")[0].text
            credit_score = 0
            try:
                issuer = block.select("span.MuiTypography-root.MuiTypography-bodySmall.MuiTypography-alignCenter.css-1uw5l8w")[0].text
                issuer = re.sub(r"on | website", "", issuer).split("'")[0]
            except IndexError:
                issuer = re.split(r"[®™]", name)[0]

            name = re.sub(r"®|™", "", name)

            if any(issuer.lower() in s for s in discluded_providers):
                continue
            
            table = block.select("div.MuiGrid-root.MuiGrid-container.MuiGrid-direction-xs-row.css-7zk183")
            first_row = table[0].select("div.MuiGrid-root.MuiGrid-direction-xs-row.css-43v8ft")
                
            annual_fee = None
            rewards = []
                
            for entry in first_row:
                if entry.select("div.MuiBox-root.css-dayuin")[0].text == "Annual fee":
                    annual_fee = entry.select("div.MuiBox-root.css-1ffk1vi")[0].text
                if "Recommended credit" in entry.select("div.MuiBox-root.css-dayuin")[0].text:
                    credit_score = 1

            rows = table[0].select("div.MuiGrid-root.MuiGrid-container.MuiGrid-direction-xs-row.css-1a97p8s")
            for row in rows:
                if "Recommended credit" in row.select("div.MuiBox-root.css-dayuin")[0].text:            
                    credit_score_raw = row.text
                    for k in score_conversion:
                        if k in credit_score_raw:
                            credit_score = score_conversion[k]
                
                
        
            cards["annual_fee"].append(annual_fee)
            
            reward_block = block.select("details.MuiBox-root.css-171u67s")
            reward_block = reward_block[0].select("div.MuiBox-root.css-1wcs7fe")
            if reward_block != []:
                rewards = [
                    div.text+" "+div.find_next_sibling("span").text for div in reward_block[0].select("div.MuiBox-root")
                ]
            if score:
                cards["score"].append(credit_score)     
            
            cards["rewards"].append(rewards)
            
            cards["name"].append(name)

            cards["issuer"].append(issuer)
            
    df = pd.DataFrame(cards)

    if clean:
        df["clean_annual_fee"] = df["annual_fee"].apply(clean_annual_fee)
        df["clean_rewards"] = df["rewards"].apply(clean_rewards_list)
    
    return df