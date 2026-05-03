"""
Fetches monthly S&P 500 (^GSPC) and Nasdaq Composite (^IXIC) closing prices
using yfinance and writes them to index_data.json.

Run locally:  pip install yfinance && python fetch_index_data.py
Auto-run:     GitHub Actions (.github/workflows/update_index_data.yml) — weekly
"""

import json
import sys
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)


def fetch_monthly(ticker: str, start: str = "2017-09-01") -> dict:
    """Returns {YYYY-MM: close_price} for all months from start to today."""
    df = yf.download(ticker, start=start, interval="1mo", auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data returned for {ticker}")

    result = {}
    close_col = "Close"
    for date, row in df.iterrows():
        ym = date.strftime("%Y-%m")
        val = row[close_col]
        # Handle MultiIndex columns (yfinance >= 0.2.x)
        if hasattr(val, "__iter__"):
            val = list(val)[0]
        result[ym] = round(float(val), 2)
    return result


def main():
    print("Fetching S&P 500 (^GSPC)...")
    sp500 = fetch_monthly("^GSPC")
    print(f"  → {len(sp500)} months  ({min(sp500)} – {max(sp500)})")

    print("Fetching Nasdaq Composite (^IXIC)...")
    nasdaq = fetch_monthly("^IXIC")
    print(f"  → {len(nasdaq)} months  ({min(nasdaq)} – {max(nasdaq)})")

    data = {
        "sp500":   sp500,
        "nasdaq":  nasdaq,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }

    out_path = "index_data.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nWrote {out_path}  (updated={data['updated']})")


if __name__ == "__main__":
    main()
