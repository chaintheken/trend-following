import ccxt
import pandas as pd

exchange = ccxt.binance()

def get_data() :
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1d')
    df = pd.DataFrame(ohlcv)
    df.columns = ["timestamp" , "open" , "high" , "low" , "close" , "volume"] 
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df

# def get_data(symbol="BTC/USDT", timeframe="1d", refresh=False):
#     cache_path = f"data/{symbol.replace('/', '_')}_{timeframe}.parquet"
#     if not refresh and os.path.exists(cache_path):
#         return pd.read_parquet(cache_path)
#     df = fetch_from_binance(symbol, timeframe)
#     df.to_parquet(cache_path)
#     return df

if __name__ == "__main__" :
    df = get_data()
    print(df)
