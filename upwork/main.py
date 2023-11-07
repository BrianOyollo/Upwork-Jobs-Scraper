from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os


# everything related to data scraping
# scraping_terms=[
#     'python','data extraction', 'scripting', 'data scraping','python script','data mining',
#     'web scraping','selenium','web crawler','web crawling','scrapy','beautifulsoup',
#     'webdriver','appium','scripting'
# ]

options=Options()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

scraping_date = f'{datetime.today().strftime("%Y-%m-%d")}'
url_path = f"{scraping_date}/urls.txt"
existing_urls = []
todays_urls = []


def days_setup():
    """
    Set up the environment for data scraping.

    This function checks if today's folder and the URLs text file exist. If they do not exist, it creates them.
    If the URLs text file exists, it leaves it unchanged.

    :return: None
    """
    # check if today's folder and urls file exists else create them.
    if not os.path.exists(scraping_date):
        print(f"Creating today's folder...")
        os.mkdir(scraping_date)
    else:
        print("Today's folder located")

    # check if the day's urls.txt file exists
    if not os.path.exists(url_path):
        print(f"Creating today's urls text file...")
        with open(url_path, 'w') as file:
            file.write('')
    else:
        print(f"Today's urls text file found")


def read_existing_urls():
    """
    Read existing URLs from the URLs text file.

    This function reads the existing URLs from the URLs text file and populates the `existing_urls` list.

    :return: None
    """
    print('Reading existing urls...')
    with open(url_path, 'r') as file:
        urls = file.readlines()
    
    for url in urls:
        existing_urls.append(url.strip())


def load_page(url, page_count):
    """
    Open a web page and wait for it to load.

    This function opens a web page specified by the `url` and waits for the page to load by looking for a specific element on the page.
    If the page doesn't load within the specified time, it quits the web driver.

    :param url: The URL of the web page to load.
    :param page_count: The page count or index for tracking the progress.
    :return: None
    """
    try:
        print(f'Opening page {page_count}')
        driver.get(url)
        # wait for the page to load(until pagination is found)
        print('Waiting for the page to load...')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='up-card-footer pb-0 d-flex justify-space-between']")))

    except TimeoutException:
        print("Page took too long to load")
        driver.quit()
 
    
def scrape_page_urls():
    """
    Scrape URLs from the current web page.

    This function scrapes URLs from the current web page using Selenium and returns a list of URLs found.

    :return: A list of URLs scraped from the page.
    """
    print('scraping page urls...')
    # for _ in range(3): # no of retries if it fails
    try:
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
        page_urls = WebDriverWait(driver,20, ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='my-0 p-sm-right job-tile-title']/a")))
        page_urls = [url_href.get_attribute('href') for url_href in page_urls ]
        return page_urls

    except StaleElementReferenceException:
        driver.refresh()
        time.sleep(10)
    return []

def next_page():
    """
    Navigate to the next page if available.

    This function attempts to navigate to the next page by clicking on the next page button on the current web page. If the next page button is not found, it prints a message indicating that the last page has been reached.

    :return: None
    """
    try:
        next_page_button = driver.find_element(By.XPATH, "//button[@class='up-pagination-item up-btn up-btn-link']")
        driver.execute_script("arguments[0].click();", next_page_button)
    except NoSuchElementException:
        print('Last page reached!')


def cross_check_urls(page_urls):
    """
    Cross-check and filter URLs for duplicates.

    This function cross-checks the URLs in `page_urls` with the existing URLs in `existing_urls`.
    If any URL from `page_urls` already exists in `existing_urls`, it returns `True` to indicate that all new URLs have been scraped.
    Otherwise, it appends the new URLs to `todays_urls` and returns `False`.

    :param page_urls: A list of URLs to be cross-checked.
    :return: `True` if all new URLs have been scraped, `False` otherwise.
    """
    print('Cross checking urls for duplicates...')
    for url in page_urls:
        if url in existing_urls:
            print("All new urls scraped. Saving new urls...")
            return True
        else:
            todays_urls.append(url.strip())
    return False

def save_days_urls(updated_urls_list):
    """
    Save a list of URLs to the URLs text file.

    This function takes a list of URLs in `updated_urls_list` and writes them to the URLs text file specified by `url_path`.

    :param updated_urls_list: A list of URLs to be saved to the file.
    :return: None
    """
    with open(url_path, 'w') as file:
        for url in updated_urls_list:
            file.write(f"{url}\n")


# def save_for_further_scraping(urls):
#     with open(url_path, 'w') as file:
#         for url in updated_urls_list:
#             file.write(f"{url}\n")


days_setup()
read_existing_urls()
page_count = 1
while page_count <=2:
    url=f"https://www.upwork.com/nx/jobs/search/?sort=recency&page={page_count}&per_page=50"
    load_page(url, page_count)
    time.sleep(10)
    page_urls = scrape_page_urls()
    if cross_check_urls(page_urls):
        break

    time.sleep(10)
    page_count+=1
    next_page()
    
print('Exiting driver')
driver.quit()

filtered_todays_urls = []
for url in todays_urls:
    if url not in filtered_todays_urls:
        filtered_todays_urls.append(url)

updated_urls_list = filtered_todays_urls+existing_urls

save_days_urls(updated_urls_list)
