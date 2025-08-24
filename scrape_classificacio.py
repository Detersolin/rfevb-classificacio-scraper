# -*- coding: utf-8 -*-
"""
Scraper de classificació RFEVB -> CSV local per a OBS
- Intenta primer el microsite DataProject (HTML més “net”).
- Si falla, prova la pàgina de rfevb.com.
- Escriu: C:\Overlay\classificacio.csv i un TOP-3 a classificacion_top3.txt
Executa-ho periòdicament amb el Task Scheduler.
"""

import time
import os
import pandas as pd
import requests

OUT_DIR = r"C:\Overlay"
CSV_OUT = os.path.join(OUT_DIR, "classificacio.csv")
TOP3_TXT = os.path.join(OUT_DIR, "classificacio_top3.txt")

# 👉 Quan surti la temporada nova, pot canviar l'ID (136 és un exemple de temporada anterior)
URLS = [
    "https://rfevb-web.dataproject.com/CompetitionHome.aspx?ID=136",
    "https://www.rfevb.com/superliga-femenina-2-grupo-b-clasificacion",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def pick_standing_table(tables):
    """Escull la taula que sembli classificació (pos, equip, punts...)."""
    KEYWORDS = ["pos", "equ", "team", "pt", "punt", "points", "pj", "jug"]
    best = None
    best_score = -1
    for df in tables:
        cols = [str(c).strip().lower() for c in df.columns]
        score = sum(any(k in c for k in KEYWORDS) for c in cols)
        if score > best_score:
            best = df
            best_score = score
    return best

def fetch_table():
    for url in URLS:
        try:
            html = requests.get(url, headers=HEADERS, timeout=20).text
            tables = pd.read_html(html)  # detecta totes les taules HTML
            if not tables:
                continue
            df = pick_standing_table(tables) or tables[0]
            df = df.dropna(how="all")
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception:
            continue
    return None

def save_outputs(df):
    os.makedirs(OUT_DIR, exist_ok=True)
    # CSV
    df.to_csv(CSV_OUT, index=False, encoding="utf-8-sig")
    # TOP-3 text (per OBS Text GDI+)
    top = df.head(3).copy()
    cols = list(top.columns)
    lines = []
    for _, r in top.iterrows():
        pos   = str(r.get(cols[0], "")).strip()
        equip = str(r.get(cols[1], "")).strip()
        punts = str(r.get(cols[-1], "")).strip()
        lines.append(f"{pos} - {equip} ({punts})")
    with open(TOP3_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main_loop(poll_seconds=300):
    while True:
        try:
            df = fetch_table()
            if df is not None and not df.empty:
                save_outputs(df)
        except Exception:
            pass
        time.sleep(poll_seconds)

if __name__ == "__main__":
    main_loop(300)  # cada 5 minuts
