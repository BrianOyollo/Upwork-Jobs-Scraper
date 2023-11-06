from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import re
import json


# everything related to data scraping
# scraping_terms=[
#     'python','data extraction', 'scripting', 'data scraping','python script','data mining',
#     'web scraping','selenium','web crawler','web crawling','scrapy','beautifulsoup',
#     'webdriver','appium','scripting'
# ]

options=Options()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

def load_listing_details_page(url):
    job_details = {}
    try:
        driver.get(url)
        job_details['url']=url
        time.sleep(20)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
       
        # title
        job_title = soup.find('h4',class_='m-0').text
        # print(f"Title: {job_title}")
        job_details['title']=job_title

        # time_posted
        # time_posted = soup.find(attrs={"data-test":"UpCRelativeTime"}).text
        # print(f"Time posted: {time_posted}")

        # hiring_location
        job_location = soup.find(attrs={"data-test": "LocationLabel"}).text.strip()
        # print(f"Hiring: {job_location}")
        job_details['location']=job_location

        # job_description
        job_description = soup.find(class_="break mt-2", attrs={"data-test":"Description"}).text
        # print(job_description)
        job_details['description']=job_description
        

        # job_features
        job_features = []
        job_features_ul = soup.find(class_="features list-unstyled m-0")
        for feature_li in job_features_ul:
            item = feature_li.get_text(strip=True)
            job_features.append(item)
            
        filtered_list = [item for item in job_features if item]
        features_keys = ['Fixed-price', 'Experience Level', 'Project Type', 'Duration', 'Hourly']
        final_job_features = []
        for feature in filtered_list:
            for key in features_keys:
                if key in feature:
                    feature = feature.replace(key,"")
            final_job_features.append(feature)


        # print(final_job_features)
        job_details['features']=final_job_features


       # job expertise
        more_expertise_button = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='air3-badge badge air3-popper-trigger']")))
        skills_list = []
        for button in more_expertise_button:   
            driver.execute_script("arguments[0].click();", button)
            time.sleep(5)
            skills = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@data-test='Skill']")))
            for skill in skills:
                skills_list.append(skill.text.strip())

        filtered_skills_list = list({item for item in skills_list if item})
        job_details['expertise'] = filtered_skills_list

        with open('jobs.json', 'w') as file:
            json.dump(job_details, file, indent=4)
       
    except Exception as e:
        print(e)

load_listing_details_page("https://www.upwork.com/freelance-jobs/apply/Help-withdraw-crypto_~01fb51407d19c45ae6/")
driver.quit()
