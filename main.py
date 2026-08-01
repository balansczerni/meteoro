# Plik typu TUI który w zależności od podanej opcji wykonuje różne zadania
# 1. Pobierz dane (download)
# 2. Wypakuj pliki (unpack)
# 3. Wyciągnij dane (extract)
# 4. Unifikuj dane (unify)
# 5. Wyciągnij wspólny zakres (common range)
# 6. Transformuj dane (transform)

# Importujemy moduły z katalogu utils - każdy z nich realizuje jedno zadanie.
from utils import common_time_stamps, common_range, download, extract, show, unify, unpack

# Słownik łączący numer opcji z opisem zadania i funkcją, która je wykonuje.
OPCJE = {
    "1": ("Pobierz dane", download.main),
    "2": ("Wypakuj pliki", unpack.main),
    "3": ("Wyciągnij istotne dane", extract.main),
    "4": ("Unifikuj dane", unify.main),
    "5": ("Wyciągnij wspólny zakres", common_range.main),
    "6": ("Ujednolić częstotliowść pomiarów", common_time_stamps.main),
    "7": ("Pokaż dane", show.main),
}

def main():
    # Pętla menu - program działa dopóki użytkownik nie wybierze opcji 0.
    while True:
        print("\n--- CO CHCESZ ZROBIĆ? ---")
        for numer, (opis, _) in OPCJE.items():
            print(f"{numer}. {opis}")
        print("0. Wyjdź")

        wybor = input("\nWybierz opcję: ").strip()

        if wybor == "0":
            print("Pozdro.")
            break

        if wybor not in OPCJE:
            print("Nieznana opcja. Spróbuj ponownie.")
            continue

        opis, funkcja = OPCJE[wybor]
        print(f"\n--- {opis.upper()} ---")
        # Każdy moduł zwraca komunikat o wyniku zamiast kończyć program.
        print(funkcja())


if __name__ == "__main__":
    main()
