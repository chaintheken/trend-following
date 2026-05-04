def trend(ema50 , ema150 , ema200) :
    if ema50 > ema150 > ema200 :
        return "Uptrend"
    elif ema50 < ema150 < ema200 :
        return "Downtrend"
    else :
        return "Sideway" 

def cross_ema_50(high , low , close , ema50) :
    if low < ema50 and close > ema50 :
        return "Cross up"
    elif high > ema50 and close < ema50 :
        return "Cross down"
    else :
        return "No Cross"

def rsi_strength(rsi , rsi_smoothing) :
    if rsi > rsi_smoothing :
        return "Upward strength"
    else : 
        return "Downward strength"

def stop_loss(close, entry_price, position_type, atr_multiplier, atr_at_entry):
    if position_type == 1 and close < entry_price - atr_multiplier * atr_at_entry:
        return "Exit"  # signal to close the position
    elif position_type == -1 and close > entry_price + atr_multiplier * atr_at_entry:
        return "Exit"
    else:
        return "Hold"

# Add position 
# Fix stoploss

def strategy(df) :
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

    position = 0 # 0 = flat, 1 = long, -1 = short   
    entry_price = 0
    entry_atr = 0
    volatility = 1.5 
    for i in range(len(df)) :
        if i < 200 or i == len(df) : # warmup, indicators aren't ready 
            continue 

        bar_open = df.iloc[i , df.columns.get_loc("open")]
        bar_high = df.iloc[i , df.columns.get_loc("high")]
        bar_low = df.iloc[i , df.columns.get_loc("low")]
        bar_close = df.iloc[i , df.columns.get_loc("close")]
        bar_volume = df.iloc[i , df.columns.get_loc("volume")]
        datetime = df.iloc[i , df.columns.get_loc("datetime")]

        ema10 = df.iloc[i , df.columns.get_loc("EMA10")]
        ema20 = df.iloc[i , df.columns.get_loc("EMA20")]
        ema50 = df.iloc[i , df.columns.get_loc("EMA50")]
        ema150 = df.iloc[i , df.columns.get_loc("EMA150")]
        ema200 = df.iloc[i , df.columns.get_loc("EMA200")]
        atr = df.iloc[i , df.columns.get_loc("ATR")]
        rsi = df.iloc[i , df.columns.get_loc("RSI")]
        rsi_smoothing = df.iloc[i , df.columns.get_loc("RSI_smoothing")]

        if position == 0 : 
            if trend(ema50 , ema150 , ema200) == "Uptrend" :
                if (cross_ema_50(bar_high , bar_low , bar_close , ema50) == "Cross up" 
                    and rsi_strength(rsi , rsi_smoothing) == "Upward strength") :
                    signals[i] = 1
                    position = 1
                    entry_price = df.iloc[i+1 , df.columns.get_loc("open")]
                    entry_atr = atr
                    
                    print(f"Long Signal Generated : {datetime} , market_price : {bar_close} , stoploss : {bar_close - 1.5 * atr}")
            elif trend(ema50 , ema150 , ema200) == "Downtrend" :
                if (cross_ema_50(bar_high , bar_low , bar_close , ema50) == "Cross down" 
                    and rsi_strength(rsi , rsi_smoothing) == "Downward strength") :
                    signals[i] = -1
                    position = -1
                    entry_price = df.iloc[i+1 , df.columns.get_loc("open")]
                    entry_atr = atr

                    print(f"Short Signal Generated : {datetime} , market_price : {bar_close} , stoploss : {bar_close + 1.5 * atr}")
        elif position == 1:
            if bar_low <= entry_price - volatility * entry_atr :
                signals[i] = -1
                position = 0
                exits[i] = True

                print(f"Stop loss from Long Position : {datetime} , market_price : {bar_close}")
                print()
            elif (df.iloc[i-1]["close"] < df.iloc[i-1]["EMA50"] 
                and df.iloc[i-2]["close"] < df.iloc[i-2]["EMA50"]
                and df.iloc[i-1]["close"] < df.iloc[i-2]["close"]):
                signals[i] = -1
                position = 0
                exits[i] = True

                print(f"Take Profit from Long Position : {datetime} , market_price : {bar_close}")
                print()
        else :
            if bar_high >= entry_price + volatility * entry_atr :
                signals[i] = 1 
                position = 0
                exits[i] = True
                
                print(f"Stop loss from Short Position : {datetime} , market_price : {bar_close}")
                print()
            elif (df.iloc[i-1]["close"] > df.iloc[i-1]["EMA50"] 
                and df.iloc[i-2]["close"] > df.iloc[i-2]["EMA50"]
                and df.iloc[i-1]["close"] > df.iloc[i-2]["close"]):
                signals[i] = 1
                position = 0
                exits[i] = True

                print(f"Take Profit from Short Position : {datetime} , market_price : {bar_close}")
                print()

        positions[i] = position

    df["signal"] = signals # 0 = Nothing happen  , +1 = Long signal , -1 = Short signal 
    df["exit"] = exits
    df["position"] = positions # 0 = flat, 1 = long, -1 = short   

    return df

if __name__ == "__main__" :
    from data import get_data
    from indicators import indicators

    df = get_data()
    df_with_indicators = indicators(df)
    df_signals = strategy(df_with_indicators)

    print(df_signals)