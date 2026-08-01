import csv
import os
from concurrent.futures import ProcessPoolExecutor

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Z data-raw/LUBLINEK/
# B00300S;Temperatura powietrza (oficjalna);stopień Celsjusza
# B00604S;Suma opadu dobowego;milimetr
# >> na razie pomijamy << B00606S;Suma opadu godzinowego;milimetr
#
# Z data-raw/BALUTY.csv i data-raw/KWSP.csv
# Tempertura to kolumna 6
# Opady to kolumna 13
#
# Z data-raw/PATIO.csv
# Temperatura to kolumna 6
# Opady to kolumna 12

# Pliki i ścieżki (względem katalogu głównego projektu)
baluty_file = os.path.join(PROJECT_ROOT, "data-raw", "BALUTY.csv")
kwsp_file = os.path.join(PROJECT_ROOT, "data-raw", "KWSP.csv")
patio_file = os.path.join(PROJECT_ROOT, "data-raw", "PATIO.csv")
lublinek_path = os.path.join(PROJECT_ROOT, "data-raw", "LUBLINEK")

# Kolumny (-1 bo indeksowanie od 0)
kolumna_daty_KBP = 0
kolumna_opadow_KB = 12
kolumna_opadow_P = 11
kolumna_temperatury_KBP = 5
kolumna_ID_stacji = 0
kolumna_daty_lublinek = 2
kolumna_zmiennej_lublinek = 3

# Exportuj dane do folderu data (bez "raw")
export_path = os.path.join(PROJECT_ROOT, "data")

# Lublinek codes:
lublinek_stacja_code = "351190465"
lublinek_code_temperatura = "B00300S"
lublinek_code_opady_dobowe = "B00604S"
#lublinek_code_opady_godzinowe = "B00606S"

def main():

    # KWSP
    lines_to_write = extract_data_from_columns(kolumna_daty_KBP, kolumna_opadow_KB, kwsp_file)
    create_csv_from_list(lines_to_write, "opady_KWSP.csv")
    lines_to_write = extract_data_from_columns(kolumna_daty_KBP, kolumna_temperatury_KBP, kwsp_file)
    create_csv_from_list(lines_to_write, "temperatury_KWSP.csv")

    print("Finished extracting data from KWSP.")

    # Baluty
    lines_to_write = extract_data_from_columns(kolumna_daty_KBP, kolumna_opadow_KB, baluty_file)
    create_csv_from_list(lines_to_write, "opady_BALUTY.csv")
    lines_to_write = extract_data_from_columns(kolumna_daty_KBP, kolumna_temperatury_KBP, baluty_file)
    create_csv_from_list(lines_to_write, "temperatury_BALUTY.csv")

    print("Finished extracting data from BALUTY.")

    # Patio
    lines_to_write = extract_data_from_columns(kolumna_daty_KBP, kolumna_opadow_P, patio_file)
    create_csv_from_list(lines_to_write, "opady_PATIO.csv")
    lines_to_write = extract_data_from_columns(kolumna_daty_KBP, kolumna_temperatury_KBP, patio_file)
    create_csv_from_list(lines_to_write, "temperatury_PATIO.csv")

    print("Finished extracting data from PATIO.")

    # Dla Lublinek
    lines_to_write = extract_data_from_lublinek(lublinek_code_opady_dobowe)
    create_csv_from_list(lines_to_write, "opady_LUBLINEK.csv")
    lines_to_write = extract_data_from_lublinek(lublinek_code_temperatura)
    create_csv_from_list(lines_to_write, "temperatura_LUBLINEK.csv")

    print("Finished extracting data from LUBLINEK.")

    # Posortuj pliki CSV
    print("Sorting CSV files...")
    sort_csv_lines(export_path)

    # Zamiast kończyć program (sys.exit) zwracamy komunikat do main.py.
    return "Ekstrakcja zakończona. Wyniki zapisano w katalogu data."

# Funkcja wyciągająca dane z kolumny X oraz Y
def extract_data_from_columns(kolumna_daty, kolumna_zmiennej, file):
    print("File " + file)
    dane_z_csv = returnListFromCSV(file, ",", True)
    lista_danych = []
    for row in dane_z_csv:
        # line_to_write as string x, y
        line_to_write = row[kolumna_daty] + "," + row[kolumna_zmiennej] + "\n"
        lista_danych.append(line_to_write)
    return lista_danych

def extract_data_from_lublinek(pomiar_code):
    print("Files starting with " + pomiar_code)
    pliki = [
        os.path.join(lublinek_path, file)
        for file in os.listdir(lublinek_path)
        if file.startswith(pomiar_code)
    ]
    zadania = [
        (plik, lublinek_stacja_code, kolumna_daty_lublinek, kolumna_zmiennej_lublinek)
        for plik in pliki
    ]
    lista_danych = []
    # Kazdy plik jest niezalezny - przetwarzamy je rownolegle na wszystkich rdzeniach.
    # Na 8 rdzeniach to ~5-8x szybciej niz petla po kolei.
    with ProcessPoolExecutor() as executor:
        for lublinek_file, dane in executor.map(_extract_lublinek_file, zadania):
            lista_danych.extend(dane)
            #print("Processed " + os.path.basename(lublinek_file))

    #print(lista_danych)
    return lista_danych

# Przetwarza JEDEN plik LUBLINEK (wykonywane w procesie potomnym).
# Filtrujemy po kodzie stacji na surowej linii ZANIM cokolwiek sparsujemy -
# w plikach sa dane wszystkich stacji IMGW, a nas interesuje tylko jedna.
# Czytamy linia po linii zamiast wczytywac caly plik do pamieci.
def _extract_lublinek_file(zadanie):
    lublinek_file, stacja_code, kol_daty, kol_zmiennej = zadanie
    dane = []
    with open(lublinek_file) as current_file:
        for line in current_file:
            if not line.startswith(stacja_code + ";"):
                continue
            row = line.rstrip("\n").split(";")
            dane.append(row[kol_daty] + "," + row[kol_zmiennej] + "\n")
    return lublinek_file, dane

# Zwraca listę z danymi z pliku CSV
def returnListFromCSV(file, podziałka=",", ignore_header=False):
    with open(file) as current_file:
        datafromcsv =  list(csv.reader(current_file, delimiter=podziałka))
        if ignore_header:
            datafromcsv = datafromcsv[1:]
        return datafromcsv

# Tworzy plik CSV z danymi
def create_csv_from_list(lines_to_write, filename):
    out_path = os.path.join(export_path, filename)
    with open(out_path, "w") as export_file:
        export_file.writelines(lines_to_write)
    print(f"Exported to {out_path}")
    return out_path

# Posortuj linie w pliku CSV od najmniej do największej
def sort_csv_lines(files_dir):
    for file in os.listdir(files_dir):
        if not file.endswith(".csv"):
            continue
        file_path = os.path.join(files_dir, file)
        data = returnListFromCSV(file_path)
        data.sort()
        # returnListFromCSV zwraca listę list - trzeba je z powrotem złożyć w linie tekstu
        data = [",".join(row) + "\n" for row in data]
        create_csv_from_list(data, file)

if __name__ == "__main__":
    print(main())
