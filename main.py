import pandas as pd
from cal_indicators import squeeze_momentum_indicator
from get_price import save_price_data_to_csv
from plots import plot_combined, plot_squeeze_momentum

# read the price data from price_data.csv
price_data = pd.read_csv('price_data.csv')

# add sma indicators
price_data = squeeze_momentum_indicator(price_data)

save_price_data_to_csv(price_data, filename='price_data_with_indicator.csv')

# plot the price data
plot_squeeze_momentum(price_data)
