import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import yaml

class JobPost:
    def __init__(self, org_name, position, experience, salary, location, profile_name, posted_time, link, skills):
        self.org_name = org_name
        self.position = position
        self.experience = experience
        self.salary = salary
        self.location = location
        self.profile_name = profile_name
        self.posted_time = posted_time
        self.link = link
        self.skills = skills

def parse_posted_time(posted_time_str):
    posted_time_str_lower = posted_time_str.lower()

    if 'just posted' in posted_time_str_lower:
        return datetime.now()
    elif 'today' in posted_time_str_lower:
        hours_ago = int(re.findall(r'\d+', posted_time_str_lower)[0])
        return datetime.now() - timedelta(hours=hours_ago)
    elif 'yesterday' in posted_time_str_lower:
        return datetime.now() - timedelta(days=1)
    elif 'day' in posted_time_str_lower:
        days_ago = int(re.findall(r'\d+', posted_time_str_lower)[0])
        return datetime.now() - timedelta(days=days_ago)
    else:
        return datetime.now()

def extract_job_details(job_response):
    job_soup = BeautifulSoup(job_response.text, 'html.parser')
    salary_tag = job_soup.find('div', class_='jobTitle_jobTitle_salary__3bSw0')
    salary = salary_tag.text.strip() if salary_tag else 'Salary not provided'

    posted_time_tag = job_soup.find('div', class_='JobDetailWidget_jobCard_features__iHE_w')
    posted_time = posted_time_tag.text.strip() if posted_time_tag else np.nan

    skill_tag = job_soup.find('ul', class_='keyskills_keySkills_items__ej9_3')
    skills = [skill.text.strip() for skill in skill_tag.find_all('li')] if skill_tag else ['Skills not provided']

    return salary, posted_time, ','.join(skills)

def extract_job_links(soup, base_url):
    req = soup.select('div h2[itemprop="name"]')
    job_links = [link.find('a')['href'] for link in req]
    job_links = [link if link.startswith('http') else base_url + link for link in job_links]
    return req, job_links

def scrape_jobs(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        orgs = soup.find_all('div', class_='jobCard_jobCard_cName__mYnow')
        orgs1 = [o.text.split(' Hiring')[0].strip() for o in orgs]

        loc = soup.find_all('div', class_='jobCard_jobCard_lists__fdnsc')
        location = [re.findall("Yrs?(.*)$", l.text)[0].replace("+4", ", ").strip() for l in loc]
        experience = [re.findall("^(.*) Yrs?", l.text)[0] for l in loc]

        vac = soup.find_all('ul', class_='jobCard_jobCard_jobDetail__jD82J')
        vacancies = [int(re.findall(r'\d+', v.text)[0]) if re.findall(r'\d+', v.text) else 1 for v in vac]

        req, job_links = extract_job_links(soup, base_url)

        job_posts = []
        for link, org, pos, exp, loc, vac in zip(job_links, orgs1, req, experience, location, vacancies):
            job_response = requests.get(link)
            if job_response.status_code == 200:
                salary, posted_time, skills = extract_job_details(job_response)
                job = JobPost(org, vac, exp, salary, loc, pos.text.strip(), posted_time, link, skills)
                job_posts.append(job)

        return job_posts
    else:
        print('Failed to retrieve the page:', url)
        return []

def scrape_multiple_pages(base_url, num_pages):
    all_jobs = []
    for page in range(1, num_pages + 1):
        url = f"{base_url}&page={page}"
        print(f"Scraping page {page}...")
        jobs = scrape_jobs(url)
        all_jobs.extend(jobs)
    return all_jobs

def remove_duplicates(jobs):
    unique_links = set()
    unique_jobs = []
    for job in jobs:
        if job.link not in unique_links:
            unique_links.add(job.link)
            unique_jobs.append(job)
    return unique_jobs

def read_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

# Read parameters from config.yaml
config = read_config()
base_url = config['base_url']
num_pages = config['num_pages']

# Scrape job postings
jobs = scrape_multiple_pages(base_url, num_pages)
unique_jobs = remove_duplicates(jobs)

if unique_jobs:
    # Process scraped data and generate DataFrame
    job_data = {
        'Company Name': [job.org_name for job in unique_jobs],
        'Positions': [job.position for job in unique_jobs],
        'Experience': [job.experience for job in unique_jobs],
        'Salary': [job.salary for job in unique_jobs],
        'Location': [job.location for job in unique_jobs],
        'Profile Name': [job.profile_name for job in unique_jobs],
        'Posted Time': [job.posted_time for job in unique_jobs],
        'Skills': [job.skills for job in unique_jobs],
        'Link': [job.link for job in unique_jobs]
    }

    jobs_df = pd.DataFrame(job_data)
    jobs_df['Posted Date'] = jobs_df['Posted Time'].apply(parse_posted_time)
    jobs_df['Days Posted'] = (datetime.now() - jobs_df['Posted Date']).dt.days
    jobs_df['Status'] = ['Hot' if days < 3 else '-' for days in jobs_df['Days Posted']]
    jobs_df['Actively Hiring'] = ['Yes' if days < 30 else 'No' for days in jobs_df['Days Posted']] # Assume actively hiring within 30 days

    jobs_df = jobs_df[['Company Name', 'Positions', 'Experience', 'Salary', 'Location', 'Profile Name',
                    'Posted Time', 'Posted Date', 'Status', 'Actively Hiring', 'Link', 'Skills']]

    # Print DataFrame
    print(jobs_df)

    # Save DataFrame to CSV
    csv_filename = "job_postings.csv"
    jobs_df.to_csv(csv_filename, index=False)
    print(f"Job postings saved to {csv_filename}")
    
else:
    print("No job postings found.")
