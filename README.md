
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
