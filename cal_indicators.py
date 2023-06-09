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


def generate_smi_signals(df, smi_col='squeeze_momentum', squeeze_on_col='squeeze_on', min_smi_threshold=0.2):
    """
    Generate buy and sell signals based on the squeeze momentum indicator.

    Args:
        df (pd.DataFrame): The price data DataFrame with SMI values.
        smi_col (str): The column name for the squeeze momentum indicator values.
        squeeze_on_col (str): The column name for the squeeze on flag.
        min_smi_threshold (float): The minimum SMI threshold for generating signals.

    Returns:
        pd.DataFrame: The input DataFrame with buy and sell signals added as a new column.
    """
    signals = []
    for i in range(len(df)):
        if df.at[i, squeeze_on_col] and df.at[i, smi_col] > min_smi_threshold:
            signals.append('buy')
        elif df.at[i, squeeze_on_col] and df.at[i, smi_col] < -min_smi_threshold:
            signals.append('sell')
        else:
            signals.append(None)

    df['signal'] = signals
    return df



def backtest_sma_strategy(price_data_df, initial_balance=10000, short_term_MA='short_term_MA', long_term_MA='long_term_MA'):
    in_position = False
    balance = pd.DataFrame(columns=['time', 'balance'])
    current_balance = initial_balance

    for index, row in price_data_df.iterrows():
        if row['signal'] == 'buy' and not in_position:
            in_position = True
            buy_price = row['close']
            buy_time = row['time']
            shares_to_buy = current_balance / row['close']
            print(f"{buy_time}: BUY  at {buy_price:8.2f}, Total profit: {current_balance - initial_balance:10.2f}, Profit percentage: {((current_balance - initial_balance) / initial_balance) * 100:6.2f}%")

        if row['signal'] == 'sell' and in_position:
            in_position = False
            sell_price = row['close']
            sell_time = row['time']
            current_balance = shares_to_buy * row['close']
            print(f"{sell_time}: SELL at {sell_price:8.2f}, Total profit: {current_balance - initial_balance:10.2f}, Profit percentage: {((current_balance - initial_balance) / initial_balance) * 100:6.2f}%")
            new_row = pd.DataFrame({'time': [sell_time], 'balance': [current_balance]})
            balance = pd.concat([balance, new_row], ignore_index=True)

    # Account for the value of the remaining shares at the end of the backtesting period
    if in_position:
        starting_balance = shares_to_buy * price_data_df.iloc[-1]['close']
        new_row = pd.DataFrame({'time': [price_data_df.iloc[-1]['time']], 'balance': [starting_balance]})
        balance = pd.concat([balance, new_row], ignore_index=True)

    return balance




