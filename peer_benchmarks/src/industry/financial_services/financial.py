import numpy as np
import pandas as pd
import yfinance as yf

def get_yf_ticker(stock_symbol):
    return yf.Ticker(stock_symbol)

def safe_transpose(df):
    # Returns a transposed dataframe or none if empty
    if df is None or df.empty:
        return None
    return df.transpose()

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

# ------------------------------------Retrieve values from financial statements-----------------------------------------
def get_market_cap(ticker_info):
    # Returns a company's market cap
    market_cap = ticker_info.get('marketCap') or ticker_info.get('nonDilutedMarketCap')
    if market_cap is None:
        shares_outstanding = ticker_info.get('sharesOutstanding') or ticker_info.get('floatShares')
        current_price = ticker_info.get('currentPrice')
        if current_price is None or shares_outstanding is None:
            return None
        market_cap = shares_outstanding * current_price
    return market_cap

def get_equity(balance_sheet):
    # Obtain shareholder equity, returns none if not available
    if balance_sheet is None:
        return None
    if 'StockholdersEquity' in balance_sheet.columns:
        shareholder_equity_series = balance_sheet.get('StockholdersEquity')
    elif 'ShareholdersEquity' in balance_sheet.columns:
        shareholder_equity_series = balance_sheet.get('ShareholdersEquity')
    else:
        return None

    shareholder_equity = shareholder_equity_series.iloc[0]
    if shareholder_equity < 0:
        return None

    return shareholder_equity

def get_total_debt(balance_sheet):
    # Retrieves total debt from a company's balance sheet and returns None if not available
    if balance_sheet is None:
        return None
    if 'TotalDebt' in balance_sheet.columns:
        total_debt_series = balance_sheet.get('TotalDebt')
    else:
        return None
    total_debt = total_debt_series.iloc[0]
    return total_debt

def get_revenue(income_statement):
    # Retrieves most recent year's revenue and previous year's
    if income_statement is None:
        return None
    if 'TotalRevenue' in income_statement.columns:
        revenue_series = income_statement.get('TotalRevenue')
    elif 'Revenue' in income_statement.columns:
        revenue_series = income_statement.get('Revenue')
    else:
        return None

    if len(revenue_series) < 2:
        return None

    recent_revenue = revenue_series.iloc[0]
    previous_revenue = revenue_series.iloc[1]
    return recent_revenue, previous_revenue

def get_gross_profit(income_statement):
    if income_statement is None:
        return None
    if 'GrossProfit' in income_statement.columns:
        gross_profit_series = income_statement.get('GrossProfit')
    else:
        return None

    gross_profit = gross_profit_series.iloc[0]
    return gross_profit

def get_net_income(income_statement):
    if income_statement is None:
        return None
    if 'NetIncome' in income_statement.columns:
        net_income_series = income_statement.get('NetIncome')
    elif 'NetIncomeCommonStockholders' in income_statement.columns:
        net_income_series = income_statement.get('NetIncomeCommonStockholders')
    elif 'NetIncomeToCommon' in income_statement.columns:
        net_income_series = income_statement.get('NetIncomeToCommon')
    else:
        return None

    net_income = net_income_series.iloc[0]
    return net_income

#----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------Match metrics to ensure accurate computation----------------------------
def get_pb_ratio_inputs(balance_sheet, ticker_info):
    # industry market cap / industry equity
    com_market_cap = get_market_cap(ticker_info)
    com_equity = get_equity(balance_sheet)

    if com_market_cap is None or com_equity is None:
        return None
    pairs = (com_market_cap, com_equity)
    return pairs

def calculate_pb_ratio(mc_equity_pairs):
    # industry market cap / industry equity
    industry_mc_sum = sum(mc for mc, _ in mc_equity_pairs)
    industry_equity_sum = sum(equity for _, equity in mc_equity_pairs)

    return round(industry_mc_sum / industry_equity_sum, 2)

def get_de_ratio_inputs(balance_sheet,):
    # Industry total debt / industry equity
    com_debt = get_total_debt(balance_sheet=balance_sheet)
    com_equity = get_equity(balance_sheet=balance_sheet)
    pairs = (com_debt, com_equity)
    return pairs

def calculate_de_ratio(debt_equity_pairs):
    # industry total debt / industry equity
    industry_debt_sum = sum(debt for debt, _ in debt_equity_pairs)
    industry_equity = sum(equity for _, equity in debt_equity_pairs)
    return round(industry_debt_sum / industry_equity, 2)

def get_rev_growth_inputs(income_statement):
    # Recent / Previous - 1
    revenue, previous = get_revenue(income_statement)
    pairs = (revenue, previous)
    return pairs

def calculate_rev_growth(revenue_pairs):
    current_total_revenue = sum(current_r for current_r, _ in revenue_pairs)
    previous_revenue_sum = sum(previous for _, previous in revenue_pairs)
    return round(current_total_revenue / previous_revenue_sum - 1, 2)

