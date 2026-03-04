"""
Finviz Speculative Stock Scanner
Scans at 16:15 RO (13:15 UTC) and validates at 16:45 RO (13:45 UTC)
"""

import json
import os
import time
import random
import logging
from datetime import datetime, timezone
from pathlib import Path

from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

WATCHLIST_FILE = DATA_DIR / "watchlist_1615.json"
FINAL_FILE     = DATA_DIR / "final_1645.json"

# Finviz screener filters
SCAN_FILTERS = {
    "Price":            "Under $20",
    "Relative Volume":  "Over 3",
    "Change":           "Up 5%",
}

VALIDATION_FILTERS = {
    "Gap":    "Up 2%",
    "Change": "Up",
}

SLEEP_MIN = 2.5   # seconds between requests (be polite to Finviz)
SLEEP_MAX = 5.0


# ── Helpers ────────────────────────────────────────────────────────────────────

def polite_sleep(label: str = ""):
    delay = random.uniform(SLEEP_MIN, SLEEP_MAX)
    log.info(f"Sleeping {delay:.1f}s {label}")
    time.sleep(delay)


def get_overview(filters: dict) -> list[dict]:
    """Run a Finviz screener and return rows as list-of-dicts."""
    foverview = Overview()
    foverview.set_filter(filters_dict=filters)
    df = foverview.screener_view()
    if df is None or df.empty:
        return []
    return df.to_dict(orient="records")


def enrich_ticker(ticker: str) -> dict:
    """Fetch per-ticker data from Finviz quote page."""
    try:
        stock = finvizfinance(ticker)
        info  = stock.ticker_fundament()
        return {
            "52w_high":       info.get("52W High",       "N/A"),
            "52w_low":        info.get("52W Low",        "N/A"),
            "52w_change":     info.get("52W Change",     "N/A"),
            "avg_volume":     info.get("Avg Volume",     "N/A"),
            "rel_volume":     info.get("Rel Volume",     "N/A"),
            "gap":            info.get("Gap",            "N/A"),
            "price":          info.get("Price",          "N/A"),
            "change":         info.get("Change",         "N/A"),
            "industry":       info.get("Industry",       "N/A"),
            "sector":         info.get("Sector",         "N/A"),
            "description":    info.get("Description",   ""),
        }
    except Exception as e:
        log.warning(f"Could not enrich {ticker}: {e}")
        return {}


def risk_level(row: dict) -> str:
    """
    Compute risk badge based on 52-week performance.
    Falls back to extracting % from 52w_high field (e.g. "16.99 -65.57%")
    """
    raw = row.get("52w_change", "") or row.get("52W Change", "") or ""

    # If N/A, try extracting from 52w_high string e.g. "16.99 -65.57%"
    if not raw or str(raw).strip() in ("N/A", "nan", ""):
        high_raw = row.get("52w_high", "") or row.get("52W High", "") or ""
        parts = str(high_raw).split()
        for part in parts:
            if "%" in part:
                raw = part
                break

    try:
        val = float(str(raw).replace("%", "").replace(",", "").strip())
        if val <= -90:
            return "EXTREME"
        elif val <= -60:
            return "HIGH"
        elif val <= -30:
            return "MEDIUM"
        else:
            return "LOW"
    except Exception:
        return "UNKNOWN"


def parse_pct(value) -> float:
    try:
        return float(str(value).replace("%", "").replace(",", "").strip())
    except Exception:
        return 0.0


# ── Scan 16:15 ─────────────────────────────────────────────────────────────────

def scan_1615():
    log.info("=== SCAN 16:15 — Building Watchlist ===")
    rows = get_overview(SCAN_FILTERS)
    log.info(f"Found {len(rows)} candidates from screener")

    watchlist = []
    for i, row in enumerate(rows):
        ticker = str(row.get("Ticker", "")).strip()
        if not ticker:
            continue

        polite_sleep(f"({i+1}/{len(rows)}) enriching {ticker}")
        extra = enrich_ticker(ticker)
        combined = {**row, **extra}
        combined["risk"] = risk_level(combined)
        combined["scan_time"] = datetime.now(timezone.utc).isoformat()
        watchlist.append(combined)

    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=2, default=str)

    log.info(f"Watchlist saved → {WATCHLIST_FILE} ({len(watchlist)} tickers)")
    return watchlist


# ── Validate 16:45 ─────────────────────────────────────────────────────────────

def validate_1645():
    log.info("=== VALIDATE 16:45 — Strong Buy Selection ===")

    if not WATCHLIST_FILE.exists():
        log.error("Watchlist file not found — run scan_1615 first!")
        return []

    with open(WATCHLIST_FILE) as f:
        watchlist = json.load(f)

    tickers = [r.get("Ticker") or r.get("ticker") for r in watchlist if r.get("Ticker") or r.get("ticker")]
    log.info(f"Re-validating {len(tickers)} tickers from watchlist")

    strong_buys = []
    for i, ticker in enumerate(tickers):
        polite_sleep(f"({i+1}/{len(tickers)}) re-checking {ticker}")
        try:
            extra = enrich_ticker(ticker)

            gap_pct    = parse_pct(extra.get("gap",    "0"))
            change_pct = parse_pct(extra.get("change", "0"))

            if gap_pct >= 2.0 and change_pct > 0:
                record = {
                    "Ticker":     ticker,
                    "Price":      extra.get("price",      "N/A"),
                    "Change":     extra.get("change",     "N/A"),
                    "Gap":        extra.get("gap",        "N/A"),
                    "Rel Volume": extra.get("rel_volume", "N/A"),
                    "52W Change": extra.get("52w_change", "N/A"),
                    "Industry":   extra.get("industry",   "N/A"),
                    "Sector":     extra.get("sector",     "N/A"),
                    "risk":       risk_level(extra),
                    "status":     "STRONG BUY",
                    "validated_time": datetime.now(timezone.utc).isoformat(),
                }
                strong_buys.append(record)
                log.info(f"  ✅ STRONG BUY: {ticker} | Gap {gap_pct:.1f}% | Change {change_pct:.1f}%")
            else:
                log.info(f"  ❌ Skipped: {ticker} | Gap {gap_pct:.1f}% | Change {change_pct:.1f}%")

        except Exception as e:
            log.warning(f"Error validating {ticker}: {e}")

    with open(FINAL_FILE, "w") as f:
        json.dump(strong_buys, f, indent=2, default=str)

    log.info(f"Final saved → {FINAL_FILE} ({len(strong_buys)} STRONG BUY)")
    return strong_buys


# ── Entrypoint ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"

    if mode == "scan":
        scan_1615()
    elif mode == "validate":
        validate_1645()
    elif mode == "both":
        scan_1615()
        log.info("Sleeping 30 minutes before validation...")
        time.sleep(30 * 60)
        validate_1645()
    else:
        log.error(f"Unknown mode: {mode}. Use: scan | validate | both")
        sys.exit(1)
