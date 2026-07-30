from calendar import c
import csv
from inspect import getfile
import os
from random import sample
import sys
from this import s
from tracemalloc import start

# B00300S;Temperatura powietrza (oficjalna);stopień Celsjusza
# B00604S;Suma opadu dobowego;milimetr
# B00606S;Suma opadu godzinowego;milimetr
#
#
# opady to 13 w baluty i kwsp
# opady to 12 w patio

# 1. jaka jest różnica % między Bałuty, Kwsp, Lublinek
# 2. chcemy przerobić parametry z Bałuty i Kwsp na dobowe
# 3. chcemy zebrac pliki z parametru opad dobowy razem
# 4. wyciągnąć dane dla stacji Lublinek - kod stacji 351190465
# 5.zebrać to w jednym pliku
#
#
# 0. retrospektywnie zabezpiecy sie przed waroacia 999 (Lublinkowe dane)
# 1. wyciągnij temperature z PAtrIo,
# 2. wyciagnij temperatury z KwSP, BALUTY
# 3. wyciagnj temperwature zze stacji lublinek
# (pytanie - czy pomiat temparatury LUBLINKA to srednia dobowa czy pomiar o godzinie 6:00 /// w zależnosci od tego bedzie nas interesowaly inne dane z 3 powyzszychstacji)
# 4. przygotowac sie na patio godzinowe
#
# #### Tabela (4 tabele) prównujące każdy parametr dla każdej
# kolumny stacje + średnia (z 3 stacji - Bałuty, Kwsp, lublinek) + różnica między patio a średnią
# wiersze datas
# komorki wartosci
#
# (czy ktoraz z 3 wiarygodnych stacji ma wieksze odchylenia niz uystawa przewiduje)
#
# WYKRESY >
# 1. liniowy całoścowy (powinien pokazywac takie same kreski mniej wiecej) (debug)
# 2. Pytanie jak wizualizować odchylenia



# Pliki i ścieżki
files = ["data/BALUTY.csv", "data/KWSP.csv"]
patio_file = "data/PATIO.csv"
export_path = "export"

# Lublinek codes:
lublinek_stacja_code = "351190465"
lublinek_code_opady = "B00604S"
lublinek_code_opady_godzinowe = "B00606S"
lublinek_code_temperatura = "B00300S"

def main():

    # Dla KWSP i Baluty
    for file in files:
        #  Wyciągamy dane z samych opadów
        list_of_opady_per_day = przerobnadobowe(file, 12)
        filename = "opadydobowe_" + os.path.basename(file)
        lines_to_write = create_lines_from_list(list_of_opady_per_day)
        create_csv_from_list(lines_to_write, filename)
    # Dla Patio
    patio_menager(11, "opadydobowe", "day")
    # Dla Lublinek
    lublinek_menager(lublinek_code_opady, "opadydobowe", "day")
    lublinek_menager(lublinek_code_opady_godzinowe, "opadygodzinowe", "day_and_time")
    lublinek_menager(lublinek_code_temperatura, "temperatura", "day_and_time")

    sys.exit("END")


def patio_menager(kolumna_zmiennej, pomiar_name, date_time_format="day"):
    dane_z_csv = returnListFromCSV(patio_file, ",", True)
    lista_czasu = None
    filename = pomiar_name + "_PATIO.csv"
    if date_time_format == "day":
        lista_dni = create_date_list(dane_z_csv, 0)
        lista_czasu = lista_dni
    elif date_time_format == "day_and_time":
        lista_godzin = create_hour_list(dane_z_csv, 0)
        lista_czasu = lista_godzin
    else:
        return sys.exit("Invalid date_time_format in patio_menager: " + date_time_format)
    zmienna_list = []
    for czas in lista_czasu:
        opady_tego_dnia = 0
        opady_tego_dnia = sum_x_from_day(kolumna_zmiennej, czas, dane_z_csv)
        if date_time_format == "day":
            day_data = [transfrorm_date_to_yyyy_mm_dd(czas), round(opady_tego_dnia, 2)]
        elif date_time_format == "day_and_time":
            day_data = [transfrorm_date_and_time_to_yyyy_mm_dd_hh_mm_ss(czas), round(opady_tego_dnia, 2)]
        else:
            return sys.exit("Invalid date_time_format in patio_menager: " + date_time_format)
        zmienna_list.append(day_data)
    lines_to_write = create_lines_from_list(zmienna_list)
    create_csv_from_list(lines_to_write, filename)
    return print("Done.")


