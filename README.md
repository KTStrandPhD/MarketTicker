# MarketTicker TUI

**MarketTicker** is a real-time, terminal-based market monitoring dashboard built in Python. It provides live price quotes, 24-hour price changes, trading volume, historical ASCII price charts, and AI-driven market intelligence across multiple asset classes—including Stocks, Precious Metals, Cryptocurrencies, and Forex pairs.

---

## Program Overview

MarketTicker runs directly in your terminal using a modern Text User Interface (TUI). It fetches financial data dynamically from Yahoo Finance and leverages asynchronous background worker threads to keep the UI smooth and responsive without blocking terminal rendering.

### Key Features
* **Multi-Asset Monitoring:** Cleanly categorized viewports for Stocks, Precious Metals, Crypto, and Forex.
* **Real-Time Market Data:** Live price quotes, percentage change color-coding (green/red), and total trading volumes.
* **Interactive Historical ASCII Charts:** Instant 1-year historical price graph rendered in pure Unicode/ASCII characters upon highlighting any row.
* **AI Market Intelligence (Gemini + OpenRouter):** Contextual 2-sentence sentiment summaries for any selected asset.
* **Resilient Network Strategy:** Direct REST calls with hard 5-second timeout guards to prevent socket hangs during high-demand (503) or rate-limit (429) events.
* **Thread-Safe In-Memory Caching:** Instant retrieval for previously viewed assets by caching only successful status 200 responses under a thread lock.
* **Zero-Cost Fallback Architecture:** Seamless failover to OpenRouter's free auto-router (`openrouter/free`) whenever Gemini encounters congestion or rate limits.
* **Asynchronous Background Execution:** Non-blocking background worker threads (`ThreadPoolExecutor` via Textual `@work`) ensure rapid ticker switching never stutters the UI event loop.

---

## Prerequisites & Dependencies

MarketTicker requires **Python 3.10+**.

### Dependencies

| Package | Purpose |
| :--- | :--- |
| [`textual`](https://textual.textualize.io/) | TUI framework providing reactive layouts, widgets (`DataTable`, `Button`), and thread management. |
| [`yfinance`](https://pypi.org/project/yfinance/) | Financial data engine used to query market quotes and historical price charts. |
| [`pandas`](https://pandas.pydata.org/) | Data manipulation library used to structure historical chart time-series data. |
| [`requests`](https://pypi.org/project/requests/) | HTTP client library used for direct REST communications with Gemini and OpenRouter APIs. |
| [`python-dotenv`](https://pypi.org/project/python-dotenv/) | Environment variable loader for managing secure API keys. |

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/MarketTicker.git
cd MarketTicker

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install textual yfinance pandas requests python-dotenv
```

### Environment Configuration

Create a `.env` file in the root directory to configure your API keys:

```env
GEMINI_API_KEY="your_gemini_api_key_here"
OPENROUTER_API_KEY="your_openrouter_key_here"
```

---

## Program Architecture & Logic

MarketTicker is designed with a modular architecture split across four primary modules:

```
MarketTicker/
├── MarketTicker      # Executable entry point bash script
└── src/
    ├── app.py          # Main Textual TUI Application logic & event handlers
    ├── data_fetcher.py # YFinance data extraction & ticker grouping
    ├── chart.py        # ASCII/Unicode grid rendering engine
    └── ai_summarizer.py# AI sentiment analysis, caching, and fallback routing
```

### 1. Data Retrieval (`data_fetcher.py`)
* **`MarketDataFetcher`**: Interacts with `yfinance.Tickers` to retrieve current session data (`regularMarketPrice`, `regularMarketChangePercent`, `regularMarketVolume`).
* **`get_1yr_history(symbol)`**: Pulls 1-year historical closing prices (`1y` period, `1d` interval) for chart rendering.

### 2. AI Intelligence Engine (`ai_summarizer.py`)
* **`MarketAISummarizer`**: Manages direct REST communication with the Gemini API (`gemini-3.8-flash`) using strict 5-second timeouts to avoid socket hangs.
* **Thread-Safe Caching:** Utilizes an in-memory dictionary protected by a `threading.Lock` to cache successful responses (`200 OK`), ensuring zero redundant network calls for previously queried assets.
* **Automatic Fallback Routing:** Intercepts HTTP status codes (`429` rate limits or `503` high demand) and seamlessly routes queries to OpenRouter's free tier (`openrouter/free`).

### 3. UI & Asynchronous Event Loop (`app.py`)
* **`on_data_table_row_highlighted`**: Triggers asynchronous chart rendering and AI intelligence updates immediately when navigating up and down table rows.
* **Asynchronous Workers (`@work(exclusive=True, thread=True)`):** Ensures network queries and AI sentiment fetching run on background worker threads, posting UI updates back via `self.call_from_thread()` to prevent event loop blocking.

### 4. Chart Engine (`chart.py`)
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
| **Navigate Ticker Rows** | Use **`Up Arrow`** / **`Down Arrow`** keys or click any row directly. Triggering a highlight automatically fetches its 1-year chart and AI market intelligence asynchronously. |
| **Refresh Table Data** | Press **`r`** to force a live data refresh for the current category. |
| **Quit Application** | Press **`q`** or **`Ctrl+C`** to safely exit. |

---

## Troubleshooting

* **Blank Tables on Launch:** Ensure your environment has internet connectivity to reach Yahoo Finance endpoint APIs.
* **AI Intelligence Errors:** Verify that your `GEMINI_API_KEY` and `OPENROUTER_API_KEY` are properly populated in your `.env` file. If Gemini experiences high traffic (`503`) or rate limits (`429`), the app will automatically attempt failover to OpenRouter.
* **Terminal Display Artifacts:** Ensure your terminal emulator supports UTF-8 and standard ANSI color codes for optimal rendering.