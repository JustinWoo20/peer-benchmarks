from datetime import date
import sqlite3 as sql
import time
from peer_benchmarks.src.web_scraping import web_scraper
from peer_benchmarks.src.screeners.screeners import screen_by_industry
from industry_calculator.calculator import calculate_benchmarks
from peer_benchmarks.config import PEER_BENCHMARKS

def calculate_industry_benchmarks():
    # Get current year
    current_year = date.today().year
    current_month = date.today().month

    # Open SQLite connection
    conn = sql.connect(PEER_BENCHMARKS / f"peer_benchmarks_{current_year}_{current_month}.db")
    cur = conn.cursor()
    # Drop tables if they exists
    cur.execute("DROP TABLE IF EXISTS industries")
    # Create new tables for most recent values
    cur.execute("""CREATE TABLE industries
                (Industry TEXT NOT NULL,
                Sector TEXT NOT NULL,
                PB_Ratio REAL,
                DE_Ratio REAL,
                RoE REAL,
                Revenue_Growth REAL,
                Gross_Margin REAL,
                TTM_PE REAL,
                Forward_PE)""")

    # Obtain sector and industry dictionary
    industries_scraped = web_scraper.obtain_equity_query()

    # Create dictionary with stocks from industry screening
    # Screener results dictionary: {Sector: {Industry: [], Industry: []}, Sector:}
    screener_results = {}
    for sector, industries in industries_scraped.items():
        inner_dict = {}
        for i in industries:
            stock_list = screen_by_industry(industry=i)
            time.sleep(2)
            if stock_list:
                inner_dict[i] = stock_list
        screener_results[sector] = inner_dict

    # Calculate benchmarks
    benchmarks = calculate_benchmarks(screener_results)

    cur.executemany("""
        INSERT INTO industries
        (Industry, Sector, PB_Ratio, DE_Ratio, RoE, Revenue_Growth, Gross_Margin, TTM_PE, Forward_PE)
        VALUES (:Industry, :Sector, :PB_Ratio, :DE_Ratio, :RoE, :Revenue_Growth, :Gross_Margin, :TTM_PE, :Forward_PE)
    """, benchmarks)

    conn.commit()

    conn.close()
