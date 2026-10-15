# 📈 Peer Benchmarks 

A python based research tool that calculates various sector and industry benchmarks using data obtained
from the yfinance API. Benchmarks are stored in a SQLite file. 

---

### ➕ Calculation Methodology ➗
For the following metrics:
- Price to Book Ratio
- Debt to Equity Ratio
- Return on equity
- Revenue Growth 
- Gross Margin
- TTM P/E

the weighted average was calculated by obtaining data from each company in the sector/industry and
summing the totals and then dividing. For example, price to book was calculated by calculating the total sum
of each company's market cap and equity in a peer group and then dividing total market cap by
total equity. This methodology was used for each ratio and its respective inputs.

Forward P/E for each peer group was found by obtaining the median of each respective peer group.

---

## 📂 File Structure
```
peer-benchmarks
├── peer_benchmarks/
│   ├── src/ # Source scripts for screening and analysis
│   │    ├── industry/ # Scripts for calculaing industry benchmarks
│   │    │    ├── indsutry_calculator/
│   │    │    │    ├── __init__.py
│   │    │    │    └── calculator.py
│   │    │    ├── __init__.py
│   │    │    └── industry_avg.py # Commit data to SQLite database
│   │    ├── screeners/
│   │    │    ├── __init__.py
│   │    │    └── screeners.py # Use the yfinance API to pull stocks in each peer group 
│   │    ├── sector/ # Scripts for calculaing sector benchmarks
│   │    │    ├── sector_calculator/
│   │    │    │    ├── __init__.py
│   │    │    │    └── calculator.py
│   │    │    ├── __init__.py
│   │    │    └── sector_avg.py # Commit data to SQLite database
│   │    ├── web_scraping/
│   │    │    ├── __init__.py
│   │    │    └── web_scraper.py # Pulls the available industry and sector benchmark titles    
│   │    └── __init__.py    
│   ├── __init__.py
│   ├── config.py # Paths for saving benchmark data
│   └── main.py # Main script for calculating benchmarks
├── README.md # Current file
└── environment.yml # Required packages
```

---

## 🚧 Setup Instructions

1. **Clone the repository**

```git clone https://github.com/JustinWoo20/peer-benchmarks.git```

2. **Navigate to project repository**

```cd peer-benchmarks/peer_benchmarks```

3. **Create and activate new environment**
Create:

```python -m venv .venv```

Activate it:

Windows ```.\.venv\Scripts\activate```

macOS/Linux ```source .venv/bin/activate```

4. Install dependencies
```pip install -r environment.yml```

5. Create .env file
You will need to create a free API Key at the following website:
https://www.exchangerate-api.com/docs/python-currency-api

6. Copy your API key to the .env file

7. Run the calculator
```python scripts/main.py```

8. Select sector, industry, or both when prompted

---

## 📷 Example Outputs
![Industry Results](ex_images/industry_results.png)

![Sector Results](ex_images/sector_results.png)

---
## 📌 Future Improvements
- Calculate more financial ratios
- Add regional peer groups

---

### 📜 License
MIT License – free to use, modify, and distribute.

---

### 🎯 Update
- Refactored from csv to SQLite

---
### ⚠️ Disclaimer
This tool is not licensed financial advice. It is intended for discovering possible investment ideas. 
It should not be used as the deciding factor for investment decisions. 
Always perform independent research and consult a licensed financial professional before any stock purchases.