def lublinek_menager(pomiar_code, pomiar_name, date_time_format="day"):
    # For file in data, find file starting with code.
    filename = pomiar_name + "_LUBLINEK.csv"
    out_path = os.path.join(export_path, filename)
    data_to_process = []
    for file in os.listdir("data"):
        if file.startswith(pomiar_code):
            print("Processing file: " + file)
            lublinek_file = os.path.join("data/", file)
            dane_z_csv = returnListFromCSV(lublinek_file, ";", True)
            for row in dane_z_csv:
                if row[0] == lublinek_stacja_code:
                    dzien = get_date(row[2])
                    zmienna = row[3]
                    if date_time_format == "day":
                        day_data = [dzien[0:10],  zmienna]
                    elif date_time_format == "day_and_time":
                        day_data = [dzien[0:18], zmienna]
                    else:
                        return sys.exit("You have to pass valid date_time_format to lublinek_menager.")
                    data_to_process.append(day_data)
    lines_to_write = create_lines_from_list(data_to_process)
    create_csv_from_list(lines_to_write, filename)
    return print("Exported to: " + out_path)


def przerobnadobowe(file, kolumna_zmiennej):
    dane_z_csv = returnListFromCSV(file, ",", True)
    lista_dni = create_date_list(dane_z_csv, 0)
    zmienna_list = []
    for dzien in lista_dni:
        opady_tego_dnia = 0
        opady_tego_dnia = sum_x_from_day(kolumna_zmiennej, dzien, dane_z_csv)
        day_data = [dzien, round(opady_tego_dnia, 2)]
        zmienna_list.append(day_data)
    return zmienna_list

# Sumuje wartości z kolumny X dla danego dnia
def sum_x_from_day(kolumna_zmiennej, target_day, dane_z_csv, kolumna_dnia=0):
    suma_x = 0
    for row in dane_z_csv:
        data = get_date(row[kolumna_dnia])
        if data == target_day:
            suma_x += float(row[kolumna_zmiennej])
    return suma_x

# Zwraca listę z danymi z pliku CSV
def returnListFromCSV(file, podziałka=",", ignore_header=False):
    with open(file) as current_file:
        datafromcsv =  list(csv.reader(current_file, delimiter=podziałka))
        if ignore_header:
            datafromcsv = datafromcsv[1:]
        return datafromcsv

# data_list to lines_to_write
def create_lines_from_list(data_list):
    lines_to_write = []
    for item in data_list:
        lines_to_write.append(f"{item[0]},{item[1]}\n")
    return lines_to_write

# Tworzy plik CSV z danymi
def create_csv_from_list(lines_to_write, filename):
    out_path = os.path.join(export_path, filename)
    with open(out_path, "w") as export_file:
        export_file.writelines(lines_to_write)
    print(f"Exported to {out_path}")
    return out_path

# Tworzymy listę dat (doby) z danych z CSV
def create_date_list(dane_z_csv, date_column=0):
    lista_dni = []
    for row in dane_z_csv:
        cell = row[date_column]
        data = get_date(cell)
        if data not in lista_dni:
            lista_dni.append(data)
    return lista_dni

# Tworzymy listę dat (z podziałem na godziny) z danych CSV
def create_hour_list(dane_z_csv, date_column=0):
    lista_dni_i_godzin = []
    for row in dane_z_csv:
        cell = row[date_column]
        data = get_date_and_time(cell)
        if data not in lista_dni_i_godzin:
            lista_dni_i_godzin.append(data)
    return lista_dni_i_godzin

def get_date(cell):
    # data ma format YYYY-MM-DD albo DD.MM.YYYY
    return cell[0:10]

def get_date_and_time(date_and_time):
    # czas ma format YYYY-MM-DD HH:MM:SS albo DD.MM.YYYY HH:MM:SS
    return date_and_time[0:18]

# Zabezpieczamy się przed nieprawidłowymi danymi oraz brakującymi danymi
def validate_data_cell(cell):
    if cell == "" or cell == "999" or cell == 999:
        print(f"Znaleziono nieprawidłowoą wartość komórki: {cell}")
        return 0.0
    return float(cell)

# Przekształcamy DD.MM.YYYY na YYYY-MM-DD
def transfrorm_date_to_yyyy_mm_dd(date):
    # Sprawdzamy czy 3 znak jest cyfrą
    if date[2].isdigit() == False:
        print(f"Przekształcamy datę: {date}")
        return date[6:] + "-" + date[3:5] + "-" + date[0:2]
    return date

# Przekształcamy DD.MM.YYYY na YYYY-MM-DD
def transfrorm_date_and_time_to_yyyy_mm_dd_hh_mm_ss(date_and_time):
    # Sprawdzamy czy 3 znak jest cyfrą
    if date_and_time[2].isdigit() == False:
        print(f"Przekształcamy datę i czas: {date_and_time}")
        return date_and_time[6:] + "-" + date_and_time[3:5] + "-" + date_and_time[0:2] + " " + date_and_time[11:]
    return date_and_time

if __name__ == "__main__":
    main()
