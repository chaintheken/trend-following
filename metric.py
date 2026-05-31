def total_return(starting_capital , ending_capital):
    return (ending_capital - starting_capital) / starting_capital

def maximum_drawdown(df) :
    """Maximum Drawdown"""
    max_drawdown = 0 
    drawdown = 0
    highest_equity = df.iloc[0]["equity"]
    for i in range(len(df)) :
        equity = df.iloc[i , df.columns.get_loc("equity")]

        if equity > highest_equity :
            drawdown = 0 
            highest_equity = equity
        else :
            drawdown = 1 - equity / highest_equity
            max_drawdown = drawdown if drawdown > max_drawdown else max_drawdown
    return max_drawdown

def sharpe_ratio(daily_returns , risk_free_rate=0.02 , period_per_year=365) :
    """Annualized Sharpe ratio from a series of daily returns."""
    mean_daily = daily_returns.mean()
    std_daily = daily_returns.std()
    rfr_daily = risk_free_rate / period_per_year
    daily_sharpe = (mean_daily - rfr_daily) / std_daily

    return daily_sharpe * (period_per_year ** 0.5)
        
def winrate(trades) :
    winning_trade = 0
    for i in range(len(trades)) :
        winning_trade += 1 if trades[i]["return"] > 0 else 0

    return winning_trade / len(trades)

def profit_factor(trades) :
    gross_profit = 0 
    gross_lose = 0 
    for i in range(len(trades)) :
        entry_price = trades[i]["entry_price"]
        trade_return = trades[i]["return"]
        position_size = trades[i]["position_size"]

        if trade_return > 0 : 
            gross_profit += entry_price * trade_return * position_size
        else :
            gross_lose += entry_price * (-trade_return) * position_size
    
    return gross_profit / gross_lose
        
def expectancy(winrate , risk_to_reward) :
    return (winrate * risk_to_reward) - (1 - winrate)

