\# Trading Bot & Sentiment Analysis GUI

This project provides a \*\*Tkinter-based GUI\*\* for simulating a
moving-average crossover trading strategy on both live and historical
stock data, along with basic sentiment analysis of news headlines.

\-\--

\## Features

\- \*\*Trading Bot\*\* (\`TradingBot.py\`):  - Live mode: fetches
minute-level data in real time during market hours.  - Historical mode:
simulates trading over a user-specified date's data.  - Moving-average
crossover signals (short vs. long windows).  - Tracks positions, cash
balance, P/L and renders a price chart.

\- \*\*Sentiment Analysis\*\* (\`SentimentBot.py\`):  - Fetches recent
news headlines via Yahoo Finance.  - Computes VADER and TextBlob
sentiment scores.  - Provides a Buy/Hold/Sell recommendation based on
average sentiment.

\- \*\*GUI Front‑End\*\* (\`GUI.py\`):  - Two tabs: Trading and
Sentiment.  - Dropdowns to select tickers and modes, with status
updates.  - Table view of portfolio and real-time price chart.  -
News‐list view with sentiment columns.

\- \*\*Entry Point\*\*: \`main.py\` launches the GUI application.
citeturn2file0

\-\--

\## Requirements

\- Python 3.8+ - Dependencies (install via pip): \`\`\`bash pip install
yfinance pandas numpy matplotlib vaderSentiment textblob tk \`\`\`

\> Note: On some systems, \`tkinter\` may be provided by the OS package
manager (e.g. \`sudo apt install python3-tk\`).

\-\--

\## Installation & Setup

1\. Clone the repository: \`\`\`bash git clone \<repo_url\> cd
\<repo_folder\> \`\`\` 2. Create and activate a virtual environment
(recommended): \`\`\`bash python3 -m venv venv source venv/bin/activate
\# on Windows: venv\\\\Scripts\\\\activate \`\`\` 3. Install
dependencies: \`\`\`bash pip install -r requirements.txt \`\`\`

If you don't have a \`requirements.txt\`, install packages manually (see
\*\*Requirements\*\* above).

\-\--

\## Usage

Run the GUI: \`\`\`bash python main.py \`\`\`

\### Trading Tab

1\. \*\*Add\*\* a stock:  - Select ticker and number of shares → click
\`Add\`. 2. \*\*Start Bot\*\*:  - Live data: click \*\*Yes\*\* at
prompt.  - Historical: click \*\*No\*\*, enter \`YYYY-MM-DD\` date →
simulates that day. 3. \*\*Monitor\*\*:  - Portfolio table updates every
few seconds.  - Price chart displays the last 60 data points.  - Status
label shows last update time. citeturn2file3

\### Sentiment Tab

1\. Select a ticker from the dropdown. 2. Click \*\*Check Sentiment\*\*.
3. View news headlines with VADER/TextBlob scores. citeturn2file1

\-\--

\## Project Structure

\`\`\` ├── main.py \# Launches the GUI ├── GUI.py \# Tkinter application
├── TradingBot.py \# Core trading logic ├── SentimentBot.py \# News
sentiment extraction ├── tests/ \# (optional) unit tests └── README.md
\# This file \`\`\`

\-\--

\## Testing (Optional)

Add basic pytest tests under \`tests/\` for functions like -
\`TradingBot.calculate_indicators\` - \`TradingBot.get_snapshot\` -
\`SentimentBot.process_news_sentiment\`

Then run: \`\`\`bash pytest \`\`\`

\-\--

\## License

\[MIT License\](LICENSE)
