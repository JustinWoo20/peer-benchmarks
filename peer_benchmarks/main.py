from src.sector.sector_avg import calculate_sector_benchmarks
from src.industry.industry_avg import calculate_industry_benchmarks

answer = input('Calculate sector, industry, or benchmarks for both?\n'
               'Please type one of the following: "sector", "industry", "both"\n').lower()

if answer == 'sector':
    calculate_sector_benchmarks()

elif answer == 'industry':
    calculate_industry_benchmarks()

elif answer == 'both':
    calculate_sector_benchmarks()
    calculate_industry_benchmarks()

else:
    print('Please try again and provide one of the following values: "sector", "industry", "both"')