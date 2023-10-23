from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
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



def load_page(url, page_count):
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
    job_listings  = []
    print('scraping job urls...')
    for _ in range(3): #no of retries if it fails
        try:
            ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
            page_urls = WebDriverWait(driver,20, ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='my-0 p-sm-right job-tile-title']/a")))
            urls_hrefs = [url_href.get_attribute('href') for url_href in page_urls ]
            for url in urls_hrefs:
                job_listings.append(url)
                time.sleep(2)
        except StaleElementReferenceException:
            driver.refresh()
            time.sleep(10)

        else:
            break
    
    return job_listings


def next_page():
    try:
        next_page_button = driver.find_element(By.XPATH, "//button[@class='up-pagination-item up-btn up-btn-link']")
        driver.execute_script("arguments[0].click();", next_page_button)

    except NoSuchElementException:
        print('Last page reached!')
        
def save_urls(job_listings):
    print('saving job urls...')
    with open('upwork_jobs.txt', 'a') as file:
        for listing in job_listings:
            file.write(f'{listing}\n')

page_count = 1
while page_count <=5:
    url=f"https://www.upwork.com/nx/jobs/search/?sort=recency&page={page_count}"
    load_page(url, page_count)
    time.sleep(10)
    job_listings = scrape_page_urls()
    save_urls(job_listings)
    print('---------------------------------------------------------------******')
    time.sleep(10)

    try:
        page_count+=1
        next_page()
    except Exception as e:
        print('Problem encountered!')
        break




print('Exiting driver')
print(page_count)


driver.quit()
