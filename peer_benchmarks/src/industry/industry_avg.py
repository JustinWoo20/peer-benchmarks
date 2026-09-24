from datetime import date
import sqlite3 as sql
from peer_benchmarks.src.web_scraping import web_scraper
from peer_benchmarks.src.screeners.screeners import screen_by_industry
from peer_benchmarks.config import PEER_BENCHMARKS

# Get current year
current_year = date.today().year
current_month = date.today().month

# Open SQLite connection
# conn = sql.connect(PEER_BENCHMARKS / f"peer_benchmarks_{current_year}_{current_month}.db")
# cur = conn.cursor()
# # Drop tables if they exists
# cur.execute("DROP TABLE IF EXISTS industries")
# # Create new tables for most recent values
# cur.execute("""CREATE TABLE industries
#             (Industry TEXT NOT NULL,
#             Sector TEXT NOT NULL,
#             PB_Ratio REAL,
#             DE_Ratio REAL,
#             RoE REAL,
#             Revenue_Growth REAL,
#             Gross_Margin REAL,
#             TTM_PE REAL,
#             Forward_PE)""")

# Obtain sector and industry dictionary
industries_scraped = web_scraper.obtain_equity_query()

# Create dictionary with stocks from industry screening
# {Sector: {Industry: [], Industry: []}, Sector:}
screener_results = {}
for sector, industries in industries_scraped.items():
    inner_dict = {}
    for i in industries:
        stock_list = screen_by_industry(industry=i)
        if stock_list:
            inner_dict[i] = stock_list
    screener_results[sector] = inner_dict

# Calculate benchmarks
# calculate_benchmakrs(screener_results)
# Financial services industries
# calculate_f_benchmarks(industry_stock_dict=financial_services_industries)
#
# # Non-financial services industries
# calculate_nf_benchmarks(industry_stock_dict=non_financial_services_industries)

# conn.close()
