import pandas as pd
from cal_indicators import squeeze_momentum_indicator, plot_squeeze_momentum
from get_price import save_price_data_to_csv

# read the price data from price_data.csv
price_data = pd.read_csv('price_data.csv')

# add sma indicators
price_data = squeeze_momentum_indicator(price_data)

save_price_data_to_csv(price_data, filename='price_data_with_indicator.csv')

# plot the price data
plot_squeeze_momentum(price_data)
