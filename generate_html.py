"""
Dashboard HTML Generator
Reads data/watchlist_1615.json and data/final_1645.json
Outputs index.html with dark-mode Tailwind dashboard
"""

import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR      = Path("data")
WATCHLIST_FILE = DATA_DIR / "watchlist_1615.json"
FINAL_FILE     = DATA_DIR / "final_1645.json"
OUTPUT_FILE    = Path("index.html")


def load_json(path: Path) -> list:
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def risk_badge(risk: str) -> str:
    colors = {
        "EXTREME": ("bg-red-900/60 text-red-300 border border-red-700",   "⚠ EXTREME"),
        "HIGH":    ("bg-orange-900/60 text-orange-300 border border-orange-700", "▲ HIGH"),
        "MEDIUM":  ("bg-yellow-900/60 text-yellow-300 border border-yellow-700", "◆ MEDIUM"),
        "LOW":     ("bg-green-900/60 text-green-300 border border-green-700",    "✓ LOW"),
        "UNKNOWN": ("bg-zinc-800 text-zinc-400 border border-zinc-600",          "? N/A"),
    }
    cls, label = colors.get(risk, colors["UNKNOWN"])
    return f'<span class="px-2 py-0.5 rounded text-xs font-mono font-bold {cls}">{label}</span>'


def pct_cell(value) -> str:
    """Color-code a percentage value."""
    raw = str(value).replace("%", "").replace(",", "").strip()
    try:
        v = float(raw)
        if v > 0:
            return f'<span class="text-emerald-400 font-semibold">+{v:.2f}%</span>'
        elif v < 0:
            return f'<span class="text-red-400 font-semibold">{v:.2f}%</span>'
        else:
            return f'<span class="text-zinc-400">{v:.2f}%</span>'
    except Exception:
        return f'<span class="text-zinc-500">{value}</span>'


def fmt(v, default="—") -> str:
    return str(v) if v and str(v).strip() not in ("", "N/A", "None", "nan") else default


def watchlist_rows(data: list) -> str:
    if not data:
        return """
        <tr>
          <td colspan="7" class="text-center py-12 text-zinc-500 font-mono text-sm">
            Nu există date — rulează scriptul la 16:15
          </td>
        </tr>"""
    rows = []
    for r in data:
        ticker = fmt(r.get("Ticker") or r.get("ticker"))
        price  = fmt(r.get("Price")  or r.get("price"))
        change = r.get("Change") or r.get("change") or "0"
        gap    = r.get("Gap")    or r.get("gap")    or "0"
        rvol   = fmt(r.get("Rel Volume") or r.get("rel_volume"))
        risk   = r.get("risk", "UNKNOWN")
        sector = fmt(r.get("Sector") or r.get("sector"), "—")

        rows.append(f"""
        <tr class="border-b border-zinc-800 hover:bg-zinc-800/40 transition-colors group">
          <td class="px-4 py-3 font-mono font-bold text-sky-400 text-sm tracking-wider group-hover:text-sky-300">
            <a href="https://finviz.com/quote.ashx?t={ticker}" target="_blank" class="hover:underline">{ticker}</a>
          </td>
          <td class="px-4 py-3 font-mono text-zinc-200 text-sm">${price}</td>
          <td class="px-4 py-3 text-sm">{pct_cell(change)}</td>
          <td class="px-4 py-3 text-sm">{pct_cell(gap)}</td>
          <td class="px-4 py-3 font-mono text-zinc-300 text-sm">{rvol}x</td>
          <td class="px-4 py-3 text-xs text-zinc-400">{sector}</td>
          <td class="px-4 py-3">{risk_badge(risk)}</td>
        </tr>""")
    return "\n".join(rows)


