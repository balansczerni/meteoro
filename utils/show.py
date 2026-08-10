import json
import os

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(PROJECT_ROOT, "data", "common_time_stamps")
output_path = os.path.join(PROJECT_ROOT, "export")

# Stacje używane do obliczania średniej referencyjnej.
STACJE_REF = ["BALUTY", "KWSP", "LUBLINEK"]
STACJE_BL  = ["BALUTY", "LUBLINEK"]  # bez KWSP


def main():
    os.makedirs(output_path, exist_ok=True)
    for prefix, unit in [("opady", "mm"), ("temperatury", "°C")]:
        rows = build_rows(prefix)

        # Podsumowanie zawyżeń/zaniżeń per stacja
        refs = ["Średnia (B+K+L)", "Średnia (B+L)"] if prefix == "opady" else ["Średnia (B+K+L)"]
        counts = build_summary_counts(rows, refs)
        save_summary_html(counts, prefix, refs)
        print(f"Zapisano: {prefix}_podsumowanie.html")
        save_summary_chart(counts, prefix, refs)
        print(f"Zapisano: {prefix}_podsumowanie_wykres.html")

        save_html(rows, prefix, unit)
        print(f"Zapisano: {prefix}.html")

        save_chart_patio_vs_avg(rows, prefix, unit)
        print(f"Zapisano: {prefix}_patio_vs_srednia.html")

        save_chart_diff(rows, prefix, unit, "Średnia (B+K+L)", "Średnia (B+K+L)")
        print(f"Zapisano: {prefix}_diff_patio_vs_srednia.html")

        if prefix == "opady":
            save_line_chart(rows, prefix, unit, "Średnia (B+L)", "Średnia (B+L)",
                            "opady_patio_vs_srednia_bez_kwsp.html")
            print("Zapisano: opady_patio_vs_srednia_bez_kwsp.html")
            save_chart_diff(rows, prefix, unit, "Średnia (B+L)", "Średnia (B+L)",
                            out_name="opady_diff_patio_vs_srednia_bez_kwsp.html")
            print("Zapisano: opady_diff_patio_vs_srednia_bez_kwsp.html")



        for stacja in STACJE_REF:
            save_chart_patio_vs_station(rows, prefix, unit, stacja)
            print(f"Zapisano: {prefix}_patio_vs_{stacja.lower()}.html")

            save_chart_diff(rows, prefix, unit, stacja, stacja)
            print(f"Zapisano: {prefix}_diff_patio_vs_{stacja.lower()}.html")

    return "Zapisano tabele i wykresy w katalogu export/."


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


# Formatuje odchylenie: +0.00 i -0.00 zamienia na 0, reszta ze znakiem.
def fmt_deviation(val, fmt, suffix=""):
    if val is None:
        return ""
    rounded = round(val, int(fmt.strip("f.")))
    if rounded == 0:
        return f"0{suffix}"
    return f"{val:{'+' + fmt}}{suffix}"


