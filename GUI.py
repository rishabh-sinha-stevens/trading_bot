import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from TradingBot import TradingBot
from SentimentBot import SentimentBot 

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TradingApp(tk.Tk):
    """Tkinter GUI for TradingApp with TradingBot and SentimentBot."""

    # Referesh time in milliseconds to updaate the UI
    REFRESH_MS = 3000

    def __init__(self):
        super().__init__()
        self.title("Dashboard")
        self.minsize(1000, 600)
        self.configure(bg="#222")
        
        style = ttk.Style()
        style.theme_use("alt")
        style.configure("Treeview", background="#333", foreground="#eee", fieldbackground="#333")
        style.map("Treeview", background=[("selected", "#555")])

        # TradingBot objects
        self.bot = TradingBot()
        # SentimentBot object
        self.sentiment_bot  = SentimentBot()

        self.bot_running = False
        self.sim_date: str | None = None

        # Defaults
        self.default_ticker = "AAPL"
        self.default_shares = 1.0

        self._build_ui()
        self.after(self.REFRESH_MS, self._refresh)

    # ------------------------------------------------------------------ UI builders
    def _build_ui(self):
        """ Calls both tabs and sets the main layout. """
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=5, pady=5)
        self._build_trading_tab(nb)
        self._build_Sentiment_tab(nb)

    def _build_trading_tab(self, nb: ttk.Notebook):
        """ Builds the Trading Tab that shows the current portfolio with the graph and allows adding stocks, and start trading bot. """
        frame = ttk.Frame(nb)
        nb.add(frame, text="Trading")

        left = ttk.Frame(frame)
        left.pack(side="left", fill="y", padx=10, pady=10)

        # Ticker dropdown
        ttk.Label(left, text="Ticker:").grid(row=0, column=0)
        tickers = ["AAPL", "NVDA", "KO", "META", "ASTS", "AMZN", "NFLX", "TEM", "PLTR", "RDDT"]
        self.ticker_var = tk.StringVar(value=self.default_ticker)
        self.ticker_combo = ttk.Combobox(
            left, textvariable=self.ticker_var,
            values=tickers, state="readonly", width=10
        )
        self.ticker_combo.grid(row=0, column=1, pady=2)

        # Shares entry with default
        ttk.Label(left, text="Shares:").grid(row=1, column=0)
        self.shares_entry = ttk.Entry(left, width=6)
        self.shares_entry.grid(row=1, column=1, pady=2)
        self.shares_entry.insert(0, str(self.default_shares))

        # Add & Start buttons
        ttk.Button(left, text="Add", command=self._add_stock).grid(row=2, column=0, columnspan=2, pady=5)
        self.start_btn = ttk.Button(left, text="Start Bot", command=self._toggle_bot)
        self.start_btn.grid(row=3, column=0, columnspan=2, pady=5)

        # Status label
        self.status_lbl = ttk.Label(left, text="Status: Stopped", foreground="black", anchor="center")
        self.status_lbl.grid(row=4, column=0, columnspan=2, pady=10)

        # Right-side table & summary
        right = ttk.Frame(frame)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        cols = ("Ticker", "Shares", "Last Price", "Pos Value", "P/L")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=100)
        self.tree.pack(fill="both", expand=True)
        self.summary_lbl = ttk.Label(right, text="", anchor="e")
        self.summary_lbl.pack(fill="x", pady=5)

        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    def _build_Sentiment_tab(self, nb: ttk.Notebook):
        """ Creates the Sentiment analysis tab that shows news artice titles and sentiment scores. """
        self.sentiment_frame = ttk.Frame(nb)
        nb.add(self.sentiment_frame, text="Sentiment")

        top = ttk.Frame(self.sentiment_frame)
        top.pack(fill="x", pady=5, padx=5)
        ttk.Label(top, text="Select Stock:").pack(side="left")

        # self.cmb_var = tk.StringVar()
        # self.cmb = ttk.Combobox(top, textvariable=self.cmb_var, state="readonly", width=10)

        tickers = ["AAPL", "NVDA", "KO", "META", "ASTS", "AMZN", "NFLX", "TEM", "PLTR", "RDDT"]
        self.cmb_var = tk.StringVar()
        self.cmb = ttk.Combobox(
            top,
            textvariable=self.cmb_var,
            values=tickers,
            state="readonly",
            width=10
        )

        self.cmb.pack(side="left", padx=5)
        ttk.Button(top, text="Check Sentiment", command=self._analyze_news).pack(side="left")

        self.news_tree = ttk.Treeview(
            self.sentiment_frame,
            columns=("Title", "VADER", "TextBlob"),
            show="headings",
            height=12
        )
        self.news_tree.heading("Title",    text="Article Title")
        self.news_tree.heading("VADER",    text="VADER Score")
        self.news_tree.heading("TextBlob", text="TextBlob Score")
        self.news_tree.column("Title",    anchor="w",     width=400)
        self.news_tree.column("VADER",    anchor="center", width= 80)
        self.news_tree.column("TextBlob", anchor="center", width= 80)
        self.news_tree.pack(fill="both", expand=True, padx=5, pady=5)

    # ------------------------------------------------------------------ callbacks
    def _add_stock(self):
        """ Add the number of shares of seleceted stock/ticker to the portfolio."""
        ticker = self.ticker_var.get().strip().upper()
        shares = self.shares_entry.get().strip()
        if not ticker or not shares:
            messagebox.showerror("Input error", "Enter ticker and shares.")
            return
        try:
            self.bot.search_stock(ticker, float(shares))
            # Refresh available symbols in combobox
            self._update_combobox()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _toggle_bot(self):
        """ Start/stop the trading bot."""
        if not self.bot_running and not self.bot.portfolio:
            messagebox.showwarning(
                "No stocks added",
                "Please add at least one stock before starting the bot."
            )
            return
        
        # starting run → ask mode choice first
        if not self.bot_running:
            # Yes = LIVE, No = historical
            use_live = messagebox.askyesno(
                "Run Mode",
                "Click YES to run on LIVE data,\nNO to run on HISTORICAL data."
            )
            if use_live:
                self.sim_date = None
            else:
                date = simpledialog.askstring(
                    "Historical Mode",
                    "Enter date to simulate (YYYY-MM-DD):"
                )
                # if user cancels or gives no date, abort start
                if not date:
                    return
                self.sim_date = date.strip()

            # now we actually start
            self.bot_running = True
            # preload sim_data if needed
            if self.sim_date:
                self.sim_data = {}
                self.sim_idx  = {}
                for sym in self.bot.portfolio:
                    df = self.bot.get_data(sym, self.sim_date)
                    df = self.bot.calculate_indicators(df)
                    self.sim_data[sym] = df
                    self.sim_idx[sym] = 0

            mode = f"SIM {self.sim_date}" if self.sim_date else "LIVE"
            self.status_lbl.config(text=f"Status: Running ({mode})")
            self.start_btn.config(text="Stop Bot")
        else:
            # stopping
            self.bot_running = False
            self.status_lbl.config(text="Status: Stopped")
            self.start_btn.config(text="Start Bot")

    def _analyze_news(self):
        """ Analyze the sentiment scores of news articles for the selcted stocks """
        sym = self.cmb_var.get().strip().upper()
        if not sym:
            return

        df = self.sentiment_bot.process_news_sentiment(sym)
        if df is None or df.empty:
            messagebox.showinfo("No News", f"No articles found for {sym}.")
            return

        # clear and repopulate the Treeviews
        self.news_tree.delete(*self.news_tree.get_children())
        for _, row in df.iterrows():
            self.news_tree.insert(
                "", "end",
                values=(
                    row["title"],
                    f"{row['vader_sentiment']:+.2f}",
                    f"{row['textblob_sentiment']:+.2f}"
                )
            )

    # ------------------------------------------------------------------ periodic refresh
    def _refresh(self):
        """ Refresh and update the UI periodically. """
        if self.bot_running:
            self._bot_cycle()
        self._populate_tables()
        
        # calling the refresh method again after REFRESH_MS milliseconds
        self.after(self.REFRESH_MS, self._refresh)

    def _bot_cycle(self):
        """ Runs the bot cycle logic for trading and update the UI accordingly. """
        for sym in list(self.bot.portfolio.keys()):
            if self.sim_date:
                # Historical mode
                df  = self.sim_data[sym]
                idx = self.sim_idx[sym]
                print("idx", idx)
                row = df.iloc[idx]
                price, signal = row["Close"], row["Position"]
                ts = df.index[idx]

                if signal == 1 or signal == -1:
                    self.bot.execute_simulated_trade(sym, price, int(signal), timestamp=ts)

                # increment the index for the next cycle
                self.sim_idx[sym] = min(idx + 1, len(df)-1)

            else:
                # LIVE mode 
                df = self.bot.get_data(sym, None)
                if df.empty: continue
                df = self.bot.calculate_indicators(df)
                price  = df["Close"].iloc[-1]
                signal = df["Position"].iloc[-1]
                ts     = df.index[-1]
                self.bot.execute_simulated_trade(sym, price, int(signal), timestamp=ts)

            # update the bot's status label
            self.status_lbl.config(
                text=f"Status: Running ({'SIM' if self.sim_date else 'LIVE'}) — last @ {ts:%H:%M:%S}"
            )

    def _populate_tables(self):
        """ Populate the tabel and graph with the current protfolio and trading data. """
        snap = self.bot.get_snapshot()

        # Clear the treeview and populate it with the current data
        self.tree.delete(*self.tree.get_children())
        for sym, rec in snap["positions"].items():
            price = self.bot._safe_price(sym)
            value = rec["position"] * price
            pl = rec["profit_loss"]
            self.tree.insert(
                "", "end",
                values=(sym, int(rec["position"]), f"{price:.2f}", f"{value:.2f}", f"{pl:+.2f}")
            )
        self.summary_lbl.config(
            text=f"Cash: ${snap['cash']:.2f}   |   Total Value: ${snap['total_value']:.2f}   |   Total P/L: {snap['total_pl']:+.2f}"
        )

        # if bot is running and has something in portfolio then update the chart and table
        if self.bot_running and self.bot.portfolio:
            # select the first stock in the portfolio for plotting
            sym = next(iter(self.bot.portfolio))
            # get the data for that stock
            df = self.bot.get_data(sym, self.sim_date)
            df = self.bot.calculate_indicators(df)
            # now plot the last 60 bars
            df_last = df.tail(60)
            self.ax.clear()
            self.ax.plot(df_last.index, df_last["Close"], label="Price")
            self.ax.legend(loc="upper left")
            self.canvas.draw()

    def _update_combobox(self):
        # update the stock/ticker combobox with current portfolio 
        vals = list({*self.bot.portfolio.keys(), *self.ticker_combo["values"]})
        self.ticker_combo["values"] = vals

    def destroy(self):
        # Stops the bot
        self.bot_running = False
        # Quit the bot and end the task
        try:
            self.quit()
        except Exception:
            pass
        # Destroy the window
        super().destroy()
