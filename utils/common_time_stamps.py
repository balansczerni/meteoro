import os

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_path = os.path.join(PROJECT_ROOT, "data", "common_range")
output_path = os.path.join(PROJECT_ROOT, "data", "common_time_stamps")

def main():
    for file in os.listdir(data_path):
        if file.startswith("temperatury"):
            transform_na_dane_dobowe(file, "avg")
        elif file.startswith("opady"):
            transform_na_dane_dobowe(file, "sum")
        else:
            raise ValueError(f"Nieznany plik: {file}. Zdefiniuj operację (avg/sum) w common_time_stamps.py")
    return "Zakończono przetwarzanie plików do formatu dobowego."


# Jeden przebieg po pliku — grupujemy wartości po dacie (YYYY-MM-DD),
# potem liczymy avg lub sum. Bez wielokrotnego otwierania pliku.
def transform_na_dane_dobowe(file, type):
    filepath = os.path.join(data_path, file)

    # Grupujemy wartości po dacie: { "YYYY-MM-DD": [wartość, ...] }
    daily = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 2 or parts[1].strip() == "":
                continue  # pomijamy linie bez wartości
            date = parts[0][:10]  # pierwsze 10 znaków = YYYY-MM-DD
            value = float(parts[1])
            daily.setdefault(date, []).append(value)
    lines_to_save = []
    for date, values in daily.items():
        if type == "avg":
            result = sum(values) / len(values)
        elif type == "sum":
            result = sum(values)
        else:
            raise ValueError(f"Nieznany typ operacji: {type}")
        lines_to_save.append(f"{date},{round(result, 2)}\n")

    save(file, lines_to_save)
    print(f"Processed: {file} ({type})")


# Zapisz posortowany plik do katalogu output_path.
def save(file, data):
    os.makedirs(output_path, exist_ok=True)
    data.sort()
    with open(os.path.join(output_path, file), "w") as f:
        f.writelines(data)


if __name__ == "__main__":
    print(main())
