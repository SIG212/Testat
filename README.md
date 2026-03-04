# 📈 MarketPulse — Finviz Speculative Scanner

Dashboard automat pentru scanarea acțiunilor speculative de pe piața americană.

## Logica de scanare

| Ora (RO) | Ora (UTC) | Acțiune |
|----------|-----------|---------|
| **16:15** | 13:15 | Scan inițial — Price < $20, Rel.Vol > 3x, Change > 5% |
| **16:45** | 13:45 | Validare — Gap > 2% menținut + trend pozitiv → **STRONG BUY** |

## Setup

### 1. Fork / clone repo

```bash
git clone https://github.com/USER/finviz-scanner.git
cd finviz-scanner
```

### 2. Activează GitHub Pages

`Settings → Pages → Source: Deploy from branch → Branch: main → / (root)`

Dashboard-ul va fi live la: `https://USER.github.io/finviz-scanner/`

### 3. Activează GitHub Actions

Workflow-ul rulează automat Luni–Vineri la orele setate.
Pentru test manual: `Actions → Finviz Scanner → Run workflow → mode: both`

### 4. (Opțional) Finviz Elite

Dacă primești erori de rate-limiting frecvente, setează:
```
Settings → Secrets → FINVIZ_API_KEY = <cheia_ta>
```
Și modifică în `scanner.py` să folosești API-ul oficial.

## Rulare locală

```bash
pip install -r requirements.txt

# Scan 16:15
python scanner.py scan

# Validare 16:45
python scanner.py validate

# Generare dashboard
python generate_html.py

# Deschide index.html în browser
```

## Structura fișierelor

```
├── scanner.py          # Logica de scanare + validare
├── generate_html.py    # Generator dashboard HTML
├── index.html          # Dashboard (generat automat)
├── requirements.txt
├── data/
│   ├── watchlist_1615.json   # Candidați 16:15
│   └── final_1645.json       # STRONG BUY 16:45
└── .github/
    └── workflows/
        └── main.yml    # GitHub Actions
```

## Indicatorul de risc

| Badge | Criteriu |
|-------|---------|
| ✓ LOW | 52W Change > -30% |
| ◆ MEDIUM | 52W Change între -30% și -60% |
| ▲ HIGH | 52W Change între -60% și -90% |
| ⚠ EXTREME | 52W Change < -90% (acțiune quasi-falimentară) |

## ⚠️ Disclaimer

Acest tool este **exclusiv informativ**. Nu reprezintă sfat de investiții.
Acțiunile speculative cu volum ridicat sunt **extrem de volatile** și pot pierde
100% din valoare în ore. Folosește pe propria răspundere.
