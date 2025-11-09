from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import re
from scraper_core import CreditCard
from tqdm import tqdm

def scrape_amex():
    url = "https://www.americanexpress.com/us/credit-cards/?category=all&intlink=US-Axp-Shop-Consumer-VAC-Prospect-all-StickyFilter"
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    card_containers = driver.find_elements(
        By.CSS_SELECTOR,
        "div._mobileCardTileContainer_3f2e2_231"
    )
    
    card_containers = card_containers[0:-1]
    
    wait = WebDriverWait(driver, 10)
    
    results = []
    
    for card in tqdm(card_containers):
        name_el = card.find_element(
            By.CSS_SELECTOR,
            "h3.heading-4.dls-bright-blue p.margin-1-r"
        )
        name = name_el.text.strip()
    
        show_btn = card.find_element(By.CSS_SELECTOR, "button")
        driver.execute_script("arguments[0].click();", show_btn)
    
        reward_li_els = card.find_elements(By.CSS_SELECTOR, "li._cardTileExpandedBenefitsItem_3f2e2_130.flex.flex-row b")
        benefits = [li.text.strip() for li in reward_li_els]
    
        annual_fee_p_els = card.find_elements(By.CSS_SELECTOR, "p.hidden-md-up.dls-gray-06.body-3")
        annual_fee = re.sub("Annual Fee:", "", annual_fee_p_els[0].text).strip()
        welcome_amount_html = ["div._offerThemeTier1_8ve09_1 h3",
            "div._offerThemeTier2_8ve09_1 span.sc_paddingBottom_0.sc_color_gray-06.sc_margin_0.sc_textHeading_8.sc_textBody_2.sc_paddingRight_5",
            "div._offerThemeTier3_8ve09_4 span.sc_paddingBottom_0.sc_color_gray-06.sc_margin_0.sc_textHeading_8.sc_textBody_2.sc_paddingRight_5",
            "div._offerThemeTier1_8ve09_1 span.sc_paddingBottom_0.sc_color_gray-06.sc_margin_0.sc_textHeading_8.sc_textBody_2.sc_paddingRight_5"]
        welcome_amount_el = []
        for html in welcome_amount_html:
            w = card.find_elements(By.CSS_SELECTOR, html)
            if w != []:
                welcome_amount_el = w
        
        welcome_amount = welcome_amount_el[0].text.strip()
        welcome_amount =  re.sub(r"\s+", " ", welcome_amount).strip()
        
        link = card.find_element(By.CSS_SELECTOR, "a[aria-label='Rates and Fees']").get_attribute("href")
        driver2 = webdriver.Chrome(options=options)
        driver2.get(link)
    
        apr = "19.74% to 28.74%"
    
        cc = CreditCard(name, annual_fee, welcome_amount, apr, benefits)
    
        results.append(cc)
        
    
        hide_btn = card.find_element(By.CSS_SELECTOR, "button")
        driver.execute_script("arguments[0].click();", hide_btn)
    return results
