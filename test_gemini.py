# test_gemini.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def test_api():
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    return

  print("Sending direct request to Gemini API...")
  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
  
  prompt = "in 2 sentences, why is the sky blue?"
  payload = {
      "contents": [{
          "parts": [{"text": prompt}]
      }]
  }

  try:
    # Hard 5-second timeout guarantees it cannot hang indefinitely
    response = requests.post(url, json=payload, timeout=5.0)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
      data = response.json()
      text = data["candidates"][0]["content"]["parts"][0]["text"]
      print("\n--- Gemini Response ---")
      print(text.strip())
    else:
      print(f"API Error: {response.text}")

  except requests.exceptions.Timeout:
    print("Request timed out after 5 seconds.")
  except Exception as e:
    print(f"An error occurred: {e}")


if __name__ == "__main__":
  test_api()