# Buduje listę wierszy dla danego prefixu (opady / temperatury).
def build_rows(prefix):
    data = {s: load_file(prefix, s) for s in STACJE_REF}
    patio = load_file(prefix, "PATIO")

    all_dates = sorted(
        set().union(*[set(d.keys()) for d in data.values()], set(patio.keys()))
    )

    rows = []
    for date in all_dates:
        values = [data[s].get(date) for s in STACJE_REF]
        valid = [v for v in values if v is not None]
        avg = sum(valid) / len(valid) if valid else None
        patio_val = patio.get(date)
        deviation_pct = (
            (patio_val - avg) / abs(avg) * 100
            if (patio_val is not None and avg is not None and avg != 0)
            else None
        )
        deviation_abs = (
            patio_val - avg
            if (patio_val is not None and avg is not None)
            else None
        )

        # Średnia B+L (bez KWSP)
        valid_bl = [v for s, v in zip(STACJE_REF, values) if s != "KWSP" and v is not None]
        avg_bl = sum(valid_bl) / len(valid_bl) if valid_bl else None
        dev_abs_bl = patio_val - avg_bl if (patio_val is not None and avg_bl is not None) else None
        dev_pct_bl = (
            (patio_val - avg_bl) / abs(avg_bl) * 100
            if (patio_val is not None and avg_bl is not None and avg_bl != 0)
            else None
        )

        row = {
            "Data": date,
            "BALUTY": round(values[0], 2) if values[0] is not None else "",
            "KWSP": round(values[1], 2) if values[1] is not None else "",
            "LUBLINEK": round(values[2], 2) if values[2] is not None else "",
            "Średnia (B+K+L)": round(avg, 2) if avg is not None else "",
            "Średnia (B+L)": round(avg_bl, 2) if avg_bl is not None else "",
            "PATIO": round(patio_val, 2) if patio_val is not None else "",
            "PATIO odch.": fmt_deviation(deviation_abs, ".2f"),
            "PATIO % odch.": fmt_deviation(deviation_pct, ".1f", suffix="%"),
            "PATIO odch. (B+L)": fmt_deviation(dev_abs_bl, ".2f"),
            "PATIO % odch. (B+L)": fmt_deviation(dev_pct_bl, ".1f", suffix="%"),
        }

        # Odchylenia każdej stacji od średniej B+K+L i B+L
        for s, s_val in zip(STACJE_REF, values):
            for ref_avg, suffix in [(avg, "(B+K+L)"), (avg_bl, "(B+L)")]:
                d_abs = s_val - ref_avg if (s_val is not None and ref_avg is not None) else None
                d_pct = (
                    (s_val - ref_avg) / abs(ref_avg) * 100
                    if (s_val is not None and ref_avg is not None and ref_avg != 0)
                    else None
                )
                row[f"{s} odch. {suffix}"]   = fmt_deviation(d_abs, ".2f")
                row[f"{s} % odch. {suffix}"] = fmt_deviation(d_pct, ".1f", suffix="%")

        rows.append(row)
    return rows





# Zapisuje tabelę jako samodzielny plik HTML.
def save_html(rows, prefix, unit):
    # Kolumny odchyleń stacji od średniej
    if prefix == "opady":
        stacja_dev_cols = [
            col
            for s in STACJE_REF
            for suffix in ["(B+K+L)", "(B+L)"]
            for col in [f"{s} odch. {suffix}", f"{s} % odch. {suffix}"]
        ]
        col_names = [
            "Data", "BALUTY", "KWSP", "LUBLINEK",
            "Średnia (B+K+L)", "Średnia (B+L)",
            "PATIO",
            "PATIO odch.", "PATIO % odch.",
            "PATIO odch. (B+L)", "PATIO % odch. (B+L)",
        ] + stacja_dev_cols
    else:
        stacja_dev_cols = [
            col
            for s in STACJE_REF
            for col in [f"{s} odch. (B+K+L)", f"{s} % odch. (B+K+L)"]
        ]
        col_names = [
            "Data", "BALUTY", "KWSP", "LUBLINEK",
            "Średnia (B+K+L)",
            "PATIO",
            "PATIO odch.", "PATIO % odch.",
        ] + stacja_dev_cols

    # Wyciągamy każdą kolumnę jako listę wartości (Plotly tego wymaga).
    cell_values = [[row[col] for row in rows] for col in col_names]

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
            fill_color="white",
            font=dict(color="black", size=12, family="monospace"),
            align=align,
            height=24,
        ),
    )])

    fig.update_layout(
        title=f"{prefix.capitalize()} [{unit}]",
        margin=dict(l=10, r=10, t=50, b=10),
    )

    # Dane dla JS — wszystkie kolumny zapamiętane by móc je filtrować po stronie klienta.
    post_script = """
var _H = {headers};
var _C = {cells};
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
  lbl.appendChild(document.createTextNode('\u00a0' + m.label));
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
    'cells.align':   [idx.map(function(i) {{ return _A[i]; }})
    ],
  }});
}}
""".format(
        headers=json.dumps(col_names),
        cells=json.dumps(cell_values),
        align=json.dumps(align),
        meta=json.dumps([{"i": i, "label": c} for i, c in enumerate(col_names)]),
    )

    out_file = os.path.join(output_path, f"{prefix}.html")
    fig.write_html(out_file, include_plotlyjs="cdn", div_id="table-plot", post_script=post_script)


# Generyczny wykres liniowy: PATIO vs dowolna kolumna referencyjna.
def save_line_chart(rows, prefix, unit, ref_col, ref_name, filename):
    dates = [r["Data"] for r in rows]
    patio = [r["PATIO"] if r["PATIO"] != "" else None for r in rows]
    ref_vals = [r[ref_col] if r[ref_col] != "" else None for r in rows]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=ref_vals, name=ref_name, mode="lines"))
    fig.add_trace(go.Scatter(x=dates, y=patio, name="PATIO", mode="lines"))
    fig.update_layout(
        title=f"{prefix.capitalize()} [{unit}] — PATIO vs {ref_name}",
        xaxis_title="Data",
        yaxis_title=unit,
    )
    fig.write_html(os.path.join(output_path, filename), include_plotlyjs="cdn")


