from amex_scraper import scrape_amex
from capital_one_scraper import scrape_capital_one
from chase_scraper import scrape_chase
import pickle

cards = scrape_amex()+scrape_capital_one()+scrape_chase()

with open("cards.pkl", "wb") as f:
    pickle.dump(cards, f)


"""
To Access:

import pickle

with open("cards.pkl", "rb") as f:
    objects = pickle.load(f)
"""