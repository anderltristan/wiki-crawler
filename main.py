import numpy as np 
import pandas as pd
import re
import data

from urllib.request import urlopen
from bs4 import BeautifulSoup

def get_HTML_content(link):
    html = urlopen(link)
    soup = BeautifulSoup(html, 'html.parser')
    return soup

content = get_HTML_content('https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population')
# The list of countries we want to scrape is in an element with class names 'wikitable' and 'sortable'
table = content.find('table', {'class': 'wikitable sortable'})
# Each row in that table is going to contain a country that we want to scrape
rows = table.find_all('tr')

for row in rows:
    cells = row.find_all('td')
    if len(cells) > 1:
        # The <a> tag in each row will have a link to that country's wiki page
        country_link = cells[1].find('a')

def get_additional_details(url):
    try:
        country_page = get_HTML_content('https://en.wikipedia.org' + url)
        # Each country has an 'infobox' on their wiki page with a list of general
        # details (size, population, flag, etc)
        table = country_page.find('table', {'class': 'infobox geography vcard'})
        # Creating empty object that will store country details
        additional_details = []
        read_content = False
        for tr in table.find_all('tr'):
            if (tr.get('class') == ['mergedtoprow'] and not read_content):
                link = tr.find('a')
                if (link and (link.get_text().strip() == 'Area' or
                   (link.get_text().strip() == 'GDP' and tr.find('span').get_text().strip() == '(nominal)'))):
                    read_content = True
                if (link and (link.get_text().strip() == 'Population')):
                    read_content = False
            elif ((tr.get('class') == ['mergedrow'] or tr.get('class') == ['mergedbottomrow']) and read_content):
                additional_details.append(tr.find('td').get_text().strip('\n')) 
                if (tr.find('div').get_text().strip() != '•\xa0Total area' and
                   tr.find('div').get_text().strip() != '•\xa0Total'):
                    read_content = False
        return additional_details
    except Exception as error:
        print('Error occured: {}'.format(error))
        return []

# Declaring an empty object that will be used to store the content scraped from the pages
data_content = []
for row in rows:
    # Content will be scraped from each <td> tag
    cells = row.find_all('td')
    if len(cells) > 1:
        # Print each country that is currently being scraped
        print(cells[1].get_text())
        country_link = cells[1].find('a')
        country_info = [cell.text.strip('\n') for cell in cells]
        additional_details = get_additional_details(country_link.get('href'))
        if (len(additional_details) == 4):
            # Only adding to object if it has the data we want
            country_info += additional_details
            data_content.append(country_info)

# Creating a data frame from scraped content using pandas
dataset = pd.DataFrame(data_content)

# Creating column headings
headers = rows[0].find_all('th')
headers = [header.get_text().strip('\n') for header in headers]
headers += ['Total Area', 'Percentage Water', 'Total Nominal GDP', 'Per Capita GDP']
dataset.columns = headers

# Dropping columns from dataset that we don't want to use
drop_columns = ['Rank', 'Date', 'Source']
dataset.drop(drop_columns, axis = 1, inplace = True)
dataset.sample(3)
dataset.to_csv("dataset.csv", index = False)

# Reading the dataset using pandas
dataset = pd.read_csv("dataset.csv")

# Renaming headings
dataset.rename(columns = {'Country(or dependent territory)': 'Country'}, inplace = True)
dataset.rename(columns = {'% of worldpopulation': 'Percentage of World Population'}, inplace = True)
dataset.rename(columns = {'Total Area': 'Total Area (km2)'}, inplace = True)

# Formatting data
data.clean_data(dataset)