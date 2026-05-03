import pandas as pd
import numpy as np

def smoothing(series , period) :
    # smoothing indicator using sma
    return series.rolling(period).mean()

def wilder_ema(series , period) :
    # mathces Tradingview style
    alpha = 2 / (period + 1)
    sma = series.rolling(period).mean()
    ema = series.copy().astype(float)
    ema.iloc[:period - 1] = np.nan
    ema.iloc[period - 1] = sma.iloc[period - 1]
    for i in range(period, len(series)):
        ema.iloc[i] = alpha * series.iloc[i] + (1 - alpha) * ema.iloc[i - 1]
    return ema

def wilder_rsi(series , period=14) :
    # matches Tradingview style
    delta = series.diff()
    gain = delta.clip(lower=0)
    average_gain = gain.ewm(alpha=1/period , adjust=False).mean()
    loss = (-delta.clip(upper=0))
    average_loss = loss.ewm(alpha=1/period , adjust=False).mean()
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def wilder_atr(high , low , close , period=14) : 
    # matches Tradingview style
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low , 
        (high - prev_close).abs() ,
        (low - prev_close).abs()
    ] , axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period , adjust=False).mean()

    return atr 

def buying_volume_pivot(series) :
    # find that the buying volume is greater than the selling volume within 10 days (roughly 7 candles)
    pass

def selling_volume_pivot(series) :
    # find that the selling volume is greater than the buying volume within 10 days (roughly 7 candles)
    pass

def indicators(df) :
    #Optimize Later
    df = df.copy() 

    # Exponential Moving average (EMA) 
    df["EMA10"] = wilder_ema(df["close"] , 10)
    df["EMA20"] = wilder_ema(df["close"] , 20)
    df["EMA50"] = wilder_ema(df["close"] , 50)
    df["EMA150"] = wilder_ema(df["close"] , 150)
    df["EMA200"] = wilder_ema(df["close"] , 200)

    # Average true range (ATR)
    df["ATR"] = wilder_atr(df["high"] , df["low"] , df["close"] , 14)

    # Relative Strength Index (RSI - Wilder's version)
    rsi = wilder_rsi(df["close"] , 21)
    df["RSI"] = rsi
    df["RSI_smoothing"] = smoothing(rsi ,14) 

    # Volume Analysis (Volume)
    # df["Buying_Volume_Pivot"] = buying_volume_pivot(df["volume"])
    # df["Selling_Volume_Pivot"] = selling_volume_pivot(df["volume"])

    return df

if __name__ == "__main__" :
    from data import get_data

    df = get_data()
    df_with_indicators = indicators(df)
    print(df_with_indicators)
