import yfinance as yf

# Screener for getting industries
def screen_by_industry(industry):
    try:
        query = yf.EquityQuery('and', [
            yf.EquityQuery('is-in', ['industry', f'{industry}']),
            yf.EquityQuery('is-in', ['exchange', 'NYQ', 'NMS', 'ASE', 'NCM']),
        ])
        query_results = yf.screen(query, size=250)
        data = query_results['quotes']
        stocks = [d['symbol'] for d in data]
        return stocks
    except ValueError:
        print(f'{industry} is not available')
        return None
