import csv
from datetime import datetime_CAPI
import os
import sys

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


def main():
    # Pliki i ścieżki
    files = ["data/BALUTY.csv", "data/KWSP.csv"]
    patio_file = "data/PATIO.csv"
    export_path = "export"

    # Lublinek codes:
    lublinek_stacja_code = "351190465"
    lublinek_code_opady = "B00604S"
    lublinek_code_opady_godzinowe = "B00606S"
    lublinek_code_temperatura = "B00300S"

    # Wyciągamy dane z samych opadów
    # Dla KWSP i Baluty
    for file in files:
        przerobnadobowe(file, export_path, "opady")
    # Dla Patio
    opadyzpatio(patio_file, export_path)
    # Dla Lublinek
    lublinek_menager(lublinek_stacja_code,lublinek_code_opady, "opady", export_path)

    sys.exit("END")


def lublinek_menager(lublinek_stacja_code, pomiar_code, pomiar_name, export_path):
    # For file in data, find file starting with code.
    data_to_process = []
    filename = pomiar_name + ".csv"
    out_path = os.path.join(export_path, filename)

    for file in os.listdir("data"):
        if file.startswith(pomiar_code):
            print("Processing file: " + file)
            lublinek_file = os.path.join("data/", file)
            dane_z_csv = returnListFromCSV(lublinek_file, ";")
            for row in dane_z_csv:
                # print(row)
                # print(lublinek_stacja_code)
                # print(row[0])
                if row[0] == lublinek_stacja_code:
                    dzien = row[2]
                    opady = row[3]
                    day_data = [dzien[0:10],  opady]
                    print(day_data)
                    data_to_process.append(day_data)

    lines_to_write = []
    for day in data_to_process:
        lines_to_write.append(f"{day[0]},{day[1]}\n")

    with open(out_path, "w") as export_file:
        export_file.writelines(lines_to_write)

    return print("Exported to: " + out_path)



def opadyzpatio(file, export_path):
    dane_z_csv = returnListFromCSV(file)

    lista_dni = []
    for row in dane_z_csv[1:]:
        data = row[0]
        data = data[0:10]
        if data not in lista_dni:
            lista_dni.append(data)

    opady_list = []
    for dzien in lista_dni:
        #print("SPRAWDZAMY OPADY Z " + dzien)
        opady_tego_dnia = 0
        for row in dane_z_csv[1:]:
            data = row[0]
            opady = row[11]
            if data[0:10] == dzien:
                opady_tego_dnia += float(opady)
        #print(opady_tego_dnia)
        # convert dzien to DD.MM.YYYY to YYYY-MM-DD
        dzien = dzien[6:10] + "-" + dzien[3:5] + "-" + dzien[0:2]
        day_data = [dzien, round(opady_tego_dnia, 2)]
        opady_list.append(day_data)

    filename = "opadydobowe_" + os.path.basename(file)
    out_path = os.path.join(export_path, filename)
    lines_to_write = []
    for day in opady_list:
        lines_to_write.append(f"{day[0]},{day[1]}\n")

    with open(out_path, "w") as export_file:
        export_file.writelines(lines_to_write)

    return


def przerobnadobowe(file, export_path, type):

    if type == "opady":
        list_of_opady_per_day = przerobnadobowe_opady(file)
        filename = "opadydobowe_" + os.path.basename(file)
        out_path = os.path.join(export_path, filename)
        lines_to_write = []
        for day in list_of_opady_per_day:
            lines_to_write.append(f"{day[0]},{day[1]}\n")

        with open(out_path, "w") as export_file:
            export_file.writelines(lines_to_write)

    if type == "":
        pass

def przerobnadobowe_opady(file):
    dane_z_csv = returnListFromCSV(file)

    lista_dni = []
    for row in dane_z_csv[1:]:
        data = row[0]
        data = data[0:10]
        if data not in lista_dni:
            lista_dni.append(data)

    opady_list = []
    for dzien in lista_dni:
        #print("SPRAWDZAMY OPADY Z " + dzien)
        opady_tego_dnia = 0
        for row in dane_z_csv[1:]:
            data = row[0]
            opady = row[12]
            if data[0:10] == dzien:
                opady_tego_dnia += float(opady)
        #print(opady_tego_dnia)
        day_data = [dzien, round(opady_tego_dnia, 2)]
        opady_list.append(day_data)

    #print(opady_list)
    return opady_list

def returnListFromCSV(file, podziałka=","):
    with open(file) as current_file:
        return list(csv.reader(current_file, delimiter=podziałka))



if __name__ == "__main__":
    main()
