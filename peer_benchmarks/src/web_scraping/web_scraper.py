from bs4 import BeautifulSoup
import requests

# Fetch yfinance api page

def obtain_key_identifiers():
    """Obtains the sector and industry keys for yf Sector/Industry class"""
    url_key = 'https://ranaroussi.github.io/yfinance/reference/api/yfinance.Sector.html'
    response = requests.get(url_key)
    soup = BeautifulSoup(response.content, 'html.parser')
    industry_key_list = []
    sector_key_list = []
    target_table = soup.find(id='id1')
    target_table_body = target_table.find_all('td')
    for t in target_table_body:
        if t.find('ul'):
            new_text = t.text
            new_text = new_text.split('\n')
            cleaned_text = [x for x in new_text if x != '']
            industry_key_list.append(cleaned_text)

        else:
            sector_text = t.text
            sector_key_list.append(sector_text)

    sect_ind_dict = dict(zip(sector_key_list, industry_key_list))
    return sect_ind_dict

def obtain_equity_query():
    """Obtains the sector and industry keys for yf Equity class"""
    url_equity_query = 'https://ranaroussi.github.io/yfinance/reference/api/yfinance.EquityQuery.html'
    response = requests.get(url_equity_query)
    soup = BeautifulSoup(response.content, 'html.parser')
    industry_data = {}
    financial_services_data = {}
    non_financial_services_data = {}
    table = soup.find(id='id2')
    odd_rows = table.find_all(class_='row-odd')
    for row in odd_rows:
        key = row.find('td')
        if key and key.get_text(strip=True) == 'industry':
            industries = row.find_all('div', class_='line')
            break

    for industry in industries:
        text = industry.get_text(strip=True)
        sector, industry = text.split(':', 1)
        industry_data[sector] = [x.strip() for x in industry.split(',')]

    for sector, industries in industry_data.items():
        if sector == 'Financial Services':
            financial_services_data[sector] = industries
        else:
            non_financial_services_data[sector] = industries

    return financial_services_data, non_financial_services_data
