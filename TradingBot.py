# Import required libraries for stock data, data manipulation, and time handling
import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Define the TradingBot class to simulate stock trading
class TradingBot:
    # Initialize the bot with a specified total capital (default $10,000)
    def __init__(self, total_capital=10000):
        self.total_capital = total_capital  # Total starting capital
        self.portfolio = {}  # Dictionary to store portfolio data for each stock
        self.initial_cash = total_capital  # Cash available for trading

    # Allow user to search and add stocks to the portfolio
    def search_stock(self):
        while True:
            # Prompt user for ticker symbol or company name
            search_term = input("Enter ticker symbol or company name (or 'done' to finish): ")
            if search_term.lower() == 'done':
                break  # Exit loop if user is done

            try:
                # Attempt to fetch stock data using yfinance
                stock = yf.Ticker(search_term)
                info = stock.info

                # Check if stock data is valid
                if not info or 'symbol' not in info:
                    print("Stock not found. Please try again.")
                    continue

                # Display stock details
                print(f"Found: {info['longName']} ({info['symbol']})")
                print(f"Current Price: ${info['regularMarketPrice']:.2f}")

                # Prompt user for number of shares to buy
                while True:
                    try:
                        shares = float(input("How many shares would you like to start with? (0 for none): "))
                        if shares < 0:
                            print("Please enter a non-negative number.")
                            continue
                        break
                    except ValueError:
                        print("Please enter a valid number.")

                # Extract stock symbol and calculate cost
                symbol = info['symbol']
                cash = self.initial_cash if shares == 0 else 0
                cost = shares * info['regularMarketPrice'] if shares > 0 else 0

                # Check if user has enough capital to buy shares
                if shares > 0 and cost > self.initial_cash:
                    print(f"Insufficient capital. Available: ${self.initial_cash:.2f}, Needed: ${cost:.2f}")
                    continue

                # Add stock to portfolio with initial trade details
                self.portfolio[symbol] = {
                    'cash': cash,  # Cash allocated to this stock
                    'position': shares,  # Number of shares held
                    'trades': [{
                        'type': 'INITIAL_BUY',
                        'shares': shares,
                        'price': info['regularMarketPrice'],
                        'timestamp': datetime.now()
                    }] if shares > 0 else [],  # Record initial buy trade
                    'profit_loss': 0  # Track profit/loss for this stock
                }
                self.initial_cash -= cost  # Deduct cost from available cash
                if shares > 0:
                    print(f"Added {shares} shares of {symbol} to portfolio")
                print(f"Remaining initial capital: ${self.initial_cash:.2f}")

            except Exception as e:
                print(f"Error finding stock: {e}")  # Handle errors gracefully

    # Fetch historical stock data for a given symbol
    def get_data(self, symbol):
        stock = yf.Ticker(symbol)
        # Get 60 days of 5-minute interval data
        df = stock.history(period="60d", interval="5m")
        return df

    # Calculate technical indicators (moving averages) for trading signals
    def calculate_indicators(self, df, short_window=1, long_window=5):
        # Calculate short and long moving averages
        df['Short_MA'] = df['Close'].rolling(window=short_window).mean()
        df['Long_MA'] = df['Close'].rolling(window=long_window).mean()
        return df

    # Generate buy/sell signals based on moving average crossover
    def generate_signals(self, df):
        df['Signal'] = 0  # Initialize signal column
        # Set signal to 1 (buy) when short MA crosses above long MA
        df['Signal'] = np.where(df['Short_MA'] > df['Long_MA'], 1, 0)
        # Calculate position changes (1 for buy, -1 for sell)
        df['Position'] = df['Signal'].diff()
        return df

    def execute_simulated_trade(self, symbol, price, signal):
        portfolio = self.portfolio[symbol]  # Access stock's portfolio data

        # Buy signal: Purchase shares if cash is available
        if signal == 1 and self.initial_cash > price:
            shares_to_buy = int(self.initial_cash / price)  # Calculate affordable shares
            cost = shares_to_buy * price
            if cost <= self.initial_cash:
                portfolio['position'] += shares_to_buy  # Update share count
                self.initial_cash -= cost  # Deduct cost from cash
                portfolio['cash'] = 0  # Reset stock-specific cash
                trade = {
                    'type': 'BUY',
                    'shares': shares_to_buy,
                    'price': price,
                    'timestamp': datetime.now()
                }
                portfolio['trades'].append(trade)  # Record trade
                print(f"{datetime.now()}: SIMULATED BUY {shares_to_buy} {symbol} shares at ${price:.2f}")

        # Sell signal: Sell all shares if holding a position
        elif signal == -1 and portfolio['position'] > 0:
            sale_proceeds = portfolio['position'] * price  # Calculate sale value
            # Find the last buy price for profit/loss calculation
            last_buy_price = next((trade['price'] for trade in reversed(portfolio['trades'])
                                   if trade['type'] in ['BUY', 'INITIAL_BUY']), 0)
            trade_pl = (price - last_buy_price) * portfolio['position']  # Calculate trade profit/loss
            portfolio['profit_loss'] += trade_pl  # Update stock's total profit/loss

            portfolio['cash'] += sale_proceeds  # Add proceeds to stock's cash
            self.initial_cash += sale_proceeds  # Add proceeds to total cash
            trade = {
                'type': 'SELL',
                'shares': portfolio['position'],
                'price': price,
                'timestamp': datetime.now(),
                'trade_pl': trade_pl
            }
            portfolio['trades'].append(trade)  # Record trade
            print(f"{datetime.now()}: SIMULATED SELL {portfolio['position']} {symbol} shares at ${price:.2f}")
            portfolio['position'] = 0  # Reset share count

    # Display the current portfolio status
    def display_portfolio(self):
        total_value = self.initial_cash  # Start with remaining cash
        total_pl = 0  # Track total profit/loss

        # Iterate through each stock in the portfolio
        for symbol in self.portfolio:
            # Get latest stock price
            latest_price = yf.Ticker(symbol).info['regularMarketPrice']
            # Calculate stock's total value (shares * price + cash)
            value = self.portfolio[symbol]['position'] * latest_price + self.portfolio[symbol]['cash']
            total_value += self.portfolio[symbol]['position'] * latest_price
            total_pl += self.portfolio[symbol]['profit_loss']

            # Print stock details
            print(f"{symbol} - Cash: ${self.portfolio[symbol]['cash']:.2f} | "
                  f"Shares: {int(self.portfolio[symbol]['position'])} | "
                  f"Value: ${value:.2f} | "
                  f"P/L: ${self.portfolio[symbol]['profit_loss']:.2f}")

        # Print portfolio summary
        print(f"Remaining Cash: ${self.initial_cash:.2f}")
        print(f"Total Portfolio Value: ${total_value:.2f}")
        print(f"Total Profit/Loss: ${total_pl:.2f}")

    def run(self):
        pass

if __name__ == "__main__":
    bot = TradingBot(total_capital=10000)
    bot.run()
