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

def analyze_sentiment_vader(text):

    #Perform sentiment analysis using VADER.Returns a compound score between -1 (negative) and 1 (positive).

    if not text:
        return 0.0
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    return sentiment['compound']

def analyze_sentiment_textblob(text):

    #Perform sentiment analysis using TextBlob. Returns a polarity score between -1 (negative) and 1 (positive).
    if not text:
        return 0.0
    blob = TextBlob(text)
    return blob.sentiment.polarity

def process_news_sentiment(ticker_symbol, use_article_content=False):

    #Process news for a given ticker and calculate sentiment scores.

    news_data = get_yahoo_finance_news(ticker_symbol)
    if not news_data:
        print(f"No news found for {ticker_symbol}.")
        return None

    results = []
    for article in news_data:
        title = article['title']
        text_to_analyze = title
        if use_article_content:
            content = scrape_article_content(article['link'])
            text_to_analyze = content if content else title
        print(f"Title: {title[:100]}")
        print(f"Analyzing text (first 100 chars): {text_to_analyze[:100]}")

        vader_score = analyze_sentiment_vader(text_to_analyze)
        textblob_score = analyze_sentiment_textblob(text_to_analyze)

        results.append({
            'title': title,
            'publisher': article['publisher'],
            'link': article['link'],
            'vader_sentiment': vader_score,
            'textblob_sentiment': textblob_score,
            'analyzed_text_preview': text_to_analyze[:100]
        })

    return pd.DataFrame(results)

