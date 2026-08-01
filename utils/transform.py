# Używając dash oraz plotly
# 1. Utwórz tabelę która zestawia (w kolumnach) dane z BALUTY, KWSP i LUBLINEK, następnie  średnią z tych 3 stacji i dalej: wynik z PATIO i % odchylenie od średniej PATRIO
# (uwaga, dane czasem są puste). Mamy dwa zbiory danych: opady_nazwastacji.csv oraz temperatury_nazwastacji.csv

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(PROJECT_ROOT, "data", "common_time_stamps")
output_path = os.path.join(PROJECT_ROOT, "export")

def main():
    # Na razie to tylko "zaślepka" - zwracamy komunikat, zamiast kończyć program.
    return "Transformacja: jeszcze nie zaimplementowano."


if __name__ == "__main__":
    print(main())
