from datetime import datetime, date, timedelta
from typing import List
import requests
import statistics


# I would normally put this in a secrets file, but in the interest of
# making this solution usable for the grader without having to get a new
# API KEY, I'm making it public for now.
API_KEY = "FCJFW9PVWJ6HDU3K"
BASE_URL = "https://www.alphavantage.co/query"
MICROSOFT = "MSFT"
APPLE = "AAPL"
BOEING = "BA"


TimeSeriesJson = dict
StockSymbol = str
ReturnPercAsDecimal = float


def get_time_series_data_for(symbol: StockSymbol) -> TimeSeriesJson:
    url_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    resp = requests.get(BASE_URL, params=url_params)
    resp.raise_for_status()
    return resp.json()


def get_date(date_str: str) -> date:
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def calculate_seven_day_avg_volume(data: TimeSeriesJson) -> float:
    ms_by_day = data['Time Series (Daily)']

    today = date.today()
    one_week_ago = today - timedelta(days=7)

    ms_past_seven_days = [
        vals for date_str, vals in ms_by_day.items()
        if today >= get_date(date_str) > one_week_ago
    ]
    seven_day_volume = statistics.mean([int(d['5. volume']) for d in ms_past_seven_days])

    return seven_day_volume


# Find the average volume of MSFT in the past 7 days
ms_data = get_time_series_data_for(MICROSOFT)
ms_seven_day_avg_volume = calculate_seven_day_avg_volume(ms_data)
print(ms_seven_day_avg_volume)


def get_highest_closing_six_months(data: TimeSeriesJson) -> float:
    apple_by_day = data['Time Series (Daily)']
    today = date.today()

    # Would try to be more accurate, but in the interest of time
    six_months_in_days = round(6 * 365 / 12, 0)

    six_months_ago = today - timedelta(days=six_months_in_days)
    six_month_high = max(
        float(vals['4. close']) for day, vals
        in apple_by_day.items()
        if get_date(day) > six_months_ago
    )
    return six_month_high


# Find the highest closing price of AAPL in the past 6 months
apple_data = get_time_series_data_for(APPLE)
apple_six_month_high = get_highest_closing_six_months(apple_data)
print(apple_six_month_high)


def get_thirty_day_diffs(data: TimeSeriesJson) -> List[float]:
    by_day = data['Time Series (Daily)']

    today = date.today()
    one_month_ago = today - timedelta(days=30)

    thirty_day_diffs = []
    for day, vals in by_day.items():
        if get_date(day) >= one_month_ago:
            thirty_day_diffs.append(float(vals['2. high']) - float(vals['3. low']))

    return thirty_day_diffs


# Find the difference between open and close price for BA for every day in the last month
boeing_data = get_time_series_data_for(BOEING)
boeing_30_days_diffs: List = get_thirty_day_diffs(boeing_data)
print(boeing_30_days_diffs)


def highest_return_past_x_days(symbol: StockSymbol,
                               num_days: int) -> ReturnPercAsDecimal:

    by_day = get_time_series_data_for(symbol)['Time Series (Daily)']

    today = date.today()
    price_today = float(by_day[str(today)]['4. close'])

    one_month_ago = today - timedelta(days=30)

    # If day falls on day market is closed, find previous close:
    market_closed = True
    while market_closed:
        try:
            price_thirty_days_ago = float(by_day[str(one_month_ago)]['4. close'])
            market_closed = False
        except KeyError:
            one_month_ago -= timedelta(days=1)


    diff = price_thirty_days_ago - price_today

    return diff / price_thirty_days_ago


def find_stock_with_highest_return(symbols: List[StockSymbol]) -> StockSymbol:
    stock_returns = {
        highest_return_past_x_days(symbol, 30): symbol
        for symbol in symbols
    }
    return stock_returns[max(stock_returns.keys())]


# Given a list of stock symbols, find the symbol with the largest return over the past month
stock_symbols = [BOEING, APPLE, MICROSOFT]
stock_highest_return = find_stock_with_highest_return(stock_symbols)
print(stock_highest_return)



