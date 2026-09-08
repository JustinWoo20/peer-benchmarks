import yfinance as yf
import pandas as pd
from yfinance import ticker
from peer_benchmarks.src.screeners.screeners import screen_by_industry
import random

screener_results = screen_by_industry('Asset Management')
stock_picks = random.sample(screener_results, 3)
print(stock_picks)

def get_yf_ticker(ticker):
    return yf.Ticker(ticker)

def safe_transpose(df):
    # Returns a transposed dataframe or none if empty
    if df is None or df.empty:
        return None
    return df.transpose().fillna(0)

def get_statistics(ticker):
    income_statement = ticker.get_income_stmt(ticker)
    income_t = safe_transpose(income_statement)
    balance_sheet = ticker.get_balance_sheet(ticker)
    balance_t = safe_transpose(balance_sheet)
    cash_flow = ticker.get_cash_flow(ticker)
    cash_t = safe_transpose(cash_flow)
    info = ticker.info

for s in stock_picks:
    t = get_yf_ticker(s)
