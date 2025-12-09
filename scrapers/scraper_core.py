from bs4 import BeautifulSoup
import requests

def link2soup(url: str) -> BeautifulSoup:
    """
    Gets the HTML content of a webpage and parses it into a BeautifulSoup object.

    Args:
        url(string): The URL of the webpage to scrape.

    Returns:
        BeautifulSoup: A BeautifulSoup object containing the parsed HTML content.
    """
    
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')
