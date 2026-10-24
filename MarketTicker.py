#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src/ to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app import MarketTickerApp

if __name__ == "__main__":
  app = MarketTickerApp()
  app.run()
