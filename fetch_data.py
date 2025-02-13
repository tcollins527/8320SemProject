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

def fetch_census_data():
    # Calculate the last month's year and month
    today = datetime.now()
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    year = last_month.year
    month = last_month.strftime("%b").capitalize()

    url = f"{base_url}/{year}/cps/basic/{month}?get={','.join(vars)}&for=state:*&key=0cbe74e555fe4b3dac32591deacb7248f4dafae0"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data[1:], columns = data[0])

    df['year'] = year
    df['month'] = month

    column_order = ['HRHHID', 'HWHHWGT', 'year', 'month', 'REGION', 'STATE', 'CBSA', 'PELAYFTO', 'PELAYDUR', 'PESEX', 'PTDTRACE', 'PEEDUCA', 'PEMARITL', 'HEFAMINC', 'HRHTYPE', 'HRNUMHOU']
    df = df[column_order]

    return df

def filter_data(df):
    df = df[df['PELAYFTO'].isin(['0','1'])]
    return df

def save_data(df, year, month):
    filename = f"data/layoff_data_{year}_{month}.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# def filter_data(df):
#     df = df[df['PELAYFTO'].isin(['Yes'])]

def main():
    new_df = fetch_census_data()
    new_df = filter_data(new_df)

    # drop header to avoid remapping
    new_df = new_df.iloc[1:]

    # load existing data
    existing_df = pd.read_csv('data/layoff_data.csv')

    combined_df = pd.concat([existing_df, new_df]).drop_duplicates()


    today = datetime.now()
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    year = last_month.year
    month = last_month.strftime("%b").capitalize()
    save_data(combined_df, year, month)

if __name__ == "__main__":
    main()
