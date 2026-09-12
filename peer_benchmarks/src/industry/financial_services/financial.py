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

def get_revenue(income_statement):
    # Returns the most recent year's revenue and the previous year's
    if income_statement is None:
        return 0, 0
    revenue = income_statement.get('TotalRevenue')
    if revenue is None:
        return 0, 0
    elif len(revenue) < 2:
        return 0, 0
    recent_revenue = revenue.iloc[0]
    previous_revenue = revenue.iloc[1]
    if recent_revenue == 0 or previous_revenue == 0:
        return 0, 0
    else:
        return recent_revenue, previous_revenue

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
    revenue_growth = (revenue / previous) - 1
    return round(revenue_growth, 2)

def calculate_roe(revenue, equity):
    return round(revenue / equity, 2)

def calculate_ttm_pe(market_cap, net_income):
    if net_income == 0:
        return 0
    else:
        ttm_pe = market_cap / net_income
        return round(ttm_pe, 2)

def calculate_forward_pe(f_pe_list):
    median_pe = np.median(f_pe_list)
    return median_pe

def calculate_f_benchmarks(ind_stock_dict):
    industry_values = {}
    for ind, s in ind_stock_dict.items():
        # Running totals
        industry_market_cap = 0
        industry_shareholder_equity = 0
        industry_total_debt = 0
        industry_recent_revenue = 0
        industry_previous_revenue = 0
        industry_pe_market_cap = 0
        industry_net_income = 0
        industry_f_pe = []

        # Retrieve values from financial statements
        t = get_yf_ticker(s)
        income_s, balance_s, cash_f, stock_info = get_financial_statements(t)
        # Market cap
        com_market_cap = get_market_cap(ticker_info=stock_info)
        industry_market_cap += com_market_cap
        # Shareholder's equity for P/B and RoE
        com_shareholder_equity = get_shareholder_equity(balance_sheet=balance_s)
        industry_shareholder_equity += com_shareholder_equity
        # Total debt for debt to equity ratio
        com_total_debt = get_total_debt(balance_sheet=balance_s)
        industry_total_debt += com_total_debt
        # Revenue for revenue growth and RoE
        com_recent_rev, com_previous_revenue = get_revenue(income_statement=income_s)
        industry_recent_revenue += com_recent_rev
        industry_previous_revenue += com_previous_revenue
        # Market cap for pe calculations, net income, and forward P/E estimates
        com_pe_market_cap, com_net_income, com_f_pe = get_pe_ratios(income_statement=income_s, t_info=stock_info)
        industry_pe_market_cap += com_pe_market_cap
        industry_net_income += com_net_income
        industry_f_pe.append(com_f_pe)

        # Calculations
        industry_pb = calculate_pb(market_cap=industry_market_cap, equity=industry_shareholder_equity)
        industry_de = calculate_de(debt=industry_total_debt, equity=industry_shareholder_equity)
        industry_revenue_growth = calculate_revenue_growth(revenue=industry_recent_revenue, previous=industry_previous_revenue)
        industry_roe = calculate_roe(revenue=industry_recent_revenue, equity=industry_shareholder_equity)
        industry_ttm_pe = calculate_ttm_pe(market_cap=industry_pe_market_cap, net_income=industry_net_income)
        industry_forward_pe = calculate_forward_pe(f_pe_list=industry_f_pe)

        new_row = {'pb_ratio': industry_pb,
                   'de_ratio': industry_de,
                   'revenue_growth': industry_revenue_growth,
                   'gross_margin': industry_roe,
                   'trailingPE': industry_ttm_pe,
                   'forwardPE': industry_forward_pe,}
        print(new_row)

        industry_values[ind] = new_row

    print(industry_values)
    return industry_values
