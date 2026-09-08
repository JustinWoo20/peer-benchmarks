from datetime import date
import sqlite3 as sql
from peer_benchmarks.src.web_scraping import web_scraper
from peer_benchmarks.src.screeners.screeners import screen_by_industry
from non_financial_services.non_financial import calculate_nf_benchmarks
from peer_benchmarks.config import PEER_BENCHMARKS
import yfinance as yf

# Get current year
current_year = date.today().year

# Open SQLite connection
conn = sql.connect(PEER_BENCHMARKS / f"peer_benchmarks_{current_year}.db")

# Obtain companies in each industry in major American stock exchanges
industries_scraped = web_scraper.obtain_equity_query()
financial_services_industries = {}
non_financial_services_industries = {}

# Split between financial services and nonfinancial services
for sector, industries in industries_scraped.items():
    for i in industries:
        stock_list = screen_by_industry(industry=i)
        if sector == 'Financial Services' and stock_list is not None:
            financial_services_industries[i] = stock_list
        elif stock_list:
           non_financial_services_industries[i] = stock_list

# Non-financial services industries
calculate_nf_benchmarks(non_financial_services_industries)

conn.close()
