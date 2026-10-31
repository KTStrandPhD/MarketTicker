import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from ai_summarizer import MarketAISummarizer

def main():
    print("Initializing AI Sentiment Test...")
    symbol = "BTC-USD"
    print(f"Fetching news and analyzing sentiment for {symbol}...")
    
    sentiment = MarketAISummarizer.analyze_ticker_sentiment(symbol)
    
    print("\n--- AI Sentiment Result ---")
    print(sentiment)
    print("---------------------------\n")

if __name__ == "__main__":
    main()
