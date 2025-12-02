from bs4 import BeautifulSoup
import requests

def link2soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')
