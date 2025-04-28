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

     def analyze_news(self):
        symbol = input("Enter ticker symbol to analyze news: ").upper()
        if symbol not in self.bot.portfolio:
            print(f"No portfolio data for {symbol}. Please add it first.")
            return

        try:
            # Fetch news for the stock using yfinance
            stock = yf.Ticker(symbol)
            news_items = stock.news

            if not news_items:
                print(f"No recent news found for {symbol}.")
                return

            print(f"\nNews Analysis for {symbol}:")
            total_compound = 0
            news_count = 0

            # Analyze sentiment for each news item
            for item in news_items:
                title = item.get('title', '')
                if not title:
                    continue

                # Perform sentiment analysis on the title
                sentiment = self.analyzer.polarity_scores(title)
                compound = sentiment['compound']
                total_compound += compound
                news_count += 1

                # Display news details
                sentiment_label = "Positive" if compound > 0.05 else "Negative" if compound < -0.05 else "Neutral"
                print(f"- {title}")
                print(f"  Sentiment: {sentiment_label} (Score: {compound:.3f})")
                print(f"  Source: {item.get('publisher', 'Unknown')}, "
                      f"Time: {datetime.fromtimestamp(item.get('providerPublishTime', 0))}")

            # Calculate average sentiment and make recommendation
            if news_count > 0:
                avg_compound = total_compound / news_count
                if avg_compound > 0.05:
                    recommendation = "Buy"
                elif avg_compound < -0.05:
                    recommendation = "Sell"
                else:
                    recommendation = "Hold"
                print(f"\nSummary for {symbol}:")
                print(f"Average Sentiment Score: {avg_compound:.3f}")
                print(f"Recommendation: {recommendation}")
            else:
                print("No valid news titles to analyze.")

        except Exception as e:
            print(f"Error fetching or analyzing news for {symbol}: {e}")


 
