import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import pandas as pd
import numpy as np

def plot_sma_indicators(df, MA1='short_term_MA', MA2='long_term_MA',ax=None, ):
    if ax is None:
        ax = plt.gca()
    ax.plot(df['time'], df[MA1], label=MA1, color='blue')
    ax.plot(df['time'], df[MA2], label=MA2, color='red')
    ax.legend()

def plot_combined(price_data_df, MA1='short_term_MA', MA2='long_term_MA'):
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_price(price_data_df, ax)
    plot_sma_indicators(price_data_df, MA1,MA2,ax)
    plt.show()

def plot_price(df, ax=None):
    if ax is None:
        ax = plt.gca()

    # Convert the 'time' column to datetime objects
    df['time'] = pd.to_datetime(df['time'])

    ax.plot(df['time'], df['close'], label='BTC-USD Price', color='black')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.set_title('Bitcoin Price and SMA Indicators')

    # Set the x-axis date format to display dates with a unit of day
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    ax.legend()

def plot_squeeze_momentum(df):
    """
    Plot the squeeze momentum indicator along with the price.

    Args:
        df (pd.DataFrame): The price data DataFrame with the squeeze momentum indicator values.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)

    # Convert the 'time' column to datetime objects
    df['time'] = pd.to_datetime(df['time'])
    
    # Price chart
    ax1.plot(df['time'], df['close'], label='Close Price', color='blue')
    ax1.set_title('BTC Price and Squeeze Momentum Indicator')
    ax1.set_ylabel('Price')

    # Squeeze Momentum Indicator chart
    colors = np.where(df['squeeze_momentum'] >= 0, 'g', 'r')
    ax2.bar(df['time'], df['squeeze_momentum'], color=colors, label='Squeeze Momentum Indicator', width=0.1)
    ax2.set_ylabel('Squeeze Momentum')

   #  # Plot squeeze on/off markers
   #  squeeze_on_times = df.loc[df['squeeze_on'], 'time']
   #  squeeze_off_times = df.loc[df['squeeze_off'], 'time']
   #  ax2.scatter(squeeze_on_times, np.zeros(len(squeeze_on_times)), marker='^', color='black', label='Squeeze On')
   #  ax2.scatter(squeeze_off_times, np.zeros(len(squeeze_off_times)), marker='v', color='blue', label='Squeeze Off')

    # Set the maximum number of x-axis ticks
    max_ticks = 10
    ax2.xaxis.set_major_locator(MaxNLocator(max_ticks))

    # Format x-axis labels as dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    plt.xlabel('Time')
    ax1.legend()
    ax2.legend()
    plt.show()

def plot_price_and_squeeze_indicator(df):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(df['time'], df['close'], label='BTC-USD Price', color='black')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Price')
    ax1.set_title('Bitcoin Price and Squeeze Momentum Indicator')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.plot(df['time'], df['sma'], label='sma', color='green')
    ax2.set_ylabel('sma')
    ax2.legend(loc='upper left')

    plt.show()


