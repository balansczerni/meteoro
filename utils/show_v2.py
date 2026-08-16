import json
import os

import plotly.graph_objects as go

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(PROJECT_ROOT, "data", "common_time_stamps")
output_path = os.path.join(PROJECT_ROOT, "export/v2")

# Zbiory danych: (prefix, jednostka, stacje)
# Dla opadów NIE używamy KWSP.
DATASETS = [
    ("opady", "mm", ["PATIO", "LUBLINEK", "BALUTY"]),
    ("temperatury", "°C", ["PATIO", "LUBLINEK", "BALUTY", "KWSP"]),
]


def main():
    os.makedirs(output_path, exist_ok=True)
    for prefix, unit, stations in DATASETS:
        rows = build_rows(prefix, stations)

        # Pełna wersja — wszystkie pary uporządkowane (A−B oraz B−A)
        save_html(rows, prefix, unit, stations, ordered_pairs(stations),
                  f"{prefix}_odchylenia.html")
        print(f"Zapisano: {prefix}_odchylenia.html")

        # Mini wersja — każda para stacji tylko raz
        save_html(rows, prefix, unit, stations, unique_pairs(stations),
                  f"{prefix}_odchylenia_mini.html", note=" (pary unikalne)")
        print(f"Zapisano: {prefix}_odchylenia_mini.html")

    return "Zapisano tabele odchyleń w katalogu export/."


# Wczytuje plik CSV i zwraca słownik {data: wartość}.
def load_file(prefix, station):
    filepath = os.path.join(data_path, f"{prefix}_{station}.csv")
    result = {}
    if not os.path.exists(filepath):
        return result
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 2 or parts[1].strip() == "":
                continue
            try:
                result[parts[0]] = float(parts[1])
            except ValueError:
                continue
    return result


# Wszystkie pary uporządkowane: (A−B oraz B−A) dla każdej pary stacji.
def ordered_pairs(stations):
    return [(a, b) for a in stations for b in stations if a != b]


# Każda para stacji tylko raz (kolejność wg listy stacji).
def unique_pairs(stations):
    return [(stations[i], stations[j])
            for i in range(len(stations))
            for j in range(i + 1, len(stations))]


# Formatuje odchylenie: +0.00 i -0.00 zamienia na 0, reszta ze znakiem.
def fmt_deviation(val, fmt, suffix=""):
    if val is None:
        return ""
    rounded = round(val, int(fmt.strip("f.")))
    if rounded == 0:
        return f"0{suffix}"
    return f"{val:{'+' + fmt}}{suffix}"


# Kolor tła komórki odchylenia: + zielony, - czerwony, 0 i brak danych biały.
def deviation_fill(val):
    if isinstance(val, str) and val.startswith("+"):
        return "#d5f5e3"  # jasna zieleń
    elif isinstance(val, str) and val.startswith("-"):
        return "#fadbd8"  # jasna czerwień
    return "white"


# Buduje wiersze: data / pomiar każdej stacji / odchylenie każdej stacji
# w stosunku do każdej innej (pary uporządkowane: "A − B" = wartość A minus wartość B).
def build_rows(prefix, stations):
    data = {s: load_file(prefix, s) for s in stations}

    all_dates = sorted(set().union(*[set(d.keys()) for d in data.values()]))

    rows = []
    for date in all_dates:
        row = {"Data": date}

        # Pomiary stacji
        for s in stations:
            v = data[s].get(date)
            row[s] = round(v, 2) if v is not None else ""

        # Odchylenia wzajemne (każda stacja względem każdej innej)
        for a in stations:
            for b in stations:
                if a == b:
                    continue
                av = data[a].get(date)
                bv = data[b].get(date)
                d = av - bv if (av is not None and bv is not None) else None
                row[f"{a} − {b}"] = fmt_deviation(d, ".2f")

        rows.append(row)
    return rows


