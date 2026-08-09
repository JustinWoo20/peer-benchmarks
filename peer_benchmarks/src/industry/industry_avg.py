from peer_benchmarks.src.web_scraping import web_scraper
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

si_dict = web_scraper.sect_ind_dict
industry_list = []
for ind in si_dict.values():
    for i in ind:

        i_lower = i.lower()
        industry_list.append(i_lower)

industry_index = industry_list.index('agricultural-inputs')
industry_title = industry_list[industry_index]
print(industry_title)
yf_industry = yf.Industry('agricultural-inputs')
print(yf_industry.overview)

# new_row = [(i,) for i in industry_list]
# cur.executemany("INSERT INTO industry_averages VALUES(industries)", new_row)
# conn.close()
#
