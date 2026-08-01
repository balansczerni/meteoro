################################################################################
# Importujemy do projektu zewnętrzne biblioteki/moduły, które dodają funkcje,  #
# których domyślny Python w sobie nie ma.                                      #
################################################################################

# "This provides a way of using operating system dependent functionality."
# - https://docs.python.org/3/library/os.html
import os

# "This module provides tools to work with ZIP archives."
# - https://docs.python.org/3/library/zipfile.html
import zipfile

# Katalog główny projektu (rodzic katalogu utils/). Dzięki niemu ścieżki
# działają niezależnie od tego, z którego katalogu uruchomimy program.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

################################################################################
# Defniniujemy funkcje, których chcemy używać w naszym oprogramowaniu.         #
# Python czyta plik od góry do dołu.                                           #
# main() jest naszą główną funkcją - gry uruchamiamy program to ona zostaje    #
# uruchomiona jako pierwsza.                                                   #
################################################################################

def main():
    # Upewniamy się, że katalog data istnieje.
    stworzKatalogData()
    # Pobieramy listę plików do wypakowania.
    pliki = znajdzPlikiZip()
    # Iterujemy przez listę plików i każdy wypakowujemy.
    for plik in pliki:
        wypakuj(plik)

    # Zamiast kończyć program (sys.exit) zwracamy komunikat do main.py.
    return "Wypakowano: " + str(len(pliki)) + " plików."

# Funkcja, która tworzy katalog data jeśli jeszcze nie istnieje.
def stworzKatalogData():
    # Sprawdzamy, czy katalog data już istnieje.
    katalog_data = os.path.join(PROJECT_ROOT, "data")
    if not os.path.exists(katalog_data):
        # Jeśli nie istnieje, to go tworzymy.
        os.makedirs(katalog_data)
        print('Utworzono katalog "data"')

# Funkcja, która przeszukuje katalog import i zwraca listę ścieżek do plików
# .zip oraz .ZIP.
def znajdzPlikiZip():
    # Pusta lista, do której będziemy zapisywać znalezione pliki.
    listaPlikow = []
    # Katalog, w którym szukamy plików zip.
    katalog_import = os.path.join(PROJECT_ROOT, "import")
    # Lista wszystkich plików i folderów w katalogu import.
    zawartosc = os.listdir(katalog_import)
    for element in zawartosc:
        # Sprawdzamy, czy element kończy się na .zip lub .ZIP.
        if element.endswith((".zip", ".ZIP")):
            # Tworzymy pełną ścieżkę: "import/nazwa_pliku.zip"
            pelnaSciezka = os.path.join(katalog_import, element)
            # Dodajemy do listy.
            listaPlikow.append(pelnaSciezka)
            print("ZNALAZŁEM: " + pelnaSciezka)
    return listaPlikow

# Funkcja, która wypakowuje plik zip do katalogu data.
def wypakuj(sciezkaPliku):
    print("WYPAKOWUJĘ: " + sciezkaPliku)
    # Otwieramy plik zip za pomocą modułu zipfile.
    # R oznacza "read" (czytanie) - chcemy tylko czytać zawartość archiwum.
    with zipfile.ZipFile(sciezkaPliku, 'r') as archiwum:
        # Wypakowujemy całą zawartość do katalogu data.
        archiwum.extractall(os.path.join(PROJECT_ROOT, "data"))
    print("Gotowe!")

################################################################################
# Teraz, gdy mamy zapisane już wszystkie funckje, które będą nam potrzebne,    #
# możemy w końcu wywołać te, które mają ruszyć, gry uruchomimy program.        #
# Na razie chcemy by przy każdym uruchomieniu wykonywała się funkcja main().   #
################################################################################

if __name__ == "__main__":
    print(main())