# Zapisuje tabelę jako samodzielny plik HTML (z przełącznikami kolumn).
def save_html(rows, prefix, unit, stations, pairs, filename, note=""):
    # Kolumny: data, pomiary, potem odchylenia dla podanych par
    deviation_cols = [f"{a} − {b}" for a, b in pairs]
    col_names = ["Data"] + stations + deviation_cols

    # Wyciągamy każdą kolumnę jako listę wartości (Plotly tego wymaga).
    cell_values = [[row[col] for row in rows] for col in col_names]

    # Kolorowanie tła: pomiary białe, odchylenia zielone/czerwone wg znaku.
    fill_colors = [
        ["white"] * len(rows) if col in stations or col == "Data"
        else [deviation_fill(row[col]) for row in rows]
        for col in col_names
    ]

    align = ["left"] + ["right"] * (len(col_names) - 1)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=col_names,
            fill_color="#2c3e50",
            font=dict(color="white", size=13),
            align="center",
        ),
        cells=dict(
            values=cell_values,
            fill_color=fill_colors,
            font=dict(color="black", size=12, family="monospace"),
            align=align,
            height=24,
        ),
    )])

    fig.update_layout(
        title=f"{prefix.capitalize()} [{unit}] — odchylenia wzajemne{note}",
        margin=dict(l=10, r=10, t=50, b=10),
    )

    # Dane dla JS — wszystkie kolumny zapamiętane by móc je filtrować po stronie klienta.
    post_script = """var _H = {headers};
var _C = {cells};
var _F = {fills};
var _A = {align};
var _meta = {meta};
var _did = "table-plot";

var wrap = document.createElement('div');
wrap.style.cssText = 'display:flex;flex-wrap:wrap;gap:5px;margin:8px 4px 14px;align-items:center;font-family:sans-serif;font-size:12px';

function mkBtn(label, fn) {{
  var b = document.createElement('button');
  b.textContent = label;
  b.style.cssText = 'padding:2px 9px;border:1px solid #2c3e50;border-radius:3px;cursor:pointer;background:#2c3e50;color:#fff;font-size:12px';
  b.addEventListener('click', fn);
  return b;
}}

wrap.appendChild(mkBtn('Wszystkie', function() {{
  document.querySelectorAll('.ctog').forEach(function(cb) {{ cb.checked = true; }});
  redraw();
}}));
wrap.appendChild(mkBtn('Żadna', function() {{
  document.querySelectorAll('.ctog').forEach(function(cb) {{ cb.checked = false; }});
}}));

_meta.forEach(function(m) {{
  var lbl = document.createElement('label');
  lbl.style.cssText = 'display:inline-flex;align-items:center;gap:3px;padding:2px 7px;border:1px solid #ccc;border-radius:3px;cursor:pointer;background:#f8f9fa;user-select:none';
  var cb = document.createElement('input');
  cb.type = 'checkbox'; cb.className = 'ctog'; cb.value = m.i; cb.checked = true;
  cb.addEventListener('change', redraw);
  lbl.appendChild(cb);
  lbl.appendChild(document.createTextNode('\\u00a0' + m.label));
  wrap.appendChild(lbl);
}});

var plotDiv = document.getElementById(_did);
plotDiv.parentNode.insertBefore(wrap, plotDiv);

function redraw() {{
  var idx = Array.from(document.querySelectorAll('.ctog:checked')).map(function(cb) {{ return +cb.value; }});
  if (!idx.length) return;
  Plotly.restyle(_did, {{
    'header.values': [idx.map(function(i) {{ return _H[i]; }})],
    'cells.values':  [idx.map(function(i) {{ return _C[i]; }})],
    'cells.fill.color': [idx.map(function(i) {{ return _F[i]; }})],
    'cells.align':   [idx.map(function(i) {{ return _A[i]; }})
    ],
  }});
}}
""".format(
        headers=json.dumps(col_names),
        cells=json.dumps(cell_values),
        fills=json.dumps(fill_colors),
        align=json.dumps(align),
        meta=json.dumps([{"i": i, "label": c} for i, c in enumerate(col_names)]),
    )

    out_file = os.path.join(output_path, filename)
    fig.write_html(out_file, include_plotlyjs="cdn", div_id="table-plot", post_script=post_script)


if __name__ == "__main__":
    print(main())
