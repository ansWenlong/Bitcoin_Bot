import numpy as np
import matplotlib.pyplot as plt

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
    ax.plot(df['time'], df['close'], label='BTC-USD Price', color='black')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.set_title('Bitcoin Price and SMA Indicators')
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
    
# # Add squeeze momentum indicators indicators
# squeeze_momentum_df = add_sqzmom_indicators(price_data_df)


# # Plot the data
# plot_price_and_squeeze_indicator(squeeze_momentum_df)
