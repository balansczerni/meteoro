from math import e
import os
from turtle import right

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_path = os.path.join(PROJECT_ROOT, "data" , "common_range")
output_path = os.path.join(PROJECT_ROOT, "data", "common_time_stamps")


def main():
    for file in os.listdir(data_path):
        if file.startswith("temperatury"):
            transform_na_dane_dobowe(file, "avg")
        elif file.startswith("opady"):
            transform_na_dane_dobowe(file, "sum")
        else:
            raise ValueError(f"Invalid file: {file}. Please define avg or sum operation in common_time_stamps.py")
    return "Zakończono przetwarzanie plików do formatu dobowego."


# wyciągamy średnią dobową albo sumę dobową w zależności od argumentu
# (przekazujemy plik)
def transform_na_dane_dobowe(file, type):
    day_list = get_unique_days(file)
    if type == "avg":
        data = avg(file, day_list)
        save(file, data)
    elif type == "sum":
        data = sum(file, day_list)
        save(file, data)
    else:
        raise ValueError("Invalid type")
    return print(f"Processed: {file} ({type})")

# suma dobowa (przekazujemy plik i listę dni)
def sum(file, days_list):
    lines_to_save = []
    for date in days_list:
        date_sum = 0
        with open(os.path.join(data_path, file), "r") as f:
            lines = f.readlines()
            for line in lines:
                if date in line:
                    date_sum += float(line.split(",")[1])
            lines_to_save.append(f"{date[0:10]},{date_sum}\n")
    return lines_to_save

# średnia dobowa
def avg(file, days_list):
    lines_to_save = []
    for date in days_list:
        date_sum = 0
        count = 0
        with open(os.path.join(data_path, file), "r") as f:
            lines = f.readlines()
            for line in lines:
                if date in line:
                    date_sum += float(line.split(",")[1])
                    count += 1
            if count > 0:
                lines_to_save.append(f"{date[0:10]},{date_sum / count}\n")
    return lines_to_save

# zapisz plik do katalogu output_path (data to lista)
def save(file, data):
    os.makedirs(output_path, exist_ok=True)
    data.sort()
    with open(os.path.join(output_path, file), "w") as f:
        f.writelines(data)

# wyciągnij listę uniklanych dni (YYYY-MM-DD HH:MM:SS) z pliku
def get_unique_days(file):
    with open(os.path.join(data_path, file), "r") as f:
        lines = f.readlines()
        days_list = [line.split(",")[0] for line in lines]
        return list(set(days_list))

if __name__ == "__main__":
    print(main())
