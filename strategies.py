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

def strategy(df) :
    # Generate Long/Short signal
    # Buy if EMA 50 > 150 > 200, and the price's low is under EMA 50 and closing is above EMA 100 and 
    # RSI is more than the smoothing version stop loss under 2 ATR and take profits all if the price is officially under EMA 50
    # (under EMA 50 - the price is closing under EMA 50 for 2 consecutive candles, if it's not then it's not under EMA 50 yet )
    # breakeven if the price goes above 10 percent.
    # P.S. This is briefly what I trade (50%) and shorting is the opposite. This strategy works well for growth stock under up/down trend (I test only equity)

    df = df.copy()
    df["signal"] = 0 # 0 = No signal , 1 = Has Signal
    position = 0  # 0 = flat, 1 = long, -1 = short
    entry_price = 0
    
    for i in range(len(df)) :
        if i < 200 or i == len(df) : # warmup, indicators aren't ready 
            continue 

        open = df.iloc[i]["open"]
        high = df.iloc[i]["high"]
        low = df.iloc[i]["low"]
        close = df.iloc[i]["close"]
        volume = df.iloc[i]["volume"]

        ema10 = df.iloc[i]["EMA10"]
        ema20 = df.iloc[i]["EMA20"]
        ema50 = df.iloc[i]["EMA50"]
        ema150 = df.iloc[i]["EMA150"]
        ema200 = df.iloc[i]["EMA200"]
        atr = df.iloc[i]["ATR"]
        rsi = df.iloc[i]["RSI"]
        rsi_smoothing = df.iloc[i]["RSI_smoothing"]

        if position == 0 : 
            if trend(ema50 , ema150 , ema200) == "Uptrend" :
                if (cross_ema_50(high , low , close , ema50) == "Cross up" 
                    and rsi_strength(rsi , rsi_smoothing) == "Upward strength") :
                    df.loc[df.index[i] , "signal"] = 1
                    position = 1
                    entry_price = df.iloc[i+1]["open"]
                    print(f"Long Signal Generated : {df.iloc[i]["datetime"]} , market_price : {df.iloc[i]["close"]} , stoploss : {close - 1.5 * atr}")
            elif trend(ema50 , ema150 , ema200) == "Downtrend" :
                if (cross_ema_50(high , low , close , ema50) == "Cross down" 
                    and rsi_strength(rsi , rsi_smoothing) == "Downward strength") :
                    df.loc[df.index[i] , "signal"] = -1
                    position = -1
                    entry_price = df.iloc[i+1]["open"]
                    print(f"Short Signal Generated : {df.iloc[i]["datetime"]} , market_price : {df.iloc[i]["close"]}")
        elif position == 1:
            if stop_loss(close , entry_price , position , 1.5 , atr) == "Exit":
                df.loc[df.index[i] , "signal"] = 0
                position = 0
                entry_price = 0
                print(f"Stop loss from Long Position : {df.iloc[i]["datetime"]} , market_price : {df.iloc[i]["close"]}")
                print()
            
            elif (df.iloc[i-1]["close"] < df.iloc[i-1]["EMA50"] 
                and df.iloc[i-2]["close"] < df.iloc[i-2]["EMA50"]
                and df.iloc[i-1]["close"] < df.iloc[i-2]["close"]):
                df.loc[df.index[i] , "signal"] = 0
                position = 0
                entry_price = 0
                print(f"Take Profit from Long Position : {df.iloc[i]["datetime"]} , market_price : {df.iloc[i]["close"]}")
                print()
        else :
            if stop_loss(close , entry_price , position , 1.5 , atr) == "Exit":
                df.loc[df.index[i] , "signal"] = 0 
                position = 0
                entry_price = 0
                print(f"Stop loss from Short Position : {df.iloc[i]["datetime"]} , market_price : {df.iloc[i]["close"]}")
                print()
            
            elif (df.iloc[i-1]["close"] > df.iloc[i-1]["EMA50"] 
                and df.iloc[i-2]["close"] > df.iloc[i-2]["EMA50"]
                and df.iloc[i-1]["close"] > df.iloc[i-2]["close"]):
                df.loc[df.index[i] , "signal"] = 0 
                position = 0
                entry_price = 0
                print(f"Take Profit from Short Position : {df.iloc[i]["datetime"]} , market_price : {df.iloc[i]["close"]}")
                print()
    return df

if __name__ == "__main__" :
    from data import get_data
    from indicators import indicators

    df = get_data()
    df_with_indicators = indicators(df)
    df_signals = strategy(df_with_indicators)

    print(df_signals)