# Wykres liniowy: PATIO vs Średnia (B+K+L)
def save_chart_patio_vs_avg(rows, prefix, unit):
    dates = [r["Data"] for r in rows]
    patio = [r["PATIO"] if r["PATIO"] != "" else None for r in rows]
    avg = [r["Średnia (B+K+L)"] if r["Średnia (B+K+L)"] != "" else None for r in rows]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=avg, name="Średnia (B+K+L)", mode="lines"))
    fig.add_trace(go.Scatter(x=dates, y=patio, name="PATIO", mode="lines"))
    fig.update_layout(
        title=f"{prefix.capitalize()} [{unit}] — PATIO vs Średnia",
        xaxis_title="Data",
        yaxis_title=unit,
    )
    out_file = os.path.join(output_path, f"{prefix}_patio_vs_srednia.html")
    fig.write_html(out_file, include_plotlyjs="cdn")


# Wykres liniowy: PATIO vs jedna stacja referencyjna
def save_chart_patio_vs_station(rows, prefix, unit, station):
    dates = [r["Data"] for r in rows]
    patio = [r["PATIO"] if r["PATIO"] != "" else None for r in rows]
    stacja_vals = [r[station] if r[station] != "" else None for r in rows]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=stacja_vals, name=station, mode="lines"))
    fig.add_trace(go.Scatter(x=dates, y=patio, name="PATIO", mode="lines"))
    fig.update_layout(
        title=f"{prefix.capitalize()} [{unit}] — PATIO vs {station}",
        xaxis_title="Data",
        yaxis_title=unit,
    )
    out_file = os.path.join(output_path, f"{prefix}_patio_vs_{station.lower()}.html")
    fig.write_html(out_file, include_plotlyjs="cdn")


# Wykres różnicowy: dwa subploty.
# Góra: linie PATIO i referencji. Dół: słupki różnicy (PATIO − referencja).
def save_chart_diff(rows, prefix, unit, ref_col, ref_name, out_name=None):
    dates = [r["Data"] for r in rows]
    patio_vals = [r["PATIO"] if r["PATIO"] != "" else None for r in rows]
    ref_vals   = [r[ref_col] if r[ref_col] != "" else None for r in rows]

    diff = [
        p - r if (p is not None and r is not None) else None
        for p, r in zip(patio_vals, ref_vals)
    ]
    bar_colors = [
        "rgba(231, 76, 60, 0.7)" if (d is not None and d > 0) else
        "rgba(39, 174, 96, 0.7)" if (d is not None and d < 0) else
        "rgba(150, 150, 150, 0.4)"
        for d in diff
    ]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.06,
        subplot_titles=(f"PATIO vs {ref_name}", f"Różnica (PATIO − {ref_name}) [{unit}]"),
    )

    # Góra: linie
    fig.add_trace(go.Scatter(x=dates, y=ref_vals,   name=ref_name, mode="lines"), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=patio_vals, name="PATIO",   mode="lines"), row=1, col=1)

    # Dół: słupki różnicy
    fig.add_trace(go.Bar(
        x=dates, y=diff,
        name="Różnica",
        marker_color=bar_colors,
        showlegend=False,
    ), row=2, col=1)

    fig.update_yaxes(title_text=unit, row=1, col=1)
    fig.update_yaxes(title_text=unit, row=2, col=1)
    fig.update_xaxes(title_text="Data", row=2, col=1)
    fig.update_layout(
        title=f"{prefix.capitalize()} [{unit}] — PATIO vs {ref_name}",
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        bargap=0,
    )

    if out_name:
        out_file = os.path.join(output_path, out_name)
    else:
        slug = ref_name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("+", "")
        out_file = os.path.join(output_path, f"{prefix}_diff_patio_vs_{slug}.html")
    fig.write_html(out_file, include_plotlyjs="cdn")


