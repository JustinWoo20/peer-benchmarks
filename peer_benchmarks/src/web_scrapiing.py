from bs4 import BeautifulSoup
import requests

# Fetch yfinance api page
url = 'https://ranaroussi.github.io/yfinance/reference/api/yfinance.EquityQuery.html'
response = requests.get(url)

# Parse through page
soup = BeautifulSoup(response.content, 'html.parser')

target_table = soup.find(id='id2')
target_table_body = target_table.find('tbody')
line_classes = target_table_body.find_all(class_='line')
industry_divs = line_classes[22:]
for i in industry_divs:
    text = i.get_text(strip=True)
    sector, industry = text.split(': ')
