import numpy as np
import pandas as pd
import yfinance as yf

def get_yf_ticker(ticker):
    t = yf.Ticker(ticker)
    return t

def safe_transpose(df):
    # Returns a transposed dataframe or none if empty
    if df is None or df.empty:
        return None
    return df.transpose().fillna(0)

def get_market_cap(ticker):
    info = ticker.info
    market_cap = info.get('marketCap') or info.get('nonDilutedMarketCap')
    if market_cap is None:
        shares_outstanding = info.get('sharesOutstanding') or info.get('floatShares')
        current_price = info.get('currentPrice')
        if current_price is None or shares_outstanding is None:
            return 0
        market_cap = shares_outstanding * current_price
    return market_cap

def get_income_statistics(ticker):
    income_statement = safe_transpose(ticker.get_income_stmt())
    if income_statement is None:
        return 0, 0, 0

    revenue = income_statement.get('TotalRevenue')
    if revenue is None:
        return 0, 0, 0
    elif len(revenue) < 2:
        return 0, 0, 0

    recent_revenue = revenue.iloc[0]
    previous_revenue_in = revenue.iloc[1]
    if recent_revenue == 0 or previous_revenue_in == 0:
        return 0, 0, 0

    gp = income_statement.get('GrossProfit')
    if gp is None:
        return 0, 0, 0
    if gp.iloc[0] == 0:
        return 0, 0, 0
    gp = gp.iloc[0]
    return recent_revenue, previous_revenue_in, gp

def get_balance_statistics(ticker):
    balance_sheet = safe_transpose(ticker.get_balance_sheet())
    if balance_sheet is None:
        return 0, 0
    total_shareholder_equity_series = balance_sheet.get('StockholdersEquity')
    if total_shareholder_equity_series is None:
        return 0, 0
    elif total_shareholder_equity_series.iloc[0] <= 0:
        return 0, 0
    else:
        total_shareholder_equity = total_shareholder_equity_series.iloc[0]

    td = balance_sheet.get('TotalDebt')
    if td is None:
        return 0, 0
    else:
        td = td.iloc[0]

    return total_shareholder_equity, td

def pe_ratios(ticker):
    # Return market cap, net income, and forward p/e estimate
    income_statement = safe_transpose(ticker.get_income_stmt())
    if income_statement is None:
        return 0, 0, 0
    info = ticker.info

    net_income = None
    for col in ('NetIncome', 'NetIncomeCommonStockholders', 'NetIncomeToCommon'):
        if col in income_statement.columns:
            net_income = income_statement[col].iloc[0]
            break

    if net_income is None or net_income == 0:
        return 0, 0, 0

    market_cap = get_market_cap(ticker)
    ttm_pe = market_cap / net_income
    f_pe = info.get('forwardPE')
    if f_pe is None:
        f_pe = 0
    elif f_pe == 'Infinity':
        f_pe = 0

    if ttm_pe <= 0:
        return 0, 0, f_pe
    else:
        return market_cap, net_income, f_pe

def calculate_nf_benchmarks(industry_stock_dict):
    industry_values = {}
    for ind, stocks in industry_stock_dict.items():
        print(f'Now working on {ind}')

        industry_mc = 0
        industry_equity = 0
        industry_debt = 0
        industry_revenue = 0
        industry_previous_revenue = 0
        industry_gross_profit = 0
        # For P/E
        industry_pe_mc = 0
        industry_net_income = 0
        industry_forward_pe = []
        for s in stocks: # Find each respective company's market cap
            print(f'Now working on {s}')
            yf_ticker = get_yf_ticker(s)
            # Find total market cap
            mc = get_market_cap(yf_ticker)
            industry_mc += mc
            # Find most recent revenue and previous
            total_revenue, previous_revenue, gross_profit = get_income_statistics(yf_ticker)
            industry_revenue += total_revenue
            industry_previous_revenue += previous_revenue
            # Gross Profit
            industry_gross_profit += gross_profit
            # Find most recent stockholder's equity
            equity, total_debt = get_balance_statistics(yf_ticker)
            industry_equity += equity
            # Find total debt per industry
            industry_debt += total_debt
            # Trailing P/E and Forward P/E
            pe_market_cap, pe_net_income, forward_pe = pe_ratios(yf_ticker)
            industry_pe_mc += pe_market_cap
            industry_net_income += pe_net_income
            industry_forward_pe.append(forward_pe)

        # Clean forward P/E list
        forward_pe_cleaned = [x for x in industry_forward_pe if x != 0]  # Remove placeholder 0  values from Forward PE

        # Calculations
        industry_pb = industry_mc / industry_equity
        industry_de = industry_debt / industry_equity
        industry_rev_growth = (industry_revenue / industry_previous_revenue) - 1
        industry_gross_margin = industry_gross_profit / industry_revenue
        if industry_net_income == 0:
            industry_ttm_pe = 0
        else:
            industry_ttm_pe = industry_pe_mc / industry_net_income
        median_forward_pe = np.median(forward_pe_cleaned)

        # Create dictionary
        new_row = {'pb_ratio': industry_pb,
                   'de_ratio': industry_de,
                   'revenue_growth': industry_rev_growth,
                   'gross_margin': industry_gross_margin,
                   'trailingPE': industry_ttm_pe,
                   'forwardPE': median_forward_pe,}
        print(new_row)

        industry_values[ind] = new_row

    print(industry_values)
    return industry_values
