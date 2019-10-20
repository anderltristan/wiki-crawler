import numpy as np 
import pandas as pd
import re

from urllib.request import urlopen
from bs4 import BeautifulSoup

def clean_data(dataset):
    # Renaming Headings
    dataset.rename(columns = {'Country(or dependent territory)': 'Country'}, inplace = True)
    dataset.rename(columns = {'% of worldpopulation': 'Percentage of World Population'}, inplace = True)
    dataset.rename(columns = {'Total Area': 'Total Area (km2)'}, inplace = True)

    # Cleaning All Cells.. Remove any () or []
    for column in dataset.columns:
        dataset[column] = dataset[column].str.replace(r"\(.*\)", "")
        dataset[column] = dataset[column].str.replace(r"\[.*\]", "")

    # Cleaning Headers
    dataset['Percentage of World Population'] = dataset['Percentage of World Population'].str.strip('%')
    dataset['Percentage Water'] = dataset['Percentage Water'].str.strip('%')
    dataset['Percentage Water'] = dataset['Percentage Water'].str.strip()
    dataset.sample(5)

    # Cleaning Area Column
    for cell in range(len(dataset['Total Area (km2)'])):
        area = dataset.iloc[cell]['Total Area (km2)']
        if('sq\xa0mi' in area):
            area = area.split('-')[0]
            area = re.sub(r'[^0-9.]+', '', area)
            area = int(float(area) * 2.58999)
        else:
            area = area.split('-')[0]
            area = re.sub(r'[^0-9].+', '', area)
            area = int(float(area))
        dataset.iloc[cell]['Total Area (km2)'] = area

    # Cleaning Water Column
    for cell in range(len(dataset['Percentage Water'])):
        num = dataset.iloc[cell]['Percentage Water']
        if(num == 'n/a' or num == 'negligible' or num == 'Negligible'):
            dataset.iloc[cell]['Percentage Water'] = '0.0'
    dataset['Percentage Water'] = dataset['Percentage Water'].str.replace(r'[^0-9.]+', '')
    dataset = dataset[dataset['Percentage Water'].astype(float) <= 100]

    # Cleaning GDP Column
    dataset['Total Nominal GDP'] = dataset['Total Nominal GDP'].str.replace('$', '')
    for x in range(len(dataset['Total Nominal GDP'])):
        gdp = dataset.iloc[x]['Total Nominal GDP']
        if ('trillion' in dataset.iloc[x]['Total Nominal GDP']):
            gdp = re.sub(r'[^0-9.]+', '', gdp)
            gdp = int(float(gdp) * 1000000000000)
        elif ('billion' in dataset.iloc[x]['Total Nominal GDP']):
            gdp = re.sub(r'[^0-9.]+', '', gdp)
            gdp = int(float(gdp) * 1000000000)
        elif ('million' in dataset.iloc[x]['Total Nominal GDP']):
            gdp = re.sub(r'[^0-9.]+', '', gdp)
            gdp = int(float(gdp) * 1000000)
        else:
            gdp = int(re.sub(r'[^0-9.]+', '', gdp))
        dataset.iloc[x]['Total Nominal GDP'] = gdp

    dataset['Per Capita GDP'] = dataset['Per Capita GDP'].str.replace(r'[^0-9.]+', '')

    # Generating final CSV with cleaned data
    dataset.to_csv("dataset_final.csv", index = False)
