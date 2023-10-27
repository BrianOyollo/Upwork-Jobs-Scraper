from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import re


# everything related to data scraping
scraping_terms=[
    'python','data extraction', 'scripting', 'data scraping','python script','data mining',
    'web scraping','selenium','web crawler','web crawling','scrapy','beautifulsoup',
    'webdriver','appium','scripting'
]

options=Options()
options.add_argument('--incognito')
driver = webdriver.Firefox(options=options)

def load_listing_details_page(url):
    try:
        driver.get(url)

        # wait until the 'about client' section is visible. Page should be loaded by then.
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='cfe-about-client-v2 air3-card-section py-4x']" )))

        # get job title
        job_title = driver.find_element(By.XPATH, "//header[@class='air3-card-section py-4x']/h4").text
        print(f'Title: {job_title}')
        
        # get job posting time
        job_posting_time = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-test='PostedOn']/span"))).text
        print(f'Posted: {job_posting_time}')

        # get job location
        job_location = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-test='LocationLabel']/span"))).text
        print(f'Location: {job_location}')
        
        # get job description
        job_description = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-test='Description']/p"))).text
        print(f'Description: {job_description}')

        # get job pay
        # job_budget = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH, "div[@data-test='BudgetAmount']/p"))).text
        # print(job_budget)
        
        # get job features
        job_features = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='features list-unstyled m-0']/li")))
        # for job_feature in job_features:
        #     feature = job_feature.find_element(By.TAG_NAME, "strong")
        #     description = job_feature.find_element(By.CLASS_NAME,"description")

        #     if feature:
        #         feature_text = feature.text
        #         print(feature_text)
        #     # if description:
        #     #     description_text = description.text

        #     # print(f"{description_text}:{feature_text}")

        feature_texts = [job_feature.text for job_feature in job_features]
        print(feature_texts)
        for item in feature_texts:
            if "\n" in item:
                try:
                    min, x, max, desc = item.split("\n")
                    fet = f"{min}-{max}"
                    desc = desc
                except ValueError:
                    x,y = item.split("\n")
                    fet = x
                    desc = y
            else:
                fet = item
                desc = "Location"

            print(f"{desc}: {fet}")



           

    except Exception as e:
        print(e)

url1='https://www.upwork.com/freelance-jobs/apply/Designer-for-Metfi-DAO_~012c2c3f27607d06e6/'
url2='https://www.upwork.com/freelance-jobs/apply/Chatting-pondre-aux-abonn-une-influenceuse-pour-vendre-des-dias-priv_~0165ed686bba96502e/'
url3='https://www.upwork.com/freelance-jobs/apply/Google-document-into-word_~01bce6958ccd63a9f1/'
url4='https://www.upwork.com/freelance-jobs/apply/Content-Creator-STEM_~014ce1766f6b16ebe1/'
load_listing_details_page(url4)
driver.quit()
