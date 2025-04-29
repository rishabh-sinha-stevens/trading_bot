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