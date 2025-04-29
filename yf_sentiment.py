import yfinance as yf
from bs4 import BeautifulSoup
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import pandas as pd

def get_yahoo_finance_news(ticker_symbol):

   # Fetch news articles for a given stock ticker using yfinance.

    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        print(f"Fetched {len(news)} articles for {ticker_symbol}")
        news_data = []
        for article in news:
            # Extract title from nested 'content' field
            title = article.get('content', {}).get('title', '')
            if not title:
                print(f"Warning: No title found for article: {article}")
                continue
            news_data.append({
                'title': title,
                'publisher': article.get('content', {}).get('provider', {}).get('displayName', ''),
                'link': article.get('clickThroughUrl', {}).get('url', ''),
                'published_time': article.get('content', {}).get('pubDate', '')
            })
        return news_data
    except Exception as e:
        print(f"Error fetching news for {ticker_symbol}: {e}")
        return []

def scrape_article_content(url):
    #Scrape the full text of an article from its URL.

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text() for p in paragraphs])
        print(f"Scraped content (first 100 chars): {content[:100]}")
        return content
    except Exception as e:
        print(f"Error scraping article {url}: {e}")
        return ""

