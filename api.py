from datetime import datetime, date, timedelta
from typing import List
import requests
import statistics




API_KEY = "FCJFW9PVWJ6HDU3K"
BASE_URL = "https://www.alphavantage.co/query"
MICROSOFT = "MSFT"
APPLE = "AAPL"
BOEING = "BA"


TimeSeriesJson = dict
def get_time_series_data_for(symbol: str) -> TimeSeriesJson:
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
# ms_data = get_time_series_data_for(MICROSOFT)
# ms_seven_day_avg_volume = calculate_seven_day_avg_volume(ms_data)

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


# Given a list of stock symbols, find the symbol with the largest return over the past month
SYMBOLS = [BOEING, APPLE, MICROSOFT]
