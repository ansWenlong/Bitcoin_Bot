import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import pandas as pd

def add_sqzmom_indicators(df, bb_period=20, kc_period=20, atr_period=14, multiplier=2):
    # Bollinger Bands
    df['sma'] = df['close'].rolling(window=bb_period).mean()
    df['stddev'] = df['close'].rolling(window=bb_period).std()
    df['upper_bb'] = df['sma'] + (multiplier * df['stddev'])
    df['lower_bb'] = df['sma'] - (multiplier * df['stddev'])

    # Keltner Channels
    df['tr_high'] = np.maximum(df['high'] - df['low'], np.maximum(np.abs(df['high'] - df['close'].shift(1)), np.abs(df['low'] - df['close'].shift(1))))
    df['atr'] = df['tr_high'].rolling(window=atr_period).mean()
    df['upper_kc'] = df['sma'] + (multiplier * df['atr'])
    df['lower_kc'] = df['sma'] - (multiplier * df['atr'])

    # Squeeze Momentum Indicator
    df['squeeze_on'] = (df['lower_bb'] > df['lower_kc']) & (df['upper_bb'] < df['upper_kc'])
    df['squeeze_off'] = (df['lower_bb'] < df['lower_kc']) & (df['upper_bb'] > df['upper_kc'])

    return df

def add_sma_indicators(df, sma_25_period=10*24*12, sma_50_period=20*24*12):
    df['sma_25'] = df['close'].rolling(window=sma_25_period).mean()
    df['sma_50'] = df['close'].rolling(window=sma_50_period).mean()
    return df

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

def plot_sma_indicators(df, ax=None):
    if ax is None:
        ax = plt.gca()
    ax.plot(df['time'], df['sma_25'], label='SMA 25', color='blue')
    ax.plot(df['time'], df['sma_50'], label='SMA 50', color='red')
    ax.legend()

def plot_combined(price_data_df):
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_price(price_data_df, ax)
    plot_sma_indicators(price_data_df, ax)
    plt.show()


def squeeze_momentum_indicator(df, length_bb=20, mult_bb=2, length_kc=20, mult_kc=1.5, use_truerange=True):
    """
    Calculate the squeeze momentum indicator for the given DataFrame.

    Args:
        df (pd.DataFrame): The price data DataFrame.
        length_bb (int): The length of the Bollinger Bands.
        mult_bb (float): The multiplier for the Bollinger Bands.
        length_kc (int): The length of the Keltner Channels.
        mult_kc (float): The multiplier for the Keltner Channels.
        use_truerange (bool): Whether to use True Range for Keltner Channels calculations.

    Returns:
        pd.DataFrame: The input DataFrame with the squeeze momentum indicator values added as new columns.
    """
    # Bollinger Bands
    basis_bb = df['close'].rolling(window=length_bb).mean()
    dev = mult_bb * df['close'].rolling(window=length_bb).std()
    upper_bb = basis_bb + dev
    lower_bb = basis_bb - dev

    # Keltner Channels
    ma = df['close'].rolling(window=length_kc).mean()
    range_kc = ta.TRANGE(df['high'], df['low'], df['close']) if use_truerange else (df['high'] - df['low'])
    rangema = range_kc.rolling(window=length_kc).mean()
    upper_kc = ma + rangema * mult_kc
    lower_kc = ma - rangema * mult_kc

    # Squeeze Momentum Indicator
    sqz_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
    sqz_off = (lower_bb < lower_kc) & (upper_bb > upper_kc)

    val = ta.LINEARREG(df['close'] - ((df['high'] + df['low'] + df['close']) / 3).rolling(window=length_kc).mean(), length_kc)
    val_min = val.min()
    val_max = val.max()
    val_abs_max = max(abs(val_min), val_max)
    df['squeeze_momentum'] = val/val_abs_max
    df['squeeze_on'] = sqz_on
    df['squeeze_off'] = sqz_off

    return df

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
    ax2.bar(df['time'], df['squeeze_momentum'], color=colors, label='Squeeze Momentum Indicator', width=0.02)
    ax2.set_ylabel('Squeeze Momentum')

    # Plot squeeze on/off markers
    squeeze_on_times = df.loc[df['squeeze_on'], 'time']
    squeeze_off_times = df.loc[df['squeeze_off'], 'time']
    ax2.scatter(squeeze_on_times, np.zeros(len(squeeze_on_times)), marker='^', color='black', label='Squeeze On')
    ax2.scatter(squeeze_off_times, np.zeros(len(squeeze_off_times)), marker='v', color='blue', label='Squeeze Off')

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