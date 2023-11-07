from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import json
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
unscraped_urls_path = f"{scraping_date}/urls.txt"
scraped_urls_path = f"{scraping_date}/scraped_urls.txt"
jobs_file_path= f"{scraping_date}/jobs.json"


def read_urls_file(file_path):
    print(f'Reading urls at {file_path}')
    try:
        with open(file_path, 'r') as file:
            urls = file.readlines()
        stripped_urls = [url.strip() for url in urls]
        return stripped_urls
    except Exception as e:
        print(f"{e}. Confirm the file exists then try again!")

def write_to_urls_file(urls, file_path):
    print(f'Writing urls at {file_path}')
    if urls:
        try:
            with open(file_path, 'w') as file:
                for url in urls:
                    file.write(f"{url}\n")
        except Exception as e:
            print(f"{e}. Confirm the file exists then try again!")


def setup(scraped_urls_file, jobs_file_path):
    if not os.path.exists(scraped_urls_file):
        print("Creating a file for scraped urls...")
        with open(scraped_urls_file, 'w') as file:
            file.write('')
    else:
        print('Scraped urls file located.')
    
    if not os.path.exists(jobs_file_path):
        print('Creating JSON file for jobs...')
        with open(jobs_file_path, 'w') as file:
            json.dump([], file, indent=3)
    else:
        print('Jobs file located!')

def compare_urls(unscraped_urls, scraped_urls):
    print(f"cross checking urls at {unscraped_urls} and {scraped_urls}")
    unscraped_urls_list = read_urls_file(unscraped_urls)
    scrapped_urls_list = read_urls_file(scraped_urls) 
    urls_to_scrape = [url for url in unscraped_urls_list if url not in scrapped_urls_list]
    return urls_to_scrape


def update_scraped_urls_file(scraped_urls_path, new_urls):
    print(f'Updating urls file at {scraped_urls_path}')
    existing_urls = read_urls_file(scraped_urls_path)
    updated_urls_list = new_urls + existing_urls
    write_to_urls_file(updated_urls_list, scraped_urls_path)
    

def load_listing_details_page(urls):
    if urls:
        jobs_list = []
        scraped_urls = []
        for url in urls[:6]:
            print(f"scraping {url}...")
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
                    skills = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@data-test='Skill']")))
                    for skill in skills:
                        skills_list.append(skill.text.strip())

                filtered_skills_list = list({item for item in skills_list if item})
                job_details['expertise'] = filtered_skills_list
                job_details['scraping_date'] = scraping_date

                # add job to jobs list
                # save url to scraped_urls list
                jobs_list.append(job_details)
                scraped_urls.append(url)

            except Exception as e:
                print(e)

        update_scraped_urls_file(scraped_urls_path, scraped_urls)
        return jobs_list  
            
    else:
        print('No new urls to scrape!')
        return []

def save_jobs(jobs_list, jobs_file_path):
    print(f'Saving scraped jobs at {jobs_file_path}')
    if jobs_list:
        # print(jobs_list)
        with open(jobs_file_path, 'r') as input_file:
            existing_jobs = json.load(input_file)

        updated_jobs = jobs_list+existing_jobs

        with open(jobs_file_path, 'w') as output_file:
            json.dump(updated_jobs, output_file, indent=3)


setup(scraped_urls_path,jobs_file_path)
urls_to_scrape = compare_urls(unscraped_urls_path, scraped_urls_path)
jobs_list = load_listing_details_page(urls_to_scrape)
save_jobs(jobs_list, jobs_file_path)

driver.quit()
