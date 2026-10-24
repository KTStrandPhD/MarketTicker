import numpy as np
import pandas as pd


class TerminalChart:

  @staticmethod
  def render_ascii_chart(
      series: pd.Series, height: int = 12, width: int = 60
  ) -> str:
    """Converts a 1-year price series into a scaled ASCII character grid."""
    if series.empty:
      return 'No historical data available.'

    # Downsample series to fit width
    prices = series.values
    if len(prices) > width:
      indices = np.linspace(0, len(prices) - 1, width, dtype=int)
      prices = prices[indices]

    min_p, max_p = np.min(prices), np.max(prices)
    if min_p == max_p:
      return '-' * width

    # Scale values to grid height
    scaled = (prices - min_p) / (max_p - min_p) * (height - 1)
    grid = [[' ' for _ in range(len(prices))] for _ in range(height)]

    for col, val in enumerate(scaled):
      row = height - 1 - int(round(val))
      grid[row][col] = '█'

    # Format output with min/max labels
    lines = [''.join(row) for row in grid]
    chart_str = f'High: {max_p:.2f}\n' + '\n'.join(lines) + f'\nLow:  {min_p:.2f}'
    return chart_str
