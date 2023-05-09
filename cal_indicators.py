import numpy as np
import talib as ta
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

def add_sma_indicators(df, sma_25_period=10, sma_50_period=20):
    df['sma_25'] = df['close'].rolling(window=sma_25_period).mean()
    df['sma_50'] = df['close'].rolling(window=sma_50_period).mean()
    return df

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

def calculate_moving_averages(df, price_column, short_term_window, long_term_window):
    """
    Calculate short-term and long-term moving averages for the given price data.

    Args:
        df (pd.DataFrame): The price data DataFrame.
        price_column (str): The name of the column containing the prices in the DataFrame.
        short_term_window (int): The window length for the short-term moving average.
        long_term_window (int): The window length for the long-term moving average.

    Returns:
        pd.DataFrame: The DataFrame with additional columns for short-term and long-term moving averages.
    """
    df['short_term_MA'] = df[price_column].rolling(window=short_term_window).mean()
    df['long_term_MA'] = df[price_column].rolling(window=long_term_window).mean()
    return df

def calculate_ema(df, price_column, window_length):
    """
    Calculate the Exponential Moving Average for the given price data.

    Args:
        df (pd.DataFrame): The price data DataFrame.
        price_column (str): The name of the column containing the prices in the DataFrame.
        window_length (int): The window length for the Exponential Moving Average.

    Returns:
        pd.DataFrame: The DataFrame with an additional column for the EMA.
    """
    label='EMA'+str(window_length)
    df[label] = df[price_column].ewm(span=window_length, adjust=False).mean()
    return df

def generate_signals(df, short_term_MA_col, long_term_MA_col):
    """
    Generate buy and sell signals based on short-term and long-term moving averages.

    Args:
        df (pd.DataFrame): The price data DataFrame with short-term and long-term moving average columns.
        short_term_MA_col (str): The name of the column containing the short-term moving average.
        long_term_MA_col (str): The name of the column containing the long-term moving average.

    Returns:
        pd.DataFrame: The DataFrame with additional 'signal' column containing buy, sell, or hold values.
    """
    # Initialize 'signal' column with 'hold' values
    df['signal'] = 'hold'

    # Generate buy and sell signals
    for i in range(1, len(df)):
        if df.at[i, short_term_MA_col] > df.at[i, long_term_MA_col] and df.at[i - 1, short_term_MA_col] <= df.at[i - 1, long_term_MA_col]:
            df.at[i, 'signal'] = 'buy'
        elif df.at[i, short_term_MA_col] < df.at[i, long_term_MA_col] and df.at[i - 1, short_term_MA_col] >= df.at[i - 1, long_term_MA_col]:
            df.at[i, 'signal'] = 'sell'

    return df

def backtest(df, initial_balance=10000):
    balance = initial_balance
    shares = 0
    in_position = False

    for index, row in df.iterrows():
        if row['signal'] == 'buy' and not in_position:
            shares = balance / row['close']
            balance = 0
            in_position = True
            print(f"{row['time']} - Buy at {row['close']}")

        elif row['signal'] == 'sell' and in_position:
            balance = shares * row['close']
            shares = 0
            in_position = False
            print(f"{row['time']} - Sell at {row['close']}")

    if in_position:
        balance = shares * df.iloc[-1]['close']

    profit_loss = balance - initial_balance
    return profit_loss


