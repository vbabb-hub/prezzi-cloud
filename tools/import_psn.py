"""Converte il listino del Polo Strategico Nazionale (file Excel) in collectors/psn_listino.json, che legge collectors/psn.py.

Uso:   pip install openpyxl
       python tools/import_psn.py "Listino_Polo_Strategico_Nazionale_Release_agosto_2026_Excel.xlsx"
Ogni volta che il PSN pubblica una nuova release basta rilanciarlo con il nuovo file e caricare il JSON aggiornato nel repo.
Fogli letti: "Industry Standard-Integrazione" (catalogo completo), "Hybrid Cloud on PSN site" e "Listino_Servizi_Professionali".
Non letti: i cataloghi dei servizi dei grandi provider rivenduti dal PSN (Secure Public Cloud Oracle, GCP, Azure, AWS e Public Cloud PSN
Managed: decine di migliaia di righe per singola SKU)."""
import json, re, sys, datetime, pathlib
import openpyxl

OUT = pathlib.Path(__file__).resolve().parent.parent / "collectors" / "psn_listino.json"
COLS = {"FAMIGLIA": "fam", "SOTTO-FAMIGLIA": "sub", "MAPPATURA SU TIPOLOGIA": "tip", "ELEMENTO": "el", "TIER": "tier",
        "LISTINO DI PARTENZA": "listino", "CARATTERISTICHE": "desc", "METRICA (UNITÀ": "mu", "METRICA (VALORE": "mv", "CANONE ANNUALE": "canone",
        "UT": "ut", "CORE": "core", "RAM": "ram", "VCPU": "vcpu", "VRAM": "vram", "STORAGE": "storage"}


def clean(v, n=None):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    t = re.sub(r"\s+", " ", str(v)).strip()
    if not t:
        return None
    return t[:n] if n else t


def read_sheet(ws, key_header, cols):
    """Righe di un foglio come dizionari, usando i nomi delle colonne dell'intestazione (non le posizioni)."""
    header_row, idx = None, {}
    for r in range(1, 12):
        vals = [re.sub(r"\s+", " ", str(c.value or "")).strip().upper() for c in ws[r]]
        if any(v.startswith(key_header) for v in vals):
            header_row = r
            for i, v in enumerate(vals):
                for prefix, name in cols.items():
                    if v.startswith(prefix) and name not in idx.values():
                        idx[i] = name
                        break
            break
    if header_row is None:
        raise SystemExit(f"intestazione '{key_header}' non trovata nel foglio {ws.title}")
    rows = []
    for r in ws.iter_rows(min_row=header_row + 1, values_only=True):
        rows.append({name: clean(r[i], 260 if name == "desc" else None) for i, name in idx.items() if i < len(r)})
    return rows


def main(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    out = {"file": pathlib.Path(path).name, "imported": datetime.date.today().isoformat()}
    m = re.search(r"[Rr]elease[_ ]([A-Za-zàèé]+)[_ ](\d{4})", pathlib.Path(path).name)
    out["release"] = f"{m.group(1)} {m.group(2)}" if m else "non indicata"
    out["industry"] = [d for d in read_sheet(wb["Industry Standard-Integrazione"], "FAMIGLIA", COLS) if d.get("fam")]
    hyb = {"TIPOLOGIA": "tip", "ELEMENTO": "el", "LISTINO DI PARTENZA": "listino", "CORE": "core", "RAM": "ram", "VCPU": "vcpu", "VRAM": "vram",
           "STORAGE": "storage", "CANONE ANNUALE": "canone"}
    out["hybrid"] = [d for d in read_sheet(wb["Hybrid Cloud on PSN site"], "TIPOLOGIA", hyb) if d.get("tip") and d.get("canone") is not None]
    prof = {"TIPOLOGIA": "tip", "FIGURA": "fig", "LISTINO DI PARTENZA": "listino", "ATTIVIT": "att", "UT": "ut"}
    out["servizi"] = [d for d in read_sheet(wb["Listino_Servizi_Professionali"], "TIPOLOGIA", prof) if d.get("fig") and isinstance(d.get("ut"), (int, float))]
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{OUT.name}: release {out['release']}, {len(out['industry'])} righe Industry Standard, {len(out['hybrid'])} Hybrid Cloud, {len(out['servizi'])} servizi professionali")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
