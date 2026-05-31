# Constant over string
TREND_UP = 1
TREND_DOWN = -1
SIDEWAY = 0 

LONG = 1
SHORT = -1

CROSS_UP = 1
CROSS_DOWN = -1
NO_CROSS = 0 

MOMENTUM_UP = 1
MOMENTUM_DOWN = -1

WARMUP = 200

# Helpers functions
def trend(ema50 , ema150 , ema200) :
    if ema50 > ema150 > ema200 :
        return TREND_UP
    elif ema50 < ema150 < ema200 :
        return TREND_DOWN
    else :
        return SIDEWAY

def cross_ema_50(high , low , close , ema50) :
    # Technical Gap in Equity
    if low < ema50 and close > ema50 :
        return CROSS_UP
    elif high > ema50 and close < ema50 :
        return CROSS_DOWN
    else :
        return NO_CROSS

def rsi_strength(rsi , rsi_smoothing) :
    if rsi > rsi_smoothing :
        return MOMENTUM_UP
    else : 
        return MOMENTUM_DOWN

def consecutive_closing(closing_period=2) :
    pass

# Decision functions 
def check_entry(row , atr_multiplier , next_open) -> dict :
    # Price
    bar_high = row["high"]
    bar_low = row["low"]
    bar_close = row["close"]
    bar_datetime = row["datetime"]
    
    # Indicators
    ema50 = row["EMA50"]
    ema150 = row["EMA150"]
    ema200 = row["EMA200"]
    atr = row["ATR"]
    rsi = row["RSI"]
    rsi_smoothing = row["RSI_smoothing"]

    if trend(ema50 , ema150 , ema200) == TREND_UP :
        if (cross_ema_50(bar_high , bar_low , bar_close , ema50) == CROSS_UP
            and rsi_strength(rsi , rsi_smoothing) == MOMENTUM_UP) :
            return {
                "type" : "Long" , 
                "datetime" : bar_datetime ,
                "entry_price" : next_open ,
                "stop_price" :  next_open - atr_multiplier * atr,
                "entry_atr" : atr
            }
    elif trend(ema50 , ema150 , ema200) == TREND_DOWN :
        if (cross_ema_50(bar_high , bar_low , bar_close , ema50) == CROSS_DOWN 
            and rsi_strength(rsi , rsi_smoothing) == MOMENTUM_DOWN) :
            return {
                "type" : "Short" , 
                "datetime" : bar_datetime ,
                "entry_price" : next_open ,
                "stop_price" :  next_open + atr_multiplier * atr,
                "entry_atr" : atr
            }
    return None

def check_exit(row , prev1 , prev2 , position_info) -> str:
    # Price
    bar_high = row["high"]
    bar_low = row["low"]
    bar_datetime = row["datetime"]    
    # Position
    stop_price = position_info["stop_price"]

    if position_info["type"] == "Long":
        if bar_low <= stop_price :
            return f"{bar_datetime} : Stop_loss from Long"
        if (prev1["close"] < prev1["EMA50"]
            and prev2["close"] < prev2["EMA50"]
            and prev1["close"] < prev2["close"]):
            return f"{bar_datetime} : Take_profit from Long"
    else :
        if bar_high >= stop_price :
            return f"{bar_datetime} : Stop_loss from Short"
        if (prev1["close"] > prev1["EMA50"]
            and prev2["close"] > prev2["EMA50"]
            and prev1["close"] > prev2["close"]) :
            return f"{bar_datetime} : Take_profit from Short"

def strategy(df , atr_multiplier=1.5 , verbose=False) :
    # Generate Long/Short signal
    # Buy if EMA 50 > 150 > 200, and the price's low is under EMA 50 and closing is above EMA 100 and 
    # RSI is more than the smoothing version stop loss under 2 ATR and take profits all if the price is officially under EMA 50
    # (under EMA 50 - the price is closing under EMA 50 for 2 consecutive candles, if it's not then it's not under EMA 50 yet )
    # breakeven if the price goes above 10 percent.
    # P.S. This is briefly what I trade (50%) and shorting is the opposite. This strategy works well for growth stock under up/down trend (I test only equity)
    df = df.copy()
    signals = [0] * len(df) # 0 = Nothing happen  , +1 = Long signal , -1 = Short signal 
    exits = [False] * len(df)
    positions = [0] * len(df)
    entry_price = [0] * len(df)
    stop_price = [0] * len(df)
    exit_price = [0] * len(df)
    position_info = None # Trading once per asset
    
    for i in range(WARMUP , len(df) - 1) :
        row = df.iloc[i]
        prev1 = df.iloc[i-1]
        prev2 = df.iloc[i-2]
        next_open = df.iloc[i+1]["open"]

        if position_info is None :
            position_info = check_entry(row , atr_multiplier , next_open)
            if position_info is not None : 
                signals[i] = 1 if position_info["type"] == "Long" else -1
                stop_price[i] = position_info["stop_price"]
                entry_price[i] = position_info["entry_price"]
                if verbose : print(f"{position_info["datetime"]} : {position_info["type"]} signal generated at {position_info["entry_price"]} and stop at {position_info["stop_price"]}")
        else : 
            exit_reason = check_exit(row, prev1, prev2, position_info)
            if exit_reason:
                signals[i] = -1 if position_info["type"] == "Long" else 1
                exits[i] = True
                exit_price[i] = next_open
                position_info = None

                if verbose : 
                    print(f"{exit_reason} at {row["close"]}\n")

        if position_info is not None :
            positions[i] = 1 if position_info["type"] == "Long" else -1

    df["signal"] = signals # 0 = Nothing happen  , +1 = Long signal , -1 = Short signal 
    df["exit"] = exits
    df["position"] = positions # 0 = flat, 1 = long, -1 = short   
    df["entry_price"] = entry_price
    df["stop_price"] = stop_price
    df["exit_price"] = exit_price

    return df

if __name__ == "__main__" :
    from data import get_data
    from indicators import indicators

    df = get_data()
    df_with_indicators = indicators(df)
    df_signals = strategy(df_with_indicators , verbose=True)

    print(df_signals)