def final_rows(data: list) -> str:
    if not data:
        return """
        <tr>
          <td colspan="7" class="text-center py-12 text-zinc-500 font-mono text-sm">
            Nu există validări — rulează scriptul la 16:45
          </td>
        </tr>"""
    rows = []
    for r in data:
        ticker = fmt(r.get("Ticker"))
        price  = fmt(r.get("Price"))
        change = r.get("Change", "0")
        gap    = r.get("Gap",    "0")
        rvol   = fmt(r.get("Rel Volume"))
        risk   = r.get("risk", "UNKNOWN")
        sector = fmt(r.get("Sector"), "—")

        rows.append(f"""
        <tr class="border-b border-zinc-800 hover:bg-zinc-800/40 transition-colors group">
          <td class="px-4 py-3 font-mono font-bold text-emerald-400 text-sm tracking-wider group-hover:text-emerald-300">
            <a href="https://finviz.com/quote.ashx?t={ticker}" target="_blank" class="hover:underline">{ticker}</a>
            <span class="ml-2 px-1.5 py-0.5 bg-emerald-900/50 border border-emerald-600 text-emerald-300 text-[10px] rounded font-bold">STRONG BUY</span>
          </td>
          <td class="px-4 py-3 font-mono text-zinc-200 text-sm">${price}</td>
          <td class="px-4 py-3 text-sm">{pct_cell(change)}</td>
          <td class="px-4 py-3 text-sm">{pct_cell(gap)}</td>
          <td class="px-4 py-3 font-mono text-zinc-300 text-sm">{rvol}x</td>
          <td class="px-4 py-3 text-xs text-zinc-400">{sector}</td>
          <td class="px-4 py-3">{risk_badge(risk)}</td>
        </tr>""")
    return "\n".join(rows)


