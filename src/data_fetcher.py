#Get chart data

import logging
import pandas as pd
import yfinance as yf

# Configure logging to write to a file in the project folder
logging.basicConfig(
    filename='ticker_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

# Ticker groups as originally defined in your file
TICKER_GROUPS = {
    'Stocks': [
        'AAPL',
        'MSFT',
        'NVDA',
        'GOOGL',
        'AMZN',
        'TSLA',
        'META',
        'BRK-B',
        'SPY',
        'QQQ',
    ],
    'Precious Metals': [
        'GC=F',
        'SI=F',
        'PL=F',
        'PA=F',
    ],  # Gold, Silver, Platinum, Palladium
    'Crypto': [
        'BTC-USD',
        'ETH-USD',
        'SOL-USD',
        'XRP-USD',
        'PYTH-USD',
        'XNO-USD',
        'S-USD',
    ],
    'Forex': [
        'EURUSD=X',
        'GBPUSD=X',
        'USDJPY=X',
        'AUDUSD=X',
        'USDCAD=X',
        'USDCHF=X',
    ],
}


class MarketDataFetcher:

  @staticmethod
  def get_summary_data(tickers: list[str]) -> list[dict]:
    """Fetches real-time price, 24h % change, and 24h volume with file logging."""
    results = []
    logging.info(f'Starting fetch for tickers: {tickers}')
    for symbol in tickers:
      try:
        t = yf.Ticker(symbol)
        hist = t.history(period='2d')

        if hist.empty or 'Close' not in hist.columns:
          logging.warning(f'Empty history or missing Close for {symbol}')
          continue

        closes = hist['Close'].dropna()
        if len(closes) >= 2:
          prev_close = closes.iloc[-2]
          curr_price = closes.iloc[-1]
          pct_change = ((curr_price - prev_close) / prev_close) * 100
        elif len(closes) == 1:
          curr_price = closes.iloc[-1]
          pct_change = 0.0
        else:
          continue

        volume = 0
        if 'Volume' in hist.columns:
          vol_series = hist['Volume'].dropna()
          if not vol_series.empty:
            volume = int(vol_series.iloc[-1])

        results.append({
            'symbol': symbol,
            'price': float(curr_price),
            'change_pct': float(pct_change),
            'volume': volume,
        })
        logging.info(f'Successfully fetched {symbol}: {curr_price}')
      except Exception as e:
        logging.error(f'Failed fetching {symbol}: {e}', exc_info=True)

    logging.info(f'Finished fetch. Returning {len(results)} items.')
    return results

  @staticmethod
  def get_1yr_history(symbol: str) -> pd.Series:
    """Fetches 1-year historical closing prices for charting."""
    try:
      logging.info(f'Fetching 1yr history for {symbol}')
      t = yf.Ticker(symbol)
      df = t.history(period='1y')
      if not df.empty and 'Close' in df.columns:
        return df['Close'].dropna()
    except Exception as e:
      logging.error(f'Failed 1yr history for {symbol}: {e}', exc_info=True)
    return pd.Series(dtype=float)
