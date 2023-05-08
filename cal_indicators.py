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