def generate_html():
    watchlist = load_json(WATCHLIST_FILE)
    final     = load_json(FINAL_FILE)
    now_utc   = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

    wl_count = len(watchlist)
    sb_count = len(final)

    html = f"""<!DOCTYPE html>
<html lang="ro" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>📈 Finviz Scanner — Speculative Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --accent: #22d3ee;
      --green:  #34d399;
      --red:    #f87171;
    }}
    body {{
      font-family: 'Syne', sans-serif;
      background: #09090b;
      color: #e4e4e7;
    }}
    .font-mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Scanline overlay for terminal feel */
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
      );
      pointer-events: none;
      z-index: 9999;
    }}

    .glow-header {{
      text-shadow: 0 0 30px rgba(34,211,238,0.4);
    }}
    .card {{
      background: linear-gradient(135deg, #18181b 0%, #111113 100%);
      border: 1px solid #27272a;
      border-radius: 12px;
    }}
    .stat-card {{
      background: linear-gradient(135deg, #18181b, #111113);
      border: 1px solid #27272a;
      border-radius: 10px;
      position: relative;
      overflow: hidden;
    }}
    .stat-card::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, rgba(34,211,238,0.04), transparent);
      pointer-events: none;
    }}

    thead th {{
      background: #0f0f11;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.7rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #71717a;
      border-bottom: 1px solid #27272a;
    }}

    /* Pulse dot */
    @keyframes pulse-dot {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50%       {{ opacity: 0.5; transform: scale(0.8); }}
    }}
    .pulse-dot {{ animation: pulse-dot 2s ease-in-out infinite; }}

    /* Fade in sections */
    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(16px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .fade-up {{ animation: fadeUp 0.6s ease both; }}
    .fade-up-2 {{ animation: fadeUp 0.6s 0.15s ease both; }}
    .fade-up-3 {{ animation: fadeUp 0.6s 0.3s ease both; }}

    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #18181b; }}
    ::-webkit-scrollbar-thumb {{ background: #3f3f46; border-radius: 3px; }}
  </style>
</head>
<body class="min-h-screen p-6 md:p-10">

  <!-- ── Header ── -->
  <header class="fade-up mb-10">
    <div class="flex flex-col md:flex-row md:items-end gap-4 justify-between">
      <div>
        <p class="font-mono text-xs text-cyan-500 tracking-[0.2em] uppercase mb-1">Finviz Speculative Scanner</p>
        <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight glow-header text-white">
          Market<span class="text-cyan-400">Pulse</span>
        </h1>
        <p class="mt-2 text-zinc-500 text-sm font-mono">
          Price &lt; $20 · Rel Volume &gt; 3x · Change &gt; 5%
        </p>
      </div>
      <div class="text-right">
        <div class="flex items-center justify-end gap-2 mb-1">
          <span class="w-2 h-2 rounded-full bg-emerald-400 pulse-dot"></span>
          <span class="font-mono text-xs text-zinc-400">Ultima actualizare</span>
        </div>
        <p class="font-mono text-sm text-zinc-300">{now_utc}</p>
      </div>
    </div>
  </header>

  <!-- ── Stat Cards ── -->
  <div class="fade-up-2 grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
    <div class="stat-card p-5">
      <p class="font-mono text-[10px] text-zinc-500 uppercase tracking-widest mb-1">Watchlist 16:15</p>
      <p class="text-3xl font-extrabold text-cyan-400">{wl_count}</p>
      <p class="text-xs text-zinc-500 mt-1">candidați</p>
    </div>
    <div class="stat-card p-5">
      <p class="font-mono text-[10px] text-zinc-500 uppercase tracking-widest mb-1">Strong Buy 16:45</p>
      <p class="text-3xl font-extrabold text-emerald-400">{sb_count}</p>
      <p class="text-xs text-zinc-500 mt-1">validate</p>
    </div>
    <div class="stat-card p-5">
      <p class="font-mono text-[10px] text-zinc-500 uppercase tracking-widest mb-1">Filtru Gap</p>
      <p class="text-3xl font-extrabold text-white">&gt; 2%</p>
      <p class="text-xs text-zinc-500 mt-1">minim validare</p>
    </div>
    <div class="stat-card p-5">
      <p class="font-mono text-[10px] text-zinc-500 uppercase tracking-widest mb-1">Rata Selecție</p>
      <p class="text-3xl font-extrabold text-amber-400">{f"{(sb_count/wl_count*100):.0f}%" if wl_count > 0 else "—"}</p>
      <p class="text-xs text-zinc-500 mt-1">din watchlist</p>
    </div>
  </div>

  <!-- ── Disclaimer ── -->
  <div class="fade-up-2 mb-8 px-4 py-3 rounded-lg border border-amber-900/50 bg-amber-950/20 flex gap-3 items-start">
    <span class="text-amber-400 text-lg mt-0.5">⚠</span>
    <p class="text-amber-300/80 text-xs leading-relaxed">
      <strong class="text-amber-300">Disclaimer:</strong> Acest dashboard este doar informativ. Acțiunile speculative cu volum ridicat pot pierde &gt;90% din valoare rapid.
      Indicatorul de risc se bazează pe performanța din ultimul an. Nu reprezintă sfat financiar.
    </p>
  </div>

  <!-- ── Watchlist 16:15 ── -->
  <section class="fade-up-3 mb-10">
    <div class="flex items-center gap-3 mb-4">
      <div class="w-1 h-8 bg-cyan-400 rounded-full"></div>
      <div>
        <h2 class="text-lg font-bold text-white">Watchlist 16:15</h2>
        <p class="text-xs text-zinc-500 font-mono">Scan inițial — candidați speculativi</p>
      </div>
      <span class="ml-auto font-mono text-xs bg-zinc-800 border border-zinc-700 text-zinc-400 px-3 py-1 rounded-full">
        {wl_count} acțiuni
      </span>
    </div>
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr>
              <th class="px-4 py-3 text-left">Ticker</th>
              <th class="px-4 py-3 text-left">Preț</th>
              <th class="px-4 py-3 text-left">Change</th>
              <th class="px-4 py-3 text-left">Gap</th>
              <th class="px-4 py-3 text-left">Rel. Vol</th>
              <th class="px-4 py-3 text-left">Sector</th>
              <th class="px-4 py-3 text-left">Risc</th>
            </tr>
          </thead>
          <tbody>
            {watchlist_rows(watchlist)}
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- ── Final 16:45 ── -->
  <section class="fade-up-3 mb-10">
    <div class="flex items-center gap-3 mb-4">
      <div class="w-1 h-8 bg-emerald-400 rounded-full"></div>
      <div>
        <h2 class="text-lg font-bold text-white">Validări Finale 16:45</h2>
        <p class="text-xs text-zinc-500 font-mono">Gap &gt; 2% menținut · trend pozitiv confirmat</p>
      </div>
      <span class="ml-auto font-mono text-xs bg-emerald-950 border border-emerald-800 text-emerald-400 px-3 py-1 rounded-full">
        {sb_count} STRONG BUY
      </span>
    </div>
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr>
              <th class="px-4 py-3 text-left">Ticker</th>
              <th class="px-4 py-3 text-left">Preț</th>
              <th class="px-4 py-3 text-left">Change</th>
              <th class="px-4 py-3 text-left">Gap</th>
              <th class="px-4 py-3 text-left">Rel. Vol</th>
              <th class="px-4 py-3 text-left">Sector</th>
              <th class="px-4 py-3 text-left">Risc</th>
            </tr>
          </thead>
          <tbody>
            {final_rows(final)}
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- ── Footer ── -->
  <footer class="border-t border-zinc-800 pt-6 mt-10">
    <div class="flex flex-col md:flex-row gap-2 justify-between items-center text-xs text-zinc-600 font-mono">
      <span>MarketPulse · powered by Finviz + GitHub Actions</span>
      <span>Generat automat · {now_utc}</span>
    </div>
  </footer>

</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Dashboard generat → {OUTPUT_FILE}")
    print(f"   Watchlist: {wl_count} | Strong Buy: {sb_count}")


if __name__ == "__main__":
    generate_html()
