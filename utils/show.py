import os

import plotly.graph_objects as go

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(PROJECT_ROOT, "data", "common_time_stamps")
output_path = os.path.join(PROJECT_ROOT, "export")

# Stacje używane do obliczania średniej referencyjnej.
STACJE_REF = ["BALUTY", "KWSP", "LUBLINEK"]


def main():
    os.makedirs(output_path, exist_ok=True)
    for prefix, unit in [("opady", "mm"), ("temperatury", "°C")]:
        rows = build_rows(prefix)

        save_html(rows, prefix, unit)
        print(f"Zapisano: {prefix}.html")

        save_chart_patio_vs_avg(rows, prefix, unit)
        print(f"Zapisano: {prefix}_patio_vs_srednia.html")

        for stacja in STACJE_REF:
            save_chart_patio_vs_station(rows, prefix, unit, stacja)
            print(f"Zapisano: {prefix}_patio_vs_{stacja.lower()}.html")

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

        rows.append({
            "Data": date,
            "BALUTY": round(values[0], 2) if values[0] is not None else "",
            "KWSP": round(values[1], 2) if values[1] is not None else "",
            "LUBLINEK": round(values[2], 2) if values[2] is not None else "",
            "Średnia (B+K+L)": round(avg, 2) if avg is not None else "",
            "PATIO": round(patio_val, 2) if patio_val is not None else "",
            "PATIO odch.": fmt_deviation(deviation_abs, ".2f"),
            "PATIO % odch.": fmt_deviation(deviation_pct, ".1f", suffix="%"),
        })
    return rows





# Zapisuje tabelę jako samodzielny plik HTML.
def save_html(rows, prefix, unit):
    col_names = ["Data", "BALUTY", "KWSP", "LUBLINEK", "Średnia (B+K+L)", "PATIO", "PATIO odch.", "PATIO % odch."]

    # Wyciągamy każdą kolumnę jako listę wartości (Plotly tego wymaga).
    cell_values = [[row[col] for row in rows] for col in col_names]

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
            align=["left"] + ["right"] * (len(col_names) - 1),
            height=24,
        ),
    )])

    fig.update_layout(
        title=f"{prefix.capitalize()} [{unit}]",
        margin=dict(l=10, r=10, t=50, b=10),
    )

    out_file = os.path.join(output_path, f"{prefix}.html")
    fig.write_html(out_file, include_plotlyjs="cdn")


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


if __name__ == "__main__":
    print(main())
