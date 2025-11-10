from bs4 import BeautifulSoup
import requests

def link2soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

class CreditCard:
    def __init__(self, issuer = None, name, annual_fee, welcome_amount, apr, rewards):
        self.issuer = issuer
        self.name = name
        self.annual_fee = annual_fee
        self.welcome_amount = welcome_amount
        self.apr = apr
        self.rewards = rewards
        
    def __repr__(self):
        return f"CreditCard(issue = {self.issuer} \n, name = {self.name},\n annual_fee = {self.annual_fee},\n welcome_amount = {self.welcome_amount},\n apr = {self.apr},\n rewards = {self.rewards})"