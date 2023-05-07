#%%
from get_price import get_price_data_past_n_days
from cal_indicators import plot_combined, add_sma_indicators
#%%
"""
# Get Bitcoin price on a daily basis

This code block includes three functions for analyzing the opening price of Bitcoin on a daily basis:

- `get_start_end_per_day`: Returns the start and end time of a day given a date.
- `get_daily_price`: Fetches the daily opening price of BTC-USD from the Coinbase Pro API for a given date.
- `plot_price`: Plots the opening price of BTC-USD over time.
"""

# Fetch and preprocess data
n_days = 180
price_data_df = get_price_data_past_n_days(n_days)
print(price_data_df)

#%%


price_data_df = add_sma_indicators(price_data_df)

plot_combined(price_data_df)
# %%
print(price_data_df)
# %%
