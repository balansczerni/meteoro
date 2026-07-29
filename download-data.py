################################################################################
# Importujemy do projektu zewnętrzne biblioteki/moduły, które dodają funkcje,  #
# których domyślny Python w sobie nie ma.                                      #
################################################################################

# "Requests is a simple, yet elegant, HTTP library."
# - https://pypi.org/project/requests/
import requests

# "This provides a way of using operating system dependent functionality."
# - https://docs.python.org/3/library/os.html
import os

################################################################################
# Defniniujemy funkcje, których chcemy używać w naszym oprogramowaniu.         #
# Python czyta plik od góry do dołu.                                           #
# main() jest naszą główną funkcją - gry uruchamiamy program to ona zostaje    #
# uruchomiona jako pierwsza.                                                   #
################################################################################

def main():
    x = listAllLinks()
    for link in x:
        downloading(link)
    print(x)
    pass

# Funkcja, która iteruje przez podane przez lata (od 2008 do 2027) i miesiące
# (od 1 do 13), by utworzyć listę linków do pobrania.
def listAllLinks():
    listOffAllLinks = [] # Pusta lista, do której będziemy zapisywać linki.
    for rok in range(2008, 2027):
        rok = str(rok)
        for msc in range(1, 13):
            msc = str(msc)
            # Nasz "hack" - potrzebujemy miesięcy w 2 cyfrowym formacie.
            # Więc jeśli miesiąc jest 1 cyfrowy (1-9) to dodajemy przez nim "0".
            if len(msc) == 1:
                msc = "0" + msc
            # linkcreator(rok,msc) zwróci nam konkretny link ("https://...")
            # zapisujemy go do zmiennej currentLink.
            currentLink = linkcreator(rok,msc)
            # Do listy listOffAllLinks dodajemy świeżo utworzony link.
            listOffAllLinks.append(currentLink)
    return listOffAllLinks

# Nasz menadger pobierania. Ta funkcja jest nam potrzebna, gdyż okazało się,
# że ze względu na błędy w nazewnictwie plików na serwerze danepubliczne.imgw.pl
# niektóre pliki mają format .ZIP, a niektóre .zip. Musimy wykryć "fejkowe"
# pliki, które zwraca nam serwer, gdy prosimy go o plik, który w rzeczywistości
# na nim nie istnieje.
# (Poprawienie skonfigurowany serwer zwróciłby nam bezpośrednio błąd 404).
def downloading(link):
    print("DOWNLOADING: " + link)
    file_Path = realDownloading(link)
    # Sprawdzamy rozmiar pobranego pliku - jeśli jest za mały, to wiemy, że to
    # fejk i musimy bobrać go z końcówką .ZIP (domyślnie nasz link miał .zip)
    size = os.path.getsize(file_Path)
    if size < 300:
        print("CHANGING .zip to .ZIP")
        # Skracamy link o ostatnie 3 znaki - [0:-3] czyli: z tego string'a daj
        # nam wszystko od początku (0), aż do 3 od tyłu znaku (-3).
        # I dodajemy "ZIP"
        link = link[0:-3] + "ZIP"
        # Ponawiamy pobieranie, tym razem właściwego pliku.
        realDownloading(link)

# Funkcja pobierająca i zapisująca plik z linku, który jej dajemy.
def realDownloading(link):
    # Ustalamy nazwę pliku (w tym wypadku wiemy, że chcemy ostatnie 17 znaków).
    file_Name = link[-17:]
    # Ustalamy ścieżkę pod którą chcemy zapisać plik.
    file_Path = "export/" + file_Name
    # Pobieramy plik. Korzystamy tutaj z zewnętrznej biblioteki Requests.
    # Zmienna response zawiera w sobie nie tylko pobrany plik (.content),
    # ale też inne informacje. Np. odpowiedź serwera (.status_code)
    response = requests.get(link)
    if response.status_code == 200:
        # Zapisujemy plik. Czyt. to jak:
        # "Otworz plik za pomocą funckji open()
        # pod ścieżką import/nazwa_pliku.zip
        # daj sobie uprawnienia do zapisywania plików (w - write)
        # i ten plik od tego momentu będzie dla nas dostępny jako zmienna file.
        with open(file_Path, 'wb') as file:
            # Do tego pliku zapisujemy treść, którą mamy z response.content.
            file.write(response.content)
        print('File downloaded successfully')
    else:
        print('Failed to download file')
    return file_Path

# Funkcja budująca link do pobrania danych meteorologicznych. Format:
# https://danepubliczne.imgw.pl/pl/datastore/getfiledown/Arch/Telemetria/Meteo/
# {rok}/Meteo_{rok}-{miesiąc}.zip
def linkcreator(rok, miesiac):
    baseLink = "https://danepubliczne.imgw.pl/pl/datastore/"
    ext1 = "getfiledown/Arch/Telemetria/Meteo/"
    ext2 = "/Meteo_"
    ext3 = ".zip"
    newLink = baseLink + ext1 + rok + ext2 + rok + "-" + miesiac + ext3
    return newLink

################################################################################
# Teraz, gdy mamy zapisane już wszystkie funckje, które będą nam potrzebne,    #
# możemy w końcu wywołać te, które mają ruszyć, gry uruchomimy program.        #
# Na razie chcemy by przy każdym uruchomieniu wykonywała się funkcja main().   #
################################################################################

if __name__ == "__main__":
    main()
