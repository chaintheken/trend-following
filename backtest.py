from data import get_data
from indicators import indicators
from strategies import strategy
from metric import total_return , maximum_drawdown , sharpe_ratio , profit_factor , winrate

def backtest(df, starting_capital=10000, risk_per_trade=0.01 , fee=0.001 , leverage=1):
    """
    df has: open, high, low, close, signal, position, exit
    Returns: df with equity curve, list of completed trades
    """
    equity = starting_capital
    equity_curve = []
    trades = []

    in_position = None
    entry_price = None
    stop_price = None
    exit_price = None
    position_size = None 
    for i in range(len(df)):
        # Long/Short based on signals
        # Equity curve based on asset you hold
        row = df.iloc[i]

        if in_position is None and row["signal"] != 0 and not row["exit"]:
            in_position = "Long" if row["signal"] == 1 else "Short"
            entry_price = row["entry_price"]
            stop_price = row["stop_price"]
            position_size = (equity * risk_per_trade) / abs(entry_price - stop_price)

            # deducted fee here.
            equity -= position_size * entry_price * fee

        elif in_position is not None and row["exit"] :
            exit_price = row["exit_price"]

            if in_position == "Long" :
                trade_return = (exit_price - entry_price) / entry_price
            else :
                trade_return = (entry_price - exit_price) / entry_price

            # gain/lose from the trade
            equity += trade_return * position_size * entry_price
            
            # deducted fee here
            equity -= position_size * exit_price * fee

            print(f"Equity after trade {len(trades)} : {equity}")

            trades.append({
                "entry_price": entry_price,
                "stop_price": stop_price,
                "exit_price" : exit_price,
                "direction": in_position,
                "return": trade_return,
                "position_size": position_size,
            })
            
            in_position = None 
            entry_price = None
            stop_price = None
            exit_price = None
            position_size = None

        equity_curve.append(equity)
    
    df["equity"] = equity_curve
    return df, trades

if __name__ == "__main__":
    starting_capital = 10000

    atr_multiplier = [1.25 , 1.5 , 1.75 , 2 , 2.5 , 3]
    
    for atr in atr_multiplier :
        print()
        print(f"System with ATR = {atr}")
        df = get_data()
        df = indicators(df)
        df = strategy(df , atr_multiplier=atr)
        df, trades = backtest(df , starting_capital=starting_capital)

        daily_returns = df["equity"].pct_change().dropna()
        final_equity = df['equity'].iloc[-1]
        print(df.tail())
        print(f"Final equity: {final_equity}")
        print(f"Total trades: {trades}")
        print(f"Total return : {total_return(starting_capital , final_equity) * 100} %")
        print(f"Maximum drawdown (percentage): {maximum_drawdown(df) * 100} %")
        print(f"Sharpe ratio (annualized) : {sharpe_ratio(daily_returns)}")
        print(f"Winrate : {winrate(trades) * 100} %")
        print(f"Profit factor : {profit_factor(trades)}")
        