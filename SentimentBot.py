import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import pandas as pd

class SentimentBot:
    def __init__(self):
        # initialize a single VADER analyzer instance
        self.vader = SentimentIntensityAnalyzer()

    def process_news_sentiment(self, ticker_symbol: str) -> pd.DataFrame:
        pass
def get_yahoo_finance_news(ticker_symbol):
    """ Fetch news articles for a given stock ticker using yfinance. """
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        print(f"Fetched {len(news)} articles for {ticker_symbol}")
        news_data = []
        for article in news:
            # Extract title, publisher and link of the article
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

def analyze_sentiment_vader(text):
    """
    Perform sentiment analysis using VADER.
    Returns a score between -1 (negative) and 1 (positive).
    """
    if not text:
        return 0.0
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    return sentiment['compound']

def analyze_sentiment_textblob(text):
    """
    Perform sentiment analysis using TextBlob.
    Returns a score between -1 (negative) and 1 (positive).
    """
    if not text:
        return 0.0
    blob = TextBlob(text)
    return blob.sentiment.polarity