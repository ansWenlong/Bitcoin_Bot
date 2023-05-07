import numpy as np
import talib as ta
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
    

def squeeze_momentum_indicator(df, bb_length=20, bb_mult=2.0, kc_length=20, kc_mult=1.5, use_true_range=True):
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values

    # Calculate Bollinger Bands
    basis = ta.SMA(close, bb_length)
    dev = bb_mult * ta.STDDEV(close, bb_length)
    upper_bb = basis + dev
    lower_bb = basis - dev

    # Calculate Keltner Channels
    ma = ta.SMA(close, kc_length)
    if use_true_range:
        tr = ta.TRANGE(high, low, close)
    else:
        tr = high - low
    rangema = ta.SMA(tr, kc_length)
    upper_kc = ma + rangema * kc_mult
    lower_kc = ma - rangema * kc_mult

    sqz_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
    sqz_off = (lower_bb < lower_kc) & (upper_bb > upper_kc)
    no_sqz = ~sqz_on & ~sqz_off

    linreg_input = close - ta.SMA(np.maximum(high, close) + np.minimum(low, close) / 2, kc_length)
    val = ta.LINEARREG(linreg_input, kc_length)

    df['val'] = val
    df['sqz_on'] = sqz_on
    df['sqz_off'] = sqz_off
    df['no_sqz'] = no_sqz

    return df

# Example usage
# df is a pandas DataFrame with columns 'close', 'high', and 'low'
result = squeeze_momentum_indicator(df)
