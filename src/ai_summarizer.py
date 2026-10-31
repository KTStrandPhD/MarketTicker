import os
import logging
import requests
from threading import Lock
from dotenv import load_dotenv

load_dotenv()


class MarketAISummarizer:
  _cache = {}
  _lock = Lock()

  @staticmethod
  def _call_gemini(symbol: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
      raise ValueError("GEMINI_API_KEY not found")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
    prompt = (
        f"Provide a concise, 2-sentence general market overview and sentiment analysis "
        f"for financial asset/ticker {symbol} (e.g., Bullish, Bearish, or Neutral) "
        "highlighting typical recent market dynamics or structural outlook."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=payload, timeout=5.0)

    if response.status_code == 200:
      data = response.json()
      return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    response.raise_for_status()

  @staticmethod
  def _call_openrouter_fallback(symbol: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
      logging.warning("OPENROUTER_API_KEY not found in environment.")
      return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/KTStrandPhD/MarketTicker",
        "X-Title": "MarketTicker"
    }
    prompt = (
        f"Provide a concise, 2-sentence general market overview and sentiment analysis "
        f"for financial asset/ticker {symbol} (e.g., Bullish, Bearish, or Neutral) "
        "highlighting typical recent market dynamics or structural outlook."
    )
    payload = {
        # Use OpenRouter's official free auto-router model
        "model": "openrouter/free", 
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, json=payload, headers=headers, timeout=5.0)
    if response.status_code == 200:
      data = response.json()
      return data["choices"][0]["message"]["content"].strip()
    
    logging.error(f"OpenRouter error status {response.status_code}: {response.text}")
    return None

  @staticmethod
  def analyze_ticker_sentiment(symbol: str) -> str:
    """Generates sentiment using Gemini, falling back to OpenRouter free auto-router."""
    
    with MarketAISummarizer._lock:
      if symbol in MarketAISummarizer._cache:
        return f"[green](Cached)[/green] {MarketAISummarizer._cache[symbol]}"

    cleaned_text = None
    last_status = 0

    # Try Primary: Gemini
    try:
      cleaned_text = MarketAISummarizer._call_gemini(symbol)
    except requests.exceptions.HTTPError as e:
      last_status = e.response.status_code if e.response is not None else 0
      logging.warning(f"Gemini failed with status {last_status}. Attempting OpenRouter fallback...")
    except Exception as e:
      logging.warning(f"Gemini failed with error: {e}. Attempting OpenRouter fallback...")

    # If Gemini failed (429, 503, timeout, etc.), try OpenRouter fallback
    if not cleaned_text:
      try:
        cleaned_text = MarketAISummarizer._call_openrouter_fallback(symbol)
      except Exception as fallback_err:
        logging.error(f"OpenRouter fallback exception: {fallback_err}")

    # If both failed, return descriptive status
    if not cleaned_text:
      if last_status == 429:
        return "Rate limit reached (429) on Gemini and OpenRouter fallback failed. Please verify API quotas."
      elif last_status == 503:
        return "AI model experiencing high demand (503). Please try again shortly."
      else:
        return f"API error ({last_status if last_status else 'Network'}): Unable to fetch sentiment."

    if cleaned_text:
      with MarketAISummarizer._lock:
        MarketAISummarizer._cache[symbol] = cleaned_text
      return cleaned_text

    return "Sentiment analysis temporarily unavailable."