def get_gross_margin_inputs(income_statement):
    # Industry gross profit / industry revenue
    revenue, previous = get_revenue(income_statement=income_statement)
    com_gross_profit = get_gross_profit(income_statement=income_statement)
    pairs = (com_gross_profit, revenue)
    return pairs

def calculate_gross_margin(revenue_margin_pairs):
    gross_profit_sum = sum(gp for gp, _ in revenue_margin_pairs)
    revenue_sum = sum(revenue for _, revenue in revenue_margin_pairs)

    return round(gross_profit_sum / revenue_sum, 2)


def get_roe_inputs(income_statement, balance_sheet):
    # Industry net income / industry equity
    com_net_income = get_net_income(income_statement=income_statement)
    com_equity = get_equity(balance_sheet=balance_sheet)
    pairs = (com_net_income, com_equity)
    return pairs

def calculate_roe(roe_pairs):
    # Industry net income / industry equity
    net_income_sum = sum(ni for ni, _ in roe_pairs)
    equity_sum = sum(equity for equity, _ in roe_pairs)

    return round(net_income_sum / equity_sum, 2)

def get_ttm_pe_inputs(ticker_info, income_statement):
    # market_cap / net_income
    com_market_cap = get_market_cap(ticker_info=ticker_info)
    com_net_income = get_net_income(income_statement=income_statement)
    pairs = (com_market_cap, com_net_income)
    return pairs

def calculate_ttm_pe(mc_ni_pairs):
    # industry market cap / industry net income
    industry_market_cap = sum(mc for mc, _ in mc_ni_pairs)
    industry_net_income = sum(ni for _, ni in mc_ni_pairs)
    return round(industry_market_cap / industry_net_income, 2)

def get_forward_pe(ticker_info):
    f_pe_list = []
    if ticker_info is None:
        return None
    f_pe = ticker_info.get('forwardPE')
    if f_pe is None:
        return None
    elif f_pe == 'Infinity':
        return None
    f_pe_list.append(f_pe)
    return f_pe_list

def calculate_forward_pe(industry_pe_list):
    # Take median of forward PE list
    forward_pe_cleaned = [x for x in industry_pe_list if x]
    median_forward_pe = np.median(forward_pe_cleaned)
    return median_forward_pe

#---------------------------------------------------------------------------------------------------------------------

# -------------------------------Calculate benchmarks function--------------------------------------------------------
# This is the main function that will be called when calculating industry averages

def calculate_benchmarks(sect_ind_stock_dict):
    industry_values = {}
    for sector, industries in sect_ind_stock_dict.items():
        for ind, stock_list in industries.items():
            # Blank list for storing inputs
            pb_list = []
            de_list = []
            revenue_growth_list = []
            gross_margin_list = []
            roe_list = []
            ttm_pe_list = []
            forward_pe_list = []
            for stock in stock_list:
                yf_ticker = get_yf_ticker(stock)
                income, balance, cash, stock_info = get_financial_statements(yf_ticker=yf_ticker)
                # Append each tuple to a list
                pb_ratio_inputs = get_pb_ratio_inputs(balance_sheet=balance, ticker_info=stock_info)
                pb_list.append(pb_ratio_inputs)
                de_ratio_inputs = get_de_ratio_inputs(balance_sheet=balance)
                de_list.append(de_ratio_inputs)
                revenue_growth_inputs = get_rev_growth_inputs(income_statement=income)
                revenue_growth_list.append(revenue_growth_inputs)
                gross_margin_inputs = get_gross_margin_inputs(income_statement=income)
                gross_margin_list.append(gross_margin_inputs)
                roe_inputs = get_roe_inputs(income_statement=income, balance_sheet=balance)
                roe_list.append(roe_inputs)
                ttm_pe_inputs = get_ttm_pe_inputs(ticker_info=stock_info, income_statement=income)
                ttm_pe_list.append(ttm_pe_inputs)
                forward_pe_inputs = get_forward_pe(ticker_info=stock_info)
                forward_pe_list.append(forward_pe_inputs)
            # Calculate metrics
            pb_industry = calculate_pb_ratio(mc_equity_pairs=pb_list)
            de_industry = calculate_de_ratio(debt_equity_pairs=de_list)
            revenue_growth_industry = calculate_rev_growth(revenue_pairs=revenue_growth_list)
            gross_margin_industry = calculate_gross_margin(revenue_margin_pairs=gross_margin_list)
            roe_industry = calculate_roe(roe_pairs=roe_list)
            ttm_pe_industry = calculate_ttm_pe(mc_ni_pairs=ttm_pe_list)
            forward_pe_industry = calculate_forward_pe(industry_pe_list=forward_pe_list)

            new_row = {'Sector': sector,
                       'Industry': ind,
                       'PB_Ratio': pb_industry,
                       'DE_Ratio': de_industry,
                       'Revenue_Growth': revenue_growth_industry,
                       'Gross_Margin': gross_margin_industry,
                       'RoE': roe_industry,
                       'TTM_PE': ttm_pe_industry,
                       'Forward_PE': forward_pe_industry,}
            print(new_row)

            industry_values[ind] = new_row

    print(industry_values)
    return industry_values
