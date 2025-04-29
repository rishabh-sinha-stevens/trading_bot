import tkinter as tk
from tkinter import ttk

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
