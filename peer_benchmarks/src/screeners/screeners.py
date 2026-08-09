import yfinance as yf

# Screener for getting industries
def screen_by_industry():
    yf.EquityQuery('and')