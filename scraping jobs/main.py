from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time


# everything related to data scraping
scraping_terms=[
    'python','data extraction', 'scripting', 'data scraping','python script','data mining',
    'web scraping','selenium','web crawler','web crawling','scrapy','beautifulsoup',
    'webdriver','appium','scripting'
]

options=Options()
options.add_argument('--incognito')
driver = webdriver.Firefox(options=options)

def job_urls():
    url = "https://www.upwork.com/nx/search/jobs"

    try:
        print('Opening url')
        driver.get(url)
        # wait for the page to load(until pagination is found)
        print('Waiting for the page to load...')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='up-card-footer pb-0 d-flex justify-space-between']")))
        
    except TimeoutException:
        print("Page took too long to load")
        driver.quit()
 
    print("page loaded successfully")


job_urls()

print('Exiting driver')
driver.quit()
