import datetime
import requests
import pytz
import pandas as pd
import os
import time


def get_start_end_time(date=None):
    if date is None:
        date = datetime.date.today()

    eastern_tz = pytz.timezone('US/Eastern')

    # Get the start of the day as a timezone-aware datetime object
    midnight = datetime.datetime.combine(date, datetime.time.min)
    start_time = eastern_tz.localize(midnight)

    # Get the end of the day as a timezone-aware datetime object
    end_time = datetime.datetime.combine(date, datetime.time.max)
    end_time = eastern_tz.localize(end_time)

    # If the date is today, set the end time to the current time in Eastern Time
    if date == datetime.date.today():
        et_now = datetime.datetime.utcnow().astimezone(eastern_tz)
        end_time = et_now

    return start_time, end_time


def get_daily_data(date=None, retries=3, sleep_time=5):
    url = "https://api.pro.coinbase.com/products/BTC-USD/candles"

    # Find the start and end time of a date
    if date is None:
        date = datetime.date.today()

    start_time, end_time = get_start_end_time(date)

    params = {
        "start": start_time.isoformat() + "Z",
        "end": end_time.isoformat() + "Z",
        "granularity": 3600,  # 1 day in seconds
    }

    for attempt in range(retries):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # Extract data from the API response
            data = response.json()

            # Separate the data into individual lists
            time_data = [datetime.datetime.utcfromtimestamp(item[0]) for item in data]
            low_prices = [item[1] for item in data]
            high_prices = [item[2] for item in data]
            open_prices = [item[3] for item in data]
            close_prices = [item[4] for item in data]
            volumes = [item[5] for item in data]

            return time_data, low_prices, high_prices, open_prices, close_prices, volumes

        time.sleep(sleep_time)

    print(f"Error: Failed to fetch data for {date} after {retries} retries")
    return None, None, None, None, None, None


def get_price_data_past_n_days(n):
    all_time_data = []
    all_open_prices = []
    all_high_prices = []
    all_low_prices = []
    all_close_prices = []
    all_volumes = []

    for i in range(n):
        past_date = datetime.date.today() - datetime.timedelta(days=i)
        time_data, open_prices, high_prices, low_prices, close_prices, volumes = get_daily_data(past_date)

        if (time_data is not None and open_prices is not None and high_prices is not None and
            low_prices is not None and close_prices is not None and volumes is not None):

            all_time_data.extend(time_data)
            all_open_prices.extend(open_prices)
            all_high_prices.extend(high_prices)
            all_low_prices.extend(low_prices)
            all_close_prices.extend(close_prices)
            all_volumes.extend(volumes)

    sorted_data = sorted(zip(all_time_data, all_open_prices, all_high_prices, all_low_prices, all_close_prices, all_volumes))
    all_time_data, all_open_prices, all_high_prices, all_low_prices, all_close_prices, all_volumes = zip(*sorted_data)

    price_data_df = pd.DataFrame({
        'time': all_time_data,
        'open': all_open_prices,
        'high': all_high_prices,
        'low': all_low_prices,
        'close': all_close_prices,
        'volume': all_volumes,
    })

    return price_data_df


def save_price_data_to_csv(df, output_dir='.', filename='price_data.csv'):
    """
    Save the price data DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The price data DataFrame.
        output_dir (str): The directory to save the output file (default is 'output').
        filename (str): The name of the output file (default is 'price_data.csv').
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path = os.path.join(output_dir, filename)
    df.to_csv(output_file_path, index=False)
    print(f"Price data saved to {output_file_path}")


# Example usage
price_data_df = get_price_data_past_n_days(30)
save_price_data_to_csv(price_data_df)