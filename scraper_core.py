from bs4 import BeautifulSoup
import requests

def link2soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

class CreditCard:
    def __init__(self, name, annual_fee, rewards, issuer = None):
        self.issuer = issuer
        self.name = name
        self.annual_fee = annual_fee
        self.rewards = rewards
        
    def __repr__(self):
        return f"CreditCard(issuer = {self.issuer} \n, name = {self.name},\n annual_fee = {self.annual_fee}, \n rewards = {self.rewards})"
