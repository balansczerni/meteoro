import os

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_path = os.path.join(PROJECT_ROOT, "data" , "unified")
output_path = os.path.join(PROJECT_ROOT, "data", "common_range")

def main():
    groups = detect_file_groups()
    for group_name in groups:
        print(f"Zakres dla grupy {group_name}:")
        group = [filename for filename in os.listdir(data_path) if filename.startswith(group_name)]
        print(f"  pliki: {group}")
        min_date, max_date = find_common_range(group)
        print(f"min_date: {min_date}, max_date: {max_date}")
        save_common_range(group_name, min_date, max_date)
    return f"Wspólny zakres wyznaczony i zapisany w {output_path}."


# Chcemy skopiować pliki z data/unified/ do data/common_range/ ale tylko te linie, które są częścią wspólnego zakresu
def save_common_range(group_name, min_date, max_date):
    for filename in os.listdir(data_path):
        if filename.startswith(group_name):
            filepath = os.path.join(data_path, filename)
            croped_range_file_path = os.path.join(output_path, filename)
            with open(filepath, "r") as f:
                lines = f.readlines()
                with open(croped_range_file_path, "w") as f:
                    for line in lines:
                        date, _ = get_date_time(line)
                        if min_date <= date <= max_date:
                            f.write(line)
                print(f"Zapisano pliki do {croped_range_file_path}")
    print(f"Zakończono {group_name} ({min_date} - {max_date})  ")

# detect files groups in data/unified/
# each group contains files with the same name (e.g. temperatury_<station>.csv)
# group is defined by common prefix (before the first underscore)
def detect_file_groups():
    filenames = os.listdir(data_path)
    groups = []
    for filename in filenames:
        prefix = filename.split("_")[0]
        if prefix not in groups:
            groups.append(prefix)
    return groups

# find common range for each group
# wspólny zakres = przecięcie wszystkich zakresów:
#   min_date = max z minimów każdego pliku
#   max_date = min z maksimów każdego pliku
def find_common_range(group):
    min_date = None
    max_date = None
    for filename in group:
        file_path = os.path.join(data_path, filename)
        min_date_file, max_date_file = detect_min_max_date(file_path)
        if min_date is None or min_date_file > min_date:
            min_date = min_date_file
        if max_date is None or max_date_file < max_date:
            max_date = max_date_file
    return min_date, max_date

# detect min and max date from file
def detect_min_max_date(file_path):
    min_date = None
    max_date = None
    with open(file_path, "r") as f:
        for line in f:
            date, _ = get_date_time(line)
            if min_date is None or date < min_date:
                min_date = date
            if max_date is None or date > max_date:
                max_date = date
    return min_date, max_date

# get date and time from line
# line format: <date> <time>, <value>
# ex: 2009-05-06 06:00:00,0.01
def get_date_time(line):
    data_time_part = line.strip().split(",")[0]
    date, time = data_time_part.split(" ")
    return date, time

if __name__ == "__main__":
    print(main())
