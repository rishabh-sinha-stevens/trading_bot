import time
from datetime import datetime
from TradingBot import TradingBot  # Import the TradingBot class
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class PortfolioMonitor:
    def __init__(self, bot):
        self.bot = bot  # Reference to the TradingBot instance
        self.analyzer = SentimentIntensityAnalyzer()  # Initialize sentiment analyzer

    def display_menu(self):
        print("\nPortfolio Monitor Menu:")
        print("1. View Current Portfolio")
        print("2. Analyze Yahoo Finance News for a Stock")
        print("3. Add New Stock")
        print("4. Exit")

    def view_portfolio(self):
        print("\nCurrent Portfolio Status:")
        self.bot.display_portfolio()

 
