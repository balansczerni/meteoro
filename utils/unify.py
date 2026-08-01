# Normalizuj format daty i czasu na
# YYYY-MM-DD HH:MM:SS
#
# Upewnij się, że zmienne (2 kolumna) są poprawnie znormalizowane. (0.2 a nie 0,2)
# wylistyj poprzez pront każdą zmianę którą wykonujesz w tym zakresie.
#
# Przykład:
# Lublinek opady: 2009-06-27 06:00,0.3
# Lublinek temp: 2026-05-18 21:10,10.5 ALE TEŻ 2009-05-28 06:00,13,7
# KWSP opady: 2025-04-04 17:00:00,0
# KWSP temp: 2026-04-04 22:00:00,6.8
# Patio opady: 31.01.2025 00:00:00,2.6
# Patio temp: 01.06.2025 00:00:00,20.6
# Baluty opady: 2026-06-30 18:00:00,0
# Baluty temp: 2025-05-04 19:00:00,11.7

import os

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_path = os.path.join(PROJECT_ROOT, "data")
output_path = os.path.join(PROJECT_ROOT, "data", "unified")

def main():

    os.makedirs(output_path, exist_ok=True)

    for file in os.listdir(data_path):
        file_path = os.path.join(data_path, file)
        if not os.path.isfile(file_path):
            continue
        print(f"Processing {file_path}")
        with open(file_path, 'r') as f, open(os.path.join(output_path, file), 'w') as out:
            for line in f:
                if not line.strip():
                    continue
                # Convert 0,2 to 0.2 with convert_comma_to_dot()
                line = convert_comma_to_dot(line)
                # check data and time with get_data_time_part()
                data_time = get_data_time_part(line)
                data_part = get_data_part(data_time)
                time_part = get_time_part(data_time)
                #print(f"Data part: {data_part}, Time part: {time_part}")
                data_part = flip_ddmmyyyy(data_part)
                #print(f"Flipped data part: {data_part}")
                time_part = change_hhmm_to_hhmmss(time_part)
                #print(f"Flipped time part: {time_part}")
                # Reconstruct line with flipped data and time parts
                line = f"{data_part} {time_part},{','.join(line.split(',')[1:]).strip()}"
                # Write line to output file
                out.write(line + '\n')
        print("Done.")

    sort_csv_lines(output_path)


    # Zamiast kończyć cicho, zwracamy komunikat do main.py.
    return "Unifikacja zakończona. Znormalizowane pliki są w katalogu data/unified."



# Detect 0,2 values in second column and convert , to .
# How to get 13,7 from line 2009-05-28 06:00,13,7?
def convert_comma_to_dot(line):
    parts = line.split(',')
    if len(parts) == 3:
        #print(f"Converting {parts[0]},{parts[1]},{parts[2]} to {parts[0]},{parts[1]}.{parts[2]}")
        return f"{parts[0]},{parts[1]}.{parts[2]}"
    return line

# Get data part from line
def get_data_time_part(line):
    parts = line.split(',')
    return parts[0]

# get data from line_part
def get_data_part(line_part):
    parts = line_part.split(' ')
    return parts[0]

# get time part from line_part
def get_time_part(line_part):
    parts = line_part.split(' ')
    return parts[1]

# Detect DD.MM.YYYY
def detect_ddmmyyyy(data_part):
    return data_part.count('.') == 2

def detect_hhmm(time_part):
    return time_part.count(':') == 1

# Change HH:MM to HH:MM:SS
def change_hhmm_to_hhmmss(time_part):
    if detect_hhmm(time_part):
        #print(f"Changing {time_part} to {time_part}:00")
        return f"{time_part}:00"
    return time_part

# Flip DD.MM.YYYY to YYYY-MM-DD
def flip_ddmmyyyy(data_part):
    data_part = get_data_part(data_part)
    if detect_ddmmyyyy(data_part):
        #print(f"Flipping {data_part} to {data_part[6:10]}-{data_part[3:5]}-{data_part[0:2]}")
        return f"{data_part[6:10]}-{data_part[3:5]}-{data_part[0:2]}"
    return data_part

# Posortuj linie w pliku CSV od najmniej do największej
def sort_csv_lines(files_dir):
    for file_name in os.listdir(files_dir):
        file_path = os.path.join(files_dir, file_name)
        with open(file_path, 'r') as f:
            lines = f.readlines()
        lines.sort()
        with open(file_path, 'w') as f:
            f.writelines(lines)


if __name__ == "__main__":
    print(main())
