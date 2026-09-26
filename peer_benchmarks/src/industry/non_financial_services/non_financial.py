import numpy as np
import pandas as pd
import yfinance as yf

def get_yf_ticker(ticker):
    return yf.Ticker(ticker)

def safe_transpose(df):
    # Returns a transposed dataframe or none if empty
    if df is None or df.empty:
        return None
    return df.transpose().fillna(0)

def get_financial_statements(yf_ticker):
    # Obtain the most recent financial statements for a company
    income_statement = yf_ticker.get_income_stmt()
    income_t = safe_transpose(income_statement)
    balance_sheet = yf_ticker.get_balance_sheet()
    balance_t = safe_transpose(balance_sheet)
    cash_flow = yf_ticker.get_cash_flow()
    cash_t = safe_transpose(cash_flow)
    info = yf_ticker.info
    return income_t, balance_t, cash_t, info

def get_market_cap(ticker_info):
    # Returns a company's market cap
    market_cap = ticker_info.get('marketCap') or ticker_info.get('nonDilutedMarketCap')
    if market_cap is None:
        shares_outstanding = ticker_info.get('sharesOutstanding') or ticker_info.get('floatShares')
        current_price = ticker_info.get('currentPrice')
        if current_price is None or shares_outstanding is None:
            return 0
        market_cap = shares_outstanding * current_price
    return market_cap

def get_shareholder_equity(balance_sheet):
    # Returns the most recent shareholder equity value from the balance sheet
    if balance_sheet is None:
        return 0
    total_shareholder_equity_series = balance_sheet.get('StockholdersEquity')
    if total_shareholder_equity_series is None:
        return 0
    elif total_shareholder_equity_series.iloc[0] <= 0:
        return 0
    else:
        total_shareholder_equity = total_shareholder_equity_series.iloc[0]
        return total_shareholder_equity

def get_total_debt(balance_sheet):
    # Returns the most recent total debt value from the balance sheet
    if balance_sheet is None:
        return 0
    td = balance_sheet.get('TotalDebt')
    if td is None:
        return 0
    else:
        td = td.iloc[0]
        return td

def get_revenue_and_gross_profit(income_statement):
    # Returns the most recent year's revenue and the previous year's
    if income_statement is None:
        return 0, 0, 0
    revenue = income_statement.get('TotalRevenue')
    gross_profit_series = income_statement.get('GrossProfit')
    if revenue is None or gross_profit_series is None:
        return 0, 0, 0
    elif len(revenue) < 2:
        return 0, 0, 0
    recent_revenue = revenue.iloc[0]
    previous_revenue = revenue.iloc[1]
    gross_profit = gross_profit_series.iloc[0]
    if recent_revenue == 0 or previous_revenue == 0 or gross_profit == 0:
        return 0, 0, 0
    else:
        return recent_revenue, previous_revenue, gross_profit

def get_pe_ratios(income_statement, t_info):
    # Return market cap, net income, and forward p/e estimate
    if income_statement is None:
        return 0, 0, 0

    net_income = None
    for col in ('NetIncome', 'NetIncomeCommonStockholders', 'NetIncomeToCommon'):
        if col in income_statement.columns:
            net_income = income_statement[col].iloc[0]
            break

    if net_income is None or net_income == 0:
        return 0, 0, 0

    market_cap = get_market_cap(t_info)
    ttm_pe = market_cap / net_income
    f_pe = t_info.get('forwardPE')
    if f_pe is None:
        f_pe = 0
    elif f_pe == 'Infinity':
        f_pe = 0

    if ttm_pe <= 0:
        return 0, 0, f_pe
    else:
        return market_cap, net_income, f_pe

def calculate_pb(market_cap, equity):
    return round(market_cap / equity,2)

def calculate_de(debt, equity):
    return round(debt / equity, 2)

def calculate_revenue_growth(revenue, previous):
    revenue_growth = (revenue / previous) -1
    return round(revenue_growth, 2)

def calculate_gross_margin(revenue, gross_profit):
    return round(gross_profit / revenue, 2)

def calculate_ttm_pe(market_cap, net_income):
    if net_income == 0:
        return 0
    else:
        ttm_pe = market_cap / net_income
        return round(ttm_pe, 2)

def calculate_forward_pe(f_pe_list):
    # Clean forward pe list and find the median
    forward_pe_cleaned = [x for x in f_pe_list if x != 0]
    median_pe = np.median(forward_pe_cleaned)
    return median_pe


def calculate_nf_benchmarks(industry_stock_dict):
    # Everything feeds into this function
    industry_values = {}
    for ind, stocks in industry_stock_dict.items():
        # Running totals
        print(f"Now working on {ind}")
        industry_market_cap = 0
        industry_shareholder_equity = 0
        industry_total_debt = 0
        industry_recent_revenue = 0
        industry_previous_revenue = 0
        industry_gross_profit = 0
        industry_pe_market_cap = 0
        industry_net_income = 0
        industry_f_pe = []

        for s in stocks: # Find each respective company's market cap
            print(f'Now working on {s}')
            yf_ticker = get_yf_ticker(s)
            # Get financial statements
            income_statement, balance_sheet, cash_flow, stock_info = get_financial_statements(yf_ticker=yf_ticker)
            # Find total market cap
            com_mc = get_market_cap(ticker_info=stock_info)
            industry_market_cap += com_mc
            # Find most recent stockholder's equity
            com_equity = get_shareholder_equity(balance_sheet=balance_sheet)
            industry_shareholder_equity += com_equity
            # Find total debt from balance sheet
            com_debt = get_total_debt(balance_sheet=balance_sheet)
            industry_total_debt += com_debt
            # Find most recent revenue, previous year revenue, and gross profit
            com_total_revenue, com_previous_revenue, com_gross_profit = get_revenue_and_gross_profit(income_statement=income_statement)
            industry_recent_revenue += com_total_revenue
            industry_recent_revenue += com_previous_revenue
            industry_gross_profit += com_gross_profit
            # Get data for calculating PE ratios
            new_market_cap, com_net_income, com_forward_pe = get_pe_ratios(income_statement=income_statement, t_info=stock_info)
            industry_pe_market_cap += new_market_cap
            industry_net_income += com_net_income
            industry_f_pe.append(com_forward_pe)

        # Calculations
        industry_pb = calculate_pb(market_cap=industry_market_cap, equity=industry_shareholder_equity)
        industry_de = calculate_de(debt=industry_total_debt, equity=industry_shareholder_equity)
        industry_rev_growth = calculate_revenue_growth(revenue=industry_recent_revenue, previous=industry_previous_revenue)
        industry_gross_margin = calculate_gross_margin(revenue=industry_recent_revenue, gross_profit=industry_gross_profit)
        industry_ttm_pe = calculate_ttm_pe(market_cap=industry_pe_market_cap, net_income=industry_net_income)
        industry_forward_pe = calculate_forward_pe(f_pe_list=industry_f_pe)

        # Create dictionary
        new_row = {'Industry': ind,
                   'PB_Ratio': industry_pb,
                   'DE_Ratio': industry_de,
                   'Revenue_Growth': industry_rev_growth,
                   'Gross_Margin': industry_gross_margin,
                   'TTM_PE': industry_ttm_pe,
                   'Forward_PE': industry_forward_pe,}
        print(new_row)

        industry_values[ind] = new_row

    print(industry_values)
    return industry_values
