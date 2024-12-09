# main.py
import re
import requests
import pandas as pd
from datetime import datetime
import warnings
from data_cleaner import clean_company_url, extract_company_name

# Suppress SSL warnings
warnings.filterwarnings('ignore')


def scrape_jobs():
    jobs = []
    quick_info = []
    url = "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README.md"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Keywords for finance and business roles
    role_keywords = {
        # Sales related roles
        'sales analytics': 'Sales Analytics',
        'sales analyst': 'Sales Analyst',
        'sales consulting': 'Sales Consulting',
        'sales intelligence': 'Sales Intelligence',
        'sales insights': 'Sales Insights',
        'sales operations': 'Sales Operations',
        'sales planning': 'Sales Planning',
        'sales strategy': 'Sales Strategy',

        # Strategy related roles
        'strategy analytics': 'Strategy Analytics',
        'strategy analyst': 'Strategy Analyst',
        'strategy consulting': 'Strategy Consulting',
        'strategy intelligence': 'Strategy Intelligence',
        'strategy insights': 'Strategy Insights',
        'strategy operations': 'Strategy Operations',
        'strategy planning': 'Strategy Planning',

        # Investment related roles
        'investment analytics': 'Investment Analytics',
        'investment analyst': 'Investment Analyst',
        'investment banking': 'Investment Banking',
        'investment consulting': 'Investment Consulting',
        'investment intelligence': 'Investment Intelligence',
        'investment insights': 'Investment Insights',
        'investment operations': 'Investment Operations',
        'investment planning': 'Investment Planning',
        'investment strategy': 'Investment Strategy',

        # Business related roles
        'business analytics': 'Business Analytics',
        'business analyst': 'Business Analyst',
        'business consulting': 'Business Consulting',
        'business development': 'Business Development',
        'business intelligence': 'Business Intelligence',
        'business operations': 'Business Operations',
        'business planning': 'Business Planning',
        'business strategy': 'Business Strategy',

        # Management related roles
        'management consultant': 'Management Consultant'
    }

    # Keywords to exclude
    exclude_keywords = ['data analyst', 'data science', 'software', 'engineer', 'developer', 'IT', 'technical']

    try:
        session = requests.Session()
        session.verify = False
        response = session.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error accessing URL: Status code {response.status_code}")
            return

        content = response.text
        print("Content retrieved successfully, processing jobs...")

        # Pre-filter rows to include only relevant internship listings
        rows = [row for row in content.split('\n') if '|' in row and
                ('intern' in row.lower() or '2025' in row) and
                not any(exclude in row.lower() for exclude in exclude_keywords)]

        for row in rows:
            columns = row.split('|')
            if len(columns) >= 4:
                company = columns[1].strip()
                role = columns[2].strip().lower()
                location = columns[3].strip()

                # Extract URL from the markdown link format
                url_match = re.search(r'\[(?:[^\]]*)\]\((https?://[^\s\)]+)\)', row)
                link = url_match.group(1) if url_match else ''

                # Check for matching roles
                role_category = None
                for keyword, category in role_keywords.items():
                    if keyword in role:
                        role_category = category
                        break

                if role_category:
                    clean_company = extract_company_name(company)
                    cleaned_url = clean_company_url(link) if link else ""
                    jobs.append({
                        'title': str(columns[2].strip()),
                        'company': clean_company,
                        'location': str(location),
                        'url': cleaned_url,
                        'application_url': cleaned_url,
                        'category': role_category,
                        'date_posted': str(datetime.now().strftime('%Y-%m-%d')),
                        'source': 'SimplifyJobs'
                    })

                    quick_info.append({
                        'internship': str(columns[2].strip()),
                        'company': clean_company,
                        'location': str(location),
                        'category': role_category
                    })

                    print(f"Found job: {columns[2].strip()} at {clean_company}")

    except Exception as e:
        print(f"Error processing jobs: {str(e)}")

    if jobs:
        df_full = pd.DataFrame(jobs)
        filename_full = f'business_internships_full_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        df_full.to_csv(filename_full, index=False)

        df_quick = pd.DataFrame(quick_info)
        filename_quick = f'business_internships_summary_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        df_quick.to_csv(filename_quick, index=False)

        print(f"\nSaved {len(jobs)} jobs to {filename_full}")
        print(f"Saved summary information to {filename_quick}")
    else:
        print("\nNo jobs found")

if __name__ == "__main__":
    scrape_jobs()