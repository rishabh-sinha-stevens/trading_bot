from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import yfinance as yf


class TradingBot:
    """A minimalist moving-average crossover trading simulator."""

    def __init__(self, total_capital: float = 10_000):
        self.total_capital = total_capital
        self.initial_cash = total_capital
        self.portfolio: Dict[str, Dict[str, Any]] = {}
        self._bot_running = False

    # ------------------------------------------------------------------ GUI helpers
    def get_snapshot(self) -> Dict[str, Any]:
        """Return a dict with current cash/positions/value/P L for the GUI."""
        total_value = self.initial_cash
        total_pl = 0.0
        for sym, rec in self.portfolio.items():
            last_price = self._safe_price(sym)
            total_value += rec["position"] * last_price
            total_pl += rec["profit_loss"]
        return {
            "cash": self.initial_cash,
            "positions": self.portfolio,
            "total_value": total_value,
            "total_pl": total_pl,
        }

    # ------------------------------------------------------------------ interactive / GUI
    def search_stock(self, ticker: Optional[str] = None, shares: Optional[float] = None):
        
        while True:
            if ticker is None:
                search_term = input(
                    "Enter ticker symbol or company name (or 'done'): "
                ).strip()
                if search_term.lower() == "done":
                    break
            else:
                search_term = ticker

            stock = yf.Ticker(search_term)
            info = stock.info or {}
            symbol = info.get("symbol")
            if symbol is None:
                if ticker is None:
                    print("Stock not found, try again.")
                    continue
                raise ValueError(f"Ticker {search_term} not found")

            price = info["regularMarketPrice"]
            if shares is None:
                while True:
                    try:
                        shares = float(
                            input("How many shares would you like to start with? (0=skip): ")
                        )
                        break
                    except ValueError:
                        print("Enter a valid number.")
            cost = shares * price
            if cost > self.initial_cash:
                if ticker is None:
                    print("Insufficient capital.")
                    ticker = shares = None
                    continue
                raise ValueError("Insufficient capital")

            self.portfolio[symbol] = {
                "cash": self.initial_cash - cost if shares == 0 else 0,
                "position": shares,
                "trades": [
                    {
                        "type": "INITIAL_BUY",
                        "shares": shares,
                        "price": price,
                        "timestamp": datetime.now(),
                    }
                ]
                if shares > 0
                else [],
                "profit_loss": 0.0,
            }
            self.initial_cash -= cost
            break  # one stock per call for GUI

    # ------------------------------------------------------------------ core logic
    @staticmethod
    def get_data(symbol: str, date: str = None) -> pd.DataFrame:
        """
        If `date` is given (YYYY-MM-DD), fetch that single day's 5m bars;
        otherwise pull last 30d of 5m bars as before.
        """
        if date:
            start = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=3))\
                      .strftime("%Y-%m-%d")
            end = date 
            print(f"Fetching data for {symbol} from {start} to {end}")
            return yf.Ticker(symbol).history(start=start, end=end, interval="1m")
        
        # return yf.Ticker(symbol).history(interval="1m")
        print("start", (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"))
        print("end", datetime.now().strftime("%Y-%m-%d"))

        return yf.Ticker(symbol).history(period='3d', interval='1m')

    @staticmethod
    def calculate_indicators(df: pd.DataFrame, s: int = 1, l: int = 5) -> pd.DataFrame:
        print("df.head():  ", df.head())
        print("df.tail():  ", df.tail())
        df["Short_MA"] = df["Close"].rolling(s).mean()
        df["Long_MA"] = df["Close"].rolling(l).mean()
        df["Signal"] = np.where(df["Short_MA"] > df["Long_MA"], 1, 0)
        df["Position"] = df["Signal"].diff()
        return df

    def execute_simulated_trade(self, symbol, price, signal, timestamp=None):
        print(f"Executing trade for {symbol}: {signal} at {price:.2f}")
        rec = self.portfolio[symbol]
        if signal == 1 and self.initial_cash > price:
            shares = int(self.initial_cash / price)
            cost = shares * price
            rec["position"] += shares
            self.initial_cash -= cost
            rec["trades"].append(
                {"type": "BUY", "shares": shares, "price": price, "timestamp":  timestamp or datetime.now()}
            )
        elif signal == -1 and rec["position"] > 0:
            proceeds = rec["position"] * price
            last_buy = next(
                (t["price"] for t in reversed(rec["trades"]) if t["type"] in ("BUY", "INITIAL_BUY")),
                price,
            )
            trade_pl = (price - last_buy) * rec["position"]
            rec["profit_loss"] += trade_pl
            self.initial_cash += proceeds
            rec["cash"] += proceeds
            rec["trades"].append(
                {
                    "type": "SELL",
                    "shares": rec["position"],
                    "price": price,
                    "timestamp": timestamp or datetime.now(),
                    "trade_pl": trade_pl,
                }
            )
            rec["position"] = 0

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _safe_price(symbol: str) -> float:
        try:
            return yf.Ticker(symbol).info["regularMarketPrice"]
        except Exception:
            return 0.0
