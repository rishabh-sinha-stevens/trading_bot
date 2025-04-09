import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime


class SimulatedTradingBot:
    def __init__(self, symbols, short_window=1, long_window=5, total_capital=10000):
            self.symbols = symbols
            self.short_window = short_window  # 1 period = 5 minutes
            self.long_window = long_window  # 5 periods = 25 minutes
            self.total_capital = total_capital
            self.portfolio = {symbol: {
                'cash': total_capital / len(symbols),
                'position': 0,
                'trades': [],
                'profit_loss': 0
            } for symbol in symbols}

    def get_data(self, symbol):
        # Fetch intraday data (5-minute intervals) for a specific symbol
        stock = yf.Ticker(symbol)
        df = stock.history(period="60d", interval="5m")  # 60 days of 5-minute data
        return df
    
    def calculate_indicators(self, df):
        # Calculate moving averages based on 5-minute periods
        df['Short_MA'] = df['Close'].rolling(window=self.short_window).mean()  # 5 minutes
        df['Long_MA'] = df['Close'].rolling(window=self.long_window).mean()  # 25 minutes
        return df


    def generate_signals(self, df):
        # Generate buy/sell signals
        df['Signal'] = 0
        df['Signal'] = np.where(df['Short_MA'] > df['Long_MA'], 1, 0)
        df['Position'] = df['Signal'].diff()
        return df

    def execute_simulated_trade(self, symbol, price, signal):
        portfolio = self.portfolio[symbol]

        if signal == 1 and portfolio['cash'] > price:  # Simulated buy
            shares_to_buy = int(portfolio['cash'] / price)
            cost = shares_to_buy * price
            if cost <= portfolio['cash']:
                portfolio['position'] += shares_to_buy
                portfolio['cash'] -= cost
                trade = {
                    'type': 'BUY',
                    'shares': shares_to_buy,
                    'price': price,
                    'timestamp': datetime.now()
                }
                portfolio['trades'].append(trade)
                print(f"{datetime.now()}: SIMULATED BUY {shares_to_buy} {symbol} shares at ${price:.2f}")

        elif signal == -1 and portfolio['position'] > 0:  # Simulated sell
            sale_proceeds = portfolio['position'] * price
            last_buy_price = next((trade['price'] for trade in reversed(portfolio['trades'])
                                   if trade['type'] == 'BUY'), 0)
            trade_pl = (price - last_buy_price) * portfolio['position']
            portfolio['profit_loss'] += trade_pl

            portfolio['cash'] += sale_proceeds
            trade = {
                'type': 'SELL',
                'shares': portfolio['position'],
                'price': price,
                'timestamp': datetime.now(),
                'trade_pl': trade_pl
            }
            portfolio['trades'].append(trade)
            print(f"{datetime.now()}: SIMULATED SELL {portfolio['position']} {symbol} shares at ${price:.2f}")
            portfolio['position'] = 0

    def run(self):
        print(f"Starting simulated trading bot for {', '.join(self.symbols)}")
        print(f"Total initial simulated capital: ${self.total_capital}")
        print(f"Capital per symbol: ${self.total_capital / len(self.symbols):.2f}")

        while True:
            try:
                total_portfolio_value = 0
                total_pl = 0

                for symbol in self.symbols:
                    df = self.get_data(symbol)
                    if df.empty:
                        print(f"No data available for {symbol}")
                        continue

                    df = self.calculate_indicators(df)
                    df = self.generate_signals(df)

                    latest_price = df['Close'].iloc[-1]
                    latest_signal = df['Position'].iloc[-1]

                    if not pd.isna(latest_signal):
                        self.execute_simulated_trade(symbol, latest_price, latest_signal)

                    symbol_value = (self.portfolio[symbol]['cash'] +
                                    (self.portfolio[symbol]['position'] * latest_price))
                    total_portfolio_value += symbol_value
                    total_pl += self.portfolio[symbol]['profit_loss']

                    print(f"{symbol} - Cash: ${self.portfolio[symbol]['cash']:.2f} | "
                          f"Shares: {self.portfolio[symbol]['position']} | "
                          f"Value: ${symbol_value:.2f} | "
                          f"P/L: ${self.portfolio[symbol]['profit_loss']:.2f}")

                print(f"Total Simulated Portfolio Value: ${total_portfolio_value:.2f}")
                print(f"Total Simulated Profit/Loss: ${total_pl:.2f}")
                print("-" * 50)

                time.sleep(300)  # 5 minutes

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)


# Example usage
if __name__ == "__main__":
    # Prompt user for input with default values
    print("Kindly make you are running the Bot when the stock market is open ( Mon - Fri from 9:30 am to 4:00 pm ).\n")
    try:
        total_capital = input("Enter the total capital for the simulated trading bot (default: 10000): ")
        total_capital = float(total_capital) if total_capital.strip() else 10000

        short_window = input("Enter the short moving average window (in periods, default: 1): ")
        short_window = int(short_window) if short_window.strip() else 1

        long_window = input("Enter the long moving average window (in periods, default: 5): ")
        long_window = int(long_window) if long_window.strip() else 5
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        exit(1)

    symbols = ["AAPL", "NVDA", "KO", "META", "ASTS", "AMZN", "NFLX", "TEM", "PLTR", "RDDT"]
    bot = SimulatedTradingBot(symbols=symbols,
                              short_window=short_window,
                              long_window=long_window,
                              total_capital=total_capital)
    bot.run()