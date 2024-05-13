import os
import requests
import pandas as pd
from datetime import datetime, timedelta

api_key = "0cbe74e555fe4b3dac32591deacb7248f4dafae0"
base_url = "https://api.census.gov/data"

# Define variables of interest 2010-2023
variables = [
    "HRHHID",      # Household Identifier
    "HWHHWGT",     # Household weight for surveyed individuals
    "GTCBSA",      # Metropolitan Core Based Statistical Area FIPS Code
    "PELAYFTO",    # Labor Force-(layoff) from full-time job
    "PELAYDUR",    # Labor Force-(layoff) # weeks looking for job
    "HEFAMINC",    # Household-total family income
    "PESEX",       # Demographics-sex
    "PTDTRACE",    # Demographics-race
    "PEEDUCA",     # Demographics-highest level of school completed
    "PEMARITL",    # Demographics-marital status
    "HRHTYPE",     # Household-type of family/single individual
    "HRNUMHOU",    # Household-total # of members
    "GEREG",       # REGION
    "GESTFIPS"     # FIPS STATE Code
]

# Define year range (2010-2024)
years = range(2010, 2024)

# Define months
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

# Query data 2010-2023
for year in years:
    for month in months:
        # Construct the API request URL for each year in year range, month in month range
        url = f"{base_url}/{year}/cps/basic/{month}?get={','.join(variables)}&for=state:*&key={api_key}"

        # Query data from Census API
        response = requests.get(url)

        # Confirm that the query was successful
        if response.status_code == 200:
            # Convert response to DataFrame
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            df.to_csv(f"/content/drive/MyDrive/UnsortedCPSdata/cps_data_{year}_{month}.csv")
            print(f"Data for {year}, {month} fetched")
        else:
            print(f"Failed to retrieve data for {year}, {month}: {response.status_code}")
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
    df = fetch_census_data(api_key)
    today = datetime.now()
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    year = last_month.year
    month = last_month.strftime("%m")
    save_data(df, year, month)

if __name__ == "__main__":
    main()
