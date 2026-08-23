import numpy as np
from peer_benchmarks.src.web_scraping import web_scraper
from peer_benchmarks.src.screeners.screeners import screen_by_industry
import sqlite3 as sql
import yfinance as yf

# conn = sql.connect('../../../../data/peer-benchmarks/db/industry_averages.db')
# cur = conn.cursor()
#
# cur.execute("""DROP TABLE IF EXISTS industry_averages""")
# cur.execute("""CREATE TABLE IF NOT EXISTS industry_averages (
#             Industry TEXT NOT NULL,
#             pb_ratio FLOAT NOT NULL,
#             de_ratio FLOAT NOT NULL,
#             revenue_growth FLOAT NOT NULL,
#             gross_profit FLOAT NOT NULL,
#             ttmpe FLOAT NOT NULL,
#             forwardpe FLOAT NOT NULL,
#             net_profit FLOAT NOT NULL,""")

def get_yf_ticker(ticker):
    t = yf.Ticker(ticker)
    return t

def get_market_cap(ticker):
    info = ticker.info
    market_cap = info.get('marketCap') or info.get('nonDilutedMarketCap')
    if market_cap is None:
        shares_outstanding = info.get('sharesOutstanding') or info.get('floatShares')
        current_price = info.get('currentPrice')
        market_cap = shares_outstanding * current_price
    return market_cap

def get_income_statistics(ticker):
    income_statement = ticker.get_income_stmt()
    income_transposed = income_statement.transpose()
    revenue = income_transposed.get('TotalRevenue')
    recent_revenue = revenue.iloc[0] if not None else 0
    previous_revenue_in = revenue.iloc[1] if not None else 0
    gp = income_transposed.get('GrossProfit')
    if gp is None:
        return recent_revenue, previous_revenue_in, 0
    gp = gp.iloc[0]
    return recent_revenue, previous_revenue_in, gp

def get_balance_statistics(ticker):
    balance_sheet = ticker.get_balance_sheet()
    balance_transposed = balance_sheet.transpose()
    total_shareholder_equity = balance_transposed['StockholdersEquity'].iloc[0]
    td = balance_transposed.get('TotalDebt')
    if td is None:
        return 0, 0
    td = td.iloc[0]
    return total_shareholder_equity, td

def pe_ratios(ticker):
    income_statement = ticker.get_income_stmt()
    info = ticker.info
    income_transposed = income_statement.transpose()
    net_income = income_transposed.get('NetIncome')
    if net_income is None:
        net_income = income_transposed.get('NetIncomeCommonStockholders')
    net_income = net_income.iloc[0] if net_income is not None else None
    market_cap = get_market_cap(ticker)
    ttm_pe = market_cap / net_income
    try:
        f_pe = info['forwardPE']
    except KeyError:
        f_pe = 0
    if ttm_pe > 0:
        return market_cap, net_income, f_pe
    else:
        return 0, 0, f_pe


# Obtain companies in each industry in major American stock exchanges
screener_industries = web_scraper.obtain_equity_query()
industry_stock_dict = {}
for si in screener_industries.values():
    for i in si:
        stock_list = screen_by_industry(industry=i)
        industry_stock_dict[i] = stock_list


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
        # Find most recent stockholder's equity
        equity, total_debt = get_balance_statistics(yf_ticker)
        industry_equity += equity
        # Find total debt per industry
        industry_debt += total_debt
        # Find most recent revenue and previous
        total_revenue, previous_revenue, gross_profit = get_income_statistics(yf_ticker)
        industry_revenue += total_revenue
        industry_previous_revenue += previous_revenue
        # Gross Profit
        industry_gross_profit += gross_profit
        # Trailing P/E and Forward P/E
        pe_market_cap, pe_net_income, forward_pe = pe_ratios(yf_ticker)
        industry_pe_mc += pe_market_cap
        industry_net_income += pe_net_income
        industry_forward_pe.append(forward_pe)

    # Calculations
    # P/B
    industry_pb = industry_mc / industry_equity
    industry_de = industry_debt / industry_equity
    industry_rev_growth = (industry_revenue / industry_previous_revenue) - 1
    industry_gross_margin = industry_gross_profit / industry_revenue
    industry_ttm_pe = industry_pe_mc / industry_net_income

    forward_pe_cleaned = [x for x in industry_forward_pe if x != 0] # Remove placeholder 0  values from Forward PE
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
        # Find company
#         weighted_pb = market_cap * pb
#         weighted_pb_list.append(weighted_pb)
#         weighted_de = market_cap * de
#         weighted_de_list.append(weighted_de)
#         weighted_rg = market_cap * revenue_growth
#         weighted_rg_list.append(weighted_rg)
#         weighted_gm = market_cap * gross_margin
#         weighted_gm_list.append(weighted_gm)
#         weighted_ttmpe = market_cap * trailing_pe
#         weighted_ttmpe_list.append(weighted_ttmpe)
#         weighted_fpe = market_cap * forward_pe
#         weighted_fpe_list.append(weighted_fpe)
#         industry_size += market_cap
#
#     # Add up industry totals
#     industry_pb_sum = sum(weighted_pb_list)
#     industry_de_sum = sum(weighted_de_list)
#     industry_rg_sum = sum(weighted_rg_list)
#     industry_gm_sum = sum(weighted_gm_list)
#     industry_ttmpe_sum = sum(weighted_ttmpe_list)
#     industry_fpe_sum = sum(weighted_fpe_list)
#
#     industry_pb = industry_pb_sum / industry_size
#     industry_de = industry_de_sum / industry_size
#     industry_rg = industry_rg_sum / industry_size
#     industry_gm = industry_gm_sum / industry_size
#     industry_ttmpe = industry_ttmpe_sum / industry_size
#     industry_fpe = industry_fpe_sum / industry_size
#
#     inner_dict = {'P/B': industry_pb,
#                   'D/E': industry_de,
#                   'Revenue Growth': industry_rg,
#                   'Gross Profit Margin': industry_gm,
#                   'Trailing PE': industry_ttmpe,
#                   'Forward PE': industry_fpe}
#     print(inner_dict)
#
#     industry_values[ind] = inner_dict
#
# print(industry_values)


# new_row = [(i,) for i in industry_list]
# cur.executemany("INSERT INTO industry_averages VALUES(industries)", new_row)
# conn.close()
#