# Zlicza dni, w których pomiar stacji był zawyżony/zaniżony względem średnich
# referencyjnych. Zwraca {stacja: {ref: (zawyżone, zaniżone)}}.
def build_summary_counts(rows, refs):
    stations = STACJE_REF + ["PATIO"]
    counts = {}
    for s in stations:
        counts[s] = {}
        for ref in refs:
            high = low = 0
            for r in rows:
                sv = r[s]
                rv = r[ref]
                if sv == "" or rv == "":
                    continue  # brak pomiaru lub brak referencji
                if float(sv) > float(rv):
                    high += 1
                elif float(sv) < float(rv):
                    low += 1
            counts[s][ref] = (high, low)
    return counts


# Dwie małe tabele HTML: liczba dni (zawyżone/zaniżone) oraz proporcje procentowe.
def save_summary_html(counts, prefix, refs):
    stations = STACJE_REF + ["PATIO"]

    def table(headers, rows):
        html = '<table style="border-collapse:collapse;font-family:sans-serif;font-size:13px;margin-bottom:24px">'
        html += '<tr>' + ''.join(
            f'<th style="background:#2c3e50;color:#fff;padding:6px 14px;border:1px solid #bbb">{h}</th>'
            for h in headers
        ) + '</tr>'
        for row in rows:
            html += '<tr>' + ''.join(
                f'<td style="padding:4px 14px;border:1px solid #bbb;text-align:right">{c}</td>'
                for c in row
            ) + '</tr>'
        return html + '</table>'

    rows_counts = []
    rows_pct = []
    for s in stations:
        row_counts = [s]
        row_pct = [s]
        for ref in refs:
            high, low = counts[s][ref]
            row_counts.append(high)
            row_counts.append(low)
            total = high + low
            if total:
                row_pct.append(f"{high / total * 100:.1f}% / {low / total * 100:.1f}%")
            else:
                row_pct.append("—")
        rows_counts.append(row_counts)
        rows_pct.append(row_pct)

    ref_labels = [ref.split("(")[1][:-1] for ref in refs]
    headers_counts = ["Stacja"] + [
        c for label in ref_labels for c in [f"Zawyżone ({label})", f"Zaniżone ({label})"]
    ]
    headers_pct = ["Stacja"] + [f"Zawyżone / Zaniżone ({label})" for label in ref_labels]

    title = f"{prefix.capitalize()} — zawyżenia/zaniżenia"
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{title}</title></head>
<body style="font-family:sans-serif;padding:24px;max-width:900px">
<h2 style="margin-top:0">{prefix.capitalize()} — liczba dni z zawyżonym/zaniżonym pomiarem</h2>
{table(headers_counts, rows_counts)}
<h2>{prefix.capitalize()} — proporcje procentowe (zawyżone / zaniżone)</h2>
{table(headers_pct, rows_pct)}
</body></html>"""

    out_file = os.path.join(output_path, f"{prefix}_podsumowanie.html")
    with open(out_file, "w") as f:
        f.write(page)


# Wykres: 100% skumulowane poziome słupki — stosunek zawyżeń do zaniżeń per stacja.
def save_summary_chart(counts, prefix, refs):
    stations = STACJE_REF + ["PATIO"]
    ref_labels = [ref.split("(")[1][:-1] for ref in refs]

    categories = []
    low_vals, high_vals = [], []
    low_text, high_text = [], []
    for s in stations:
        for ref, label in zip(refs, ref_labels):
            high, low = counts[s][ref]
            total = high + low
            hp = high / total * 100 if total else 0
            lp = low / total * 100 if total else 0
            categories.append(f"{s} ({label})")
            low_vals.append(lp)
            high_vals.append(hp)
            low_text.append(f"{lp:.0f}%" if total else "brak danych")
            high_text.append(f"{hp:.0f}%" if total else "")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=categories, x=low_vals, name="Zaniżone", orientation="h",
        marker_color="#27ae60", text=low_text, textposition="inside",
        textfont=dict(color="white", size=12),
    ))
    fig.add_trace(go.Bar(
        y=categories, x=high_vals, name="Zawyżone", orientation="h",
        marker_color="#e74c3c", text=high_text, textposition="inside",
        textfont=dict(color="white", size=12),
    ))
    fig.update_layout(
        title=f"{prefix.capitalize()} — stosunek dni zawyżonych do zaniżonych (% dni z porównaniem)",
        xaxis=dict(title="% dni", range=[0, 100]),
        barmode="stack",
        height=120 + 50 * len(categories),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.write_html(os.path.join(output_path, f"{prefix}_podsumowanie_wykres.html"), include_plotlyjs="cdn")


if __name__ == "__main__":
    print(main())
