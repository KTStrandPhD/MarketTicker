import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from chart import TerminalChart
from data_fetcher import TICKER_GROUPS, MarketDataFetcher
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Static


class MarketTickerApp(App):
  """A multi-asset terminal ticker with real-time stats and historical chart view."""

  CSS = """
    Screen {
        layout: vertical;
        background: $background;
    }
    #nav-bar {
        dock: top;
        height: 3;
        background: $surface;
        align: center middle;
        padding: 0 1;
    }
    .tab-btn {
        margin: 0 1;
        min-width: 15;
    }
    .tab-btn.-active {
        background: $accent;
        color: $text;
        text-style: bold;
    }
    #content-area {
        height: 1fr;
        layout: vertical;
        padding: 1;
    }
    DataTable {
        height: 100%;
        width: 100%;
    }
    #chart-container {
        height: 15;
        border-top: heavy $accent;
        padding: 0 1;
        background: $surface;
    }
    #chart-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    #chart-view {
        color: $text;
    }
    """

  BINDINGS = [
      ("r", "refresh_current_tab", "Refresh Table"),
      ("q", "quit", "Quit"),
  ]

  def __init__(self):
    super().__init__()
    self.current_category = "Stocks"

  def compose(self) -> ComposeResult:
    yield Header(show_clock=True)

    with Horizontal(id="nav-bar"):
      for cat in TICKER_GROUPS.keys():
        slug = cat.lower().replace(" ", "-")
        is_active = cat == "Stocks"
        btn_class = "tab-btn -active" if is_active else "tab-btn"
        yield Button(cat, id=f"btn-{slug}", classes=btn_class)

    with Vertical(id="content-area"):
      yield DataTable(id="main-table")

    with Container(id="chart-container"):
      yield Static("Select a ticker to display 1-year chart", id="chart-title")
      yield Static("", id="chart-view")

    yield Footer()

  def on_mount(self) -> None:
    self.fetcher = MarketDataFetcher()
    table = self.query_one("#main-table", DataTable)
    table.add_columns("Symbol", "Price ($)", "24h % Change", "24h Volume")
    table.cursor_type = "row"
    self.load_category("Stocks")

  def on_button_pressed(self, event: Button.Pressed) -> None:
    button_id = event.button.id
    if not button_id or not button_id.startswith("btn-"):
      return

    slug = button_id.replace("btn-", "")
    category_name = None
    for cat in TICKER_GROUPS.keys():
      if cat.lower().replace(" ", "-") == slug:
        category_name = cat
        break

    if category_name:
      self.current_category = category_name

      for btn in self.query(".tab-btn"):
        if btn.id == button_id:
          btn.add_class("-active")
        else:
          btn.remove_class("-active")

      self.load_category(category_name)

  def action_refresh_current_tab(self) -> None:
    self.load_category(self.current_category)

  def load_category(self, category: str) -> None:
    slug = category.lower().replace(" ", "-")
    self.fetch_and_populate(category, slug)

  @work(exclusive=True, thread=True)
  def fetch_and_populate(self, category: str, slug: str) -> None:
    table_id = "#main-table"
    try:
      table = self.query_one(table_id, DataTable)
    except Exception as e:
      logging.error(f"Could not find table {table_id}: {e}")
      return

    tickers = TICKER_GROUPS.get(category, [])
    data = self.fetcher.get_summary_data(tickers)

    def update_ui(tbl=table, rows=data):
      try:
        tbl.clear(columns=False)

        if not rows:
          tbl.add_row("NO DATA", "0.00", "0.00%", "0")
        else:
          # Specific sub-penny/fractional crypto assets requiring 6 decimal precision
          six_decimal_tokens = {"XRP-USD", "PYTH-USD", "XNO-USD"}

          for row in rows:
            sym = str(row["symbol"])
            pct = row["change_pct"]
            pct_str = f"+{pct:.2f}%" if pct >= 0 else f"{pct:.2f}%"

            if pct > 0:
              styled_pct = f"[green]{pct_str}[/green]"
            elif pct < 0:
              styled_pct = f"[red]{pct_str}[/red]"
            else:
              styled_pct = pct_str

            formatted_vol = (
                f"{int(row['volume']):,}" if row["volume"] > 0 else "N/A"
            )

            # Apply 6 decimal places for XRP, PYTH, and XNO, 2 for everything else
            if sym in six_decimal_tokens:
              formatted_price = f"{row['price']:,.6f}"
            else:
              formatted_price = f"{row['price']:,.2f}"

            tbl.add_row(sym, formatted_price, styled_pct, formatted_vol)

        tbl.refresh()
      except Exception as ex:
        logging.error(f"Error updating UI table: {ex}", exc_info=True)

    self.call_from_thread(update_ui)

  def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    row_data = event.data_table.get_row(event.row_key)
    if not row_data:
      return

    symbol = str(row_data[0])
    if symbol == "NO DATA":
      return

    chart_title = self.query_one("#chart-title", Static)
    chart_view = self.query_one("#chart-view", Static)

    chart_title.update(f"1-Year Price Chart: {symbol}")
    chart_view.update("Fetching historical data...")

    self.fetch_and_render_chart(symbol, chart_view)

  @work(exclusive=True, thread=True)
  def fetch_and_render_chart(self, symbol: str, chart_view: Static) -> None:
    history = self.fetcher.get_1yr_history(symbol)
    ascii_graph = TerminalChart.render_ascii_chart(history, height=8, width=70)
    self.call_from_thread(chart_view.update, ascii_graph)


if __name__ == "__main__":
  app = MarketTickerApp()
  app.run()
