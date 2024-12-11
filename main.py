import re
import requests
import pandas as pd
from datetime import datetime
import warnings
from data_cleaner import clean_company_url, extract_company_name

warnings.filterwarnings('ignore')

def scrape_jobs():
    jobs = []
    quick_info = []

    # Define multiple sources
    sources = {
        'SimplifyJobs': "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README.md",
        'PittCSC': "https://raw.githubusercontent.com/pittcsc/Summer2024-Internships/dev/README.md"
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Keywords for finance and business roles
    role_keywords = {
        # Investment Banking & Capital Markets
        'investment': 'Investment Banking',
        'banking': 'Investment Banking',
        'investment banking': 'Investment Banking',
        'finance': 'Finance',
        'securities': 'Securities',
        'ib': 'Investment Banking',
        'ibd': 'Investment Banking',
        'capital markets': 'Capital Markets',
        'debt': 'Capital Markets',
        'equity': 'Capital Markets',
        'mergers': 'M&A',
        'acquisitions': 'M&A',
        'ma': 'M&A',
        'leveraged': 'Leveraged Finance',
        'syndications': 'Syndications',
        'coverage': 'Coverage',

        # Asset & Wealth Management
        'asset': 'Asset Management',
        'wealth': 'Wealth Management',
        'portfolio': 'Portfolio Management',
        'fund': 'Fund Management',
        'investment': 'Investment Management',
        'client': 'Client Management',
        'private': 'Private Wealth',
        'pwm': 'Private Wealth',

        # Research & Analysis
        'research': 'Research',
        'analyst': 'Analysis',
        'analysis': 'Analysis',
        'financial': 'Financial Analysis',
        'modeling': 'Financial Modeling',
        'valuation': 'Valuation',
        'market': 'Market Analysis',
        'industry': 'Industry Analysis',

        # Private Markets
        'private equity': 'Private Equity',
        'pe': 'Private Equity',
        'venture': 'Venture Capital',
        'vc': 'Venture Capital',
        'growth': 'Growth Equity',
        'real estate': 'Real Estate',

        # Sales & Trading
        'sales': 'Sales',
        'trading': 'Trading',
        's&t': 'Sales & Trading',
        'fixed income': 'Fixed Income',
        'equities': 'Equities',
        'commodities': 'Commodities',
        'fx': 'Foreign Exchange',
        'revenue': 'Revenue',
        'account': 'Account Management',
        'relationship': 'Relationship Management',
        'advisory': 'Advisory',
        'solutions': 'Solutions',
        'institutional': 'Institutional',
        'wholesale': 'Wholesale',
        'distribution': 'Distribution',
        'commercial': 'Commercial',

        # Corporate Functions
        'corporate': 'Corporate',
        'finance': 'Finance',
        'banking': 'Banking',
        'development': 'Development',
        'planning': 'Planning',
        'strategy': 'Strategy',
        'treasury': 'Treasury',
        'underwriting': 'Underwriting',

        # Consulting
        'consulting': 'Consulting',
        'consultant': 'Consulting',
        'advisor': 'Advisory',
        'services': 'Services',
        'deal': 'Deals',
        'transaction': 'Transactions',
        'investment': 'Investments',
        'aum': 'Asset Management',
        'coordination': 'Coordination',
        'planning': 'Planning',
        'optimization': 'Optimization',
        'excellence': 'Optimization',
        'advisory': 'Advisory',
        'management': 'Management',
        'strategy': 'Strategy',
        'transformation': 'Transformation',
        'change': 'Change Management',
        'operations': 'Operations',
        'performance': 'Performance',
        'improvement': 'Improvement',

        # Business & Strategy
        'business': 'Business',
        'strategic': 'Strategy',
        'analyst': 'Analysis',
        'process': 'Process',
        'project': 'Project',
        'program': 'Program',
        'operations': 'Operations'
    }

    # Keywords to exclude
    exclude_keywords = [
        'data analyst',
        'data science',
        'data scientist',
        'ai',
        'mobile',
        'research',
        'robot',
        'technology',
        'scientist',
        'programmer',
        'development',
        'trading',
        'data',
        'software',
        'engineer',
        'developer',
        'IT',
        'technical',
        'machine learning',
        'artificial intelligence',
        'devops',
        'frontend',
        'backend',
        'full stack',
        'quant',
        'quantitative',
        'derivatives',
        'algorithmic',
        'statistical',
        'mathematical'
    ]

    # Process each source
    for source_name, url in sources.items():
        try:
            session = requests.Session()
            session.verify = False
            response = session.get(url, headers=headers)

            if response.status_code != 200:
                print(f"Error accessing {source_name}: Status code {response.status_code}")
                continue

            content = response.text
            print(f"Processing jobs from {source_name}...")

            # Modified row processing to handle different formats
            rows = [row for row in content.split('\n') if '|' in row and
                    ('intern' in row.lower() or '2024' in row or '2025' in row) and
                    not any(exclude in row.lower() for exclude in exclude_keywords)]

            for row in rows:
                columns = row.split('|')
                if len(columns) >= 4:
                    company = columns[1].strip()
                    role = columns[2].strip().lower()
                    location = columns[3].strip()
                    url_match = re.search(r'\[(?:[^\]]*)\]\((https?://[^\s\)]+)\)', row)
                    link = url_match.group(1) if url_match else ''

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
                            'source': source_name
                        })

                        quick_info.append({
                            'internship': str(columns[2].strip()),
                            'company': clean_company,
                            'location': str(location),
                            'category': role_category
                        })

                        print(f"Found job: {columns[2].strip()} at {clean_company} from {source_name}")

        except Exception as e:
            print(f"Error processing {source_name}: {str(e)}")

    # Save results
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
