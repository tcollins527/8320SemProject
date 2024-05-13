import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import json

# Constants
base_url = "https://api.census.gov/data"
vars = [
    "HRHHID", "HWHHWGT", "CBSA", "PELAYFTO", "PELAYDUR", "HEFAMINC", "PESEX",
    "PTDTRACE", "PEEDUCA", "PEMARITL", "HRHTYPE", "HRNUMHOU", "REGION", "STATE"
]

# Mapping URLs
mapping_urls = {
    'state': "https://api.census.gov/data/2024/cps/basic/jan/variables/STATE.json",
    'city': "https://api.census.gov/data/2023/cps/basic/jan/variables/GTCBSA.json",
    'region': "https://api.census.gov/data/2021/cps/basic/mar/variables/GEREG.json",
    'sex': "https://api.census.gov/data/2023/cps/basic/jan/variables/PESEX.json",
    'layoff': "https://api.census.gov/data/2023/cps/basic/jan/variables/PELAYFTO.json",
    'race': "https://api.census.gov/data/2023/cps/basic/jan/variables/PTDTRACE.json",
    'educ': "https://api.census.gov/data/2023/cps/basic/jan/variables/PEEDUCA.json",
    'marstatus': "https://api.census.gov/data/2023/cps/basic/jan/variables/PEMARITL.json",
    'famincome': "https://api.census.gov/data/2023/cps/basic/jan/variables/HEFAMINC.json",
    'famtype': "https://api.census.gov/data/2024/cps/basic/jan/variables/HRHTYPE.json"
}

def fetch_mappings():
    mappings = {}
    for key, url in mapping_urls.items():
        response = requests.get(url).text
        mappings[key] = {int(k): v for k, v in json.loads(response)['values']['item'].items()}
    return mappings

def fetch_census_data():
    today = datetime.now()
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    year = last_month.year
    month = last_month.strftime("%b").lower()

    url = f"{base_url}/{year}/cps/basic/{month}?get={','.join(vars)}&for=state:*&key=0cbe74e555fe4b3dac32591deacb7248f4dafae0"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])

    return df, year, month

def save_data(df, year, month):
    filename = f"data/cps_data_{year}_{month}.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def filter_data(df):
    df = df[df['PELAYFTO'].isin(['0', '1'])].reset_index(drop=True)
    df['PELAYDUR'] = df['PELAYDUR'].astype(int)
    df = df[df['PELAYDUR'] <= 26].reset_index(drop=True)
    df = rename_columns(df)
    return df

def rename_columns(df):
    col_names = {
        'HRHHID': 'houseid',
        'HWHHWGT': 'propweight',
        'CBSA': 'city',
        'PELAYFTO': 'layoff',
        'PELAYDUR': 'layoffdur',
        'HEFAMINC': 'famincome',
        'PESEX': 'sex',
        'PTDTRACE': 'race',
        'PEEDUCA': 'educ',
        'PEMARITL': 'marstatus',
        'HRHTYPE': 'famtype',
        'HRNUMHOU': 'famnum',
        'REGION': 'region',
        'STATE': 'state'
    }
    df = df.rename(columns=col_names)
    return df

def map_data(df, mappings):
    df['state'] = df['state'].map(mappings['state'])
    df['city'] = df['city'].map(mappings['city']).str.split(',').str[0]
    df['region'] = df['region'].map(mappings['region']).str.split(' ').str[0]
    df['sex'] = df['sex'].map(mappings['sex'])
    df['layoff'] = df['layoff'].map(mappings['layoff'])
    df['race'] = df['race'].map(mappings['race'])
    df['educ'] = df['educ'].map(mappings['educ'])
    df['marstatus'] = df['marstatus'].map(mappings['marstatus'])
    df['famincome'] = df['famincome'].map(mappings['famincome'])
    df['famtype'] = df['famtype'].map(mappings['famtype'])
    return df

def append_and_save_data(new_data, mappings):
    # Load existing data
    existing_data = pd.read_csv("data/layoff_data.csv")

    # Map new data
    new_data = map_data(new_data, mappings)

    # Combine and remove duplicates
    combined_data = pd.concat([existing_data, new_data], ignore_index=True).drop_duplicates()

    # Save combined data
    combined_data.to_csv("data/layoff_dataNEW.csv", index=False)
    print("Final dataset saved to data/layoff_data.csv")

def main():
    mappings = fetch_mappings()
    new_data, year, month = fetch_census_data()
    filtered_new_data = filter_data(new_data)
    append_and_save_data(filtered_new_data, mappings)

if __name__ == "__main__":
    main()
