import pandas as pd
from cal_indicators import *
from get_price import save_price_data_to_csv
from plots import *

# read the price data from price_data.csv
price_data = pd.read_csv('price_data.csv')

# add sma indicators
# price_data = squeeze_momentum_indicator(price_data)
# price_data = calculate_moving_averages(price_data,'close',5, 20)
price_data = calculate_ema(price_data,'close',5)
price_data = calculate_ema(price_data,'close',20)

# save_price_data_to_csv(price_data, filename='price_data_with_indicator.csv')

# plot the price data
# plot_squeeze_momentum(price_data)
plot_combined(price_data,'EMA5','EMA20')
