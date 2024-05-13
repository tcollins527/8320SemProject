import os
import requests
import pandas as pd
from datetime import datetime, timedelta

base_url = "https://api.census.gov/data"

vars = [
    "HRHHID",       # Household Identifier
    "HWHHWGT",      # Household weight for surveyed individuals
    "CBSA",         # Metropolitan Core Based Statistical Area FIPS Code
    "PELAYFTO",     # Labor Force-(layoff) from full-time job
    "PELAYDUR",     # Labor Force-(layoff) # weeks looking for job
    "HEFAMINC",     # Household-total family income
    "PESEX",        # Demographics-sex
    "PTDTRACE",     # Demographics-race
    "PEEDUCA",      # Demographics-highest level of school completed
    "PEMARITL",     # Demographics-marital status
    "HRHTYPE",      # Household-type of family/single individual
    "HRNUMHOU",     # Household-total # of members
    "REGION",       # REGION
    "STATE"         # FIPS STATE Code
    ]

def fetch_census_data(api_key):
    # Calculate the last month's year and month
    today = datetime.now()
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    year = last_month.year
    month = last_month.strftime("%m")

    url = f"{base_url}/{year}/cps/basic/{month}?get={','.join(vars)}&for=state:*&key={api_key}"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    df = pd.Dataframe(data[1:], columns = data[0])

    return df

def save_data(df, year, month):
    filename = f"data/cps_data_{year}_{month}.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        raise ValueError("API Key is not set in the environment variables.")
    
    df = fetch_census_data(api_key)
    today = datetime.now()
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    year = last_month.year
    month = last_month.strftime("%m")
    save_data(df, year, month)

if __name__ == "__main__":
    main()