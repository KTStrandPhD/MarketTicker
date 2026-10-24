# MarketTicker TUI

**MarketTicker** is a real-time, terminal-based market monitoring dashboard built in Python. It provides live price quotes, 24-hour price changes, trading volume, and historical ASCII price charts across multiple asset classes—including Stocks, Precious Metals, Cryptocurrencies, and Forex pairs.

---

## Program Overview

MarketTicker runs directly in your terminal using a modern Text User Interface (TUI). It fetches financial data dynamically from Yahoo Finance and updates user viewports asynchronously to keep the UI smooth and responsive without blocking terminal rendering.

### Key Features
* **Multi-Asset Monitoring:** Cleanly categorized viewports for Stocks, Precious Metals, Crypto, and Forex.
* **Real-Time Market Data:** Live price quotes, percentage change color-coding (green/red), and total trading volumes.
* **Interactive Historical ASCII Charts:** Instant 1-year historical price graph rendered in pure Unicode/ASCII characters upon selecting any row.
* **Asynchronous Threading:** Network requests run on background worker threads using Textual `@work` decorators to prevent TUI freezing or lag.

---

## Prerequisites & Dependencies

MarketTicker requires **Python 3.10+**.

### Dependencies

| Package | Purpose |
| :--- | :--- |
| [`textual`](https://textual.textualize.io/) | TUI framework providing reactive layouts, widgets (`DataTable`, `Button`), and thread management. |
| [`yfinance`](https://pypi.org/project/yfinance/) | Financial data engine used to query market quotes and historical price charts. |
| [`pandas`](https://pandas.pydata.org/) | Data manipulation library used to structure historical chart time-series data. |

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/MarketTicker.git
cd MarketTicker

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install textual yfinance pandas
```

---

## Program Architecture & Logic

MarketTicker is designed with a modular architecture split across three primary modules:

```
MarketTicker/
├── MarketTicker      # Executable entry point bash script
└── src/
    ├── app.py          # Main Textual TUI Application logic & event handlers
    ├── data_fetcher.py # YFinance data extraction & ticker grouping
    └── chart.py        # ASCII/Unicode grid rendering engine
```

### 1. Data Retrieval (`data_fetcher.py`)
* **`MarketDataFetcher`**: Interacts with `yfinance.Tickers` to retrieve current session data (`regularMarketPrice`, `regularMarketChangePercent`, `regularMarketVolume`).
* **`get_1yr_history(symbol)`**: Pulls 1-year historical closing prices (`1y` period, `1d` interval) for chart rendering. Handles currency fallbacks and data sanitization.

### 2. UI & Event Loop (`app.py`)
* **Custom Navigation Bar:** Uses active `Button` controls attached to category listeners.
* **Asynchronous Workers (`@work(thread=True)`):** Ensures network queries run off the main event thread, posting UI updates back via `self.call_from_thread()`.
* **Single Shared `DataTable`:** Dynamically updates table rows upon category selection to prevent viewport layout pass issues.

### 3. Chart Engine (`chart.py`)
* **`TerminalChart.render_ascii_chart()`**: Converts raw floating-point price series into a discrete 2D ASCII grid by normalizing price ranges against terminal height (`H`) and width (`W`). Displays clear `High` and `Low` price bounds on the render axis.

---

## Usage Instructions

### Launching the Application

Run the executable script directly from the root directory:

```bash
./MarketTicker
```

Or execute via Python:

```bash
python3 src/app.py
```

---

### Controls & Navigation

| Action | Control / Keybinding |
| :--- | :--- |
| **Switch Categories** | **Click** any category button at the top (`Stocks`, `Precious Metals`, `Crypto`, `Forex`) OR press **`Tab`** / **`Shift+Tab`** to cycle focus across category buttons and hit **`Enter`** / **`Space`**. |
| **Navigate Ticker Rows** | Use **`Up Arrow`** / **`Down Arrow`** keys or click any row directly. |
| **Display 1-Year Chart** | Press **`Enter`** on any highlighted ticker row (or click the row) to fetch and render its historical chart in the lower viewport. |
| **Refresh Table Data** | Press **`r`** to force a live data refresh for the current category. |
| **Quit Application** | Press **`q`** or **`Ctrl+C`** to safely exit. |

---

## Troubleshooting

* **Blank Tables on Launch:** Ensure your environment has internet connectivity to reach Yahoo Finance endpoint APIs.
* **Terminal Display Artifacts:** Ensure your terminal emulator supports UTF-8 and standard ANSI color codes for optimal rendering.