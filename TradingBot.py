# TradingBot.py

import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

class TradingBot:
    def __init__(self, total_capital=10000):
        self.total_capital = total_capital
        self.portfolio = {}
        self.initial_cash = total_capital

    def search_stock(self):
        while True:
            search_term = input("Enter ticker symbol or company name (or 'done' to finish): ")
            if search_term.lower() == 'done':
                break

            try:
                stock = yf.Ticker(search_term)
                info = stock.info

                if not info or 'symbol' not in info:
                    print("Stock not found. Please try again.")
                    continue

                print(f"Found: {info['longName']} ({info['symbol']})")
                print(f"Current Price: ${info['regularMarketPrice']:.2f}")

                while True:
                    try:
                        shares = float(input("How many shares would you like to start with? (0 for none): "))
                        if shares < 0:
                            print("Please enter a non-negative number.")
                            continue
                        break
                    except ValueError:
                        print("Please enter a valid number.")

                symbol = info['symbol']
                cash = self.initial_cash if shares == 0 else 0
                cost = shares * info['regularMarketPrice'] if shares > 0 else 0

                if shares > 0 and cost > self.initial_cash:
                    print(f"Insufficient capital. Available: ${self.initial_cash:.2f}, Needed: ${cost:.2f}")
                    continue

                self.portfolio[symbol] = {
                    'cash': cash,
                    'position': shares,
                    'trades': [{
                        'type': 'INITIAL_BUY',
                        'shares': shares,
                        'price': info['regularMarketPrice'],
                        'timestamp': datetime.now()
                    }] if shares > 0 else [],
                    'profit_loss': 0
                }
                self.initial_cash -= cost
                if shares > 0:
                    print(f"Added {shares} shares of {symbol} to portfolio")
                print(f"Remaining initial capital: ${self.initial_cash:.2f}")

            except Exception as e:
                print(f"Error finding stock: {e}")

    def get_data(self, symbol):
        pass

    def calculate_indicators(self, df, short_window=1, long_window=5):
        pass

    def generate_signals(self, df):
        pass

    def execute_simulated_trade(self, symbol, price, signal):
        pass

    def display_portfolio(self):
        pass

    def run(self):
        pass

if __name__ == "__main__":
    bot = TradingBot(total_capital=10000)
    bot.run()
