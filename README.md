# meteoro

Uczymy się Pythona poprzez tworzenie programu do pobierania i analizy danych.

Źródła: 
* [https://danepubliczne.imgw.pl/pl/datastore](https://danepubliczne.imgw.pl/pl/datastore)
* wewnętrzne pliki typu excel

## Potrzebne oprogramowanie:

* [UV](https://docs.astral.sh/uv/) - wraper wokół Pythona - czyli sposób, by z niego łatwiej korzystać 
* [git](https://git-scm.com/install/windows) - synchronizowanie zmian i wersji plików (na razie się tym nie przejmuj)
* edytor kodu - np. [ZED](https://zed.dev/download)

## Komendy które do tej pory wykonywaliśmy:

Do uruchamiania naszego programu:
```
uv run main.py
```

Do zainstalowania zewnętrznej biblioteki użyliśmy.
```
uv pip install requests
```

Ale mogliśmy też zrobić:
```
uv add requests
```

## Na wuj mi UV?

Jeśli masz na komputerze Pythona, to zamiast `uv run main.py` możesz wykonać po prostu `python3 main.py` i wyjedzie na to samo.

Podobnie z PIP (package installer for Python). Zamiast `uv pip install x` można byłoby wywołać `pip install x`.

**Problemy:** 
* Python (i PIP) ciągle się rozwija (kolejne wersje). 
* Tak samo biblioteki które dodajemy mogą się zmieniać. 
* Jeśli wszystko trzymamy bezpośrednio "na Windowsie" to szybko możemy mieć z tym burdel. 
* Poza tym - jeśli chcesz uruchomić program na innym komputerze, to musisz z głowy znów instalować wszystkie zależności (aka zewnętrzne biblioteki).
 
Z własnego doświadczenia: program *może i działa teraz*, ale za pół roku coś zaktualizujesz i już nie będzie.

Dlatego lecimy z UV, który rozwiązuje za nas te wszystkie problemy (stąd projekcie mamy pliki `uv.lock`, `pyproject.toml`, czy `.python-version`, które są plikami konfiguracyjnymi / informacjami dla UV jak ma działać w tym projekcie.) Poza tym jest też szybszy. :)

## Czego się nauczyliśmy?

1. Python czyta plik od góry do dołu. Kolejność jest ważna. Zanim wywołacz funkcje (np. `main()`) musisz ją zefiniować poprzez `def main():`.
2. Wcięcia są istotne. Mówią nam one czy dana linijka programu jest częścią jakiejś pętli czy funkcji, czy jest na tym samym poziomie co ona.
3. Jeśli domyślnie python czegoś nie ma, to możemy dodać do niego więcej funkcji poprzez zewnętrzne biblioteki i moduły (`import x`).
4. Możemy zapisywać dane do zmiennych, by mieć do nich szybki i prosty dostęp (i się nie powtarzać). `x = 10`, `y = "tekst"`, `z = [1, 2, 3, 4]` etc.
5. Poznaliśmy różne rodzaje danych:
  * `string` - czyli tekst (musi być w cudzysłowach)
  * `int` - liczba całkowita (np. 42)
  * `list` - lista (w kwadratowych nawiasach)
  * wiemy też, że są inne rodzaje danych z którymi się jeszcze nie bawiliśmy (`dict`, `bool` itd.)
6. Poznaliśmy podstawowe operacje na danych. Np. `+`. Możemy za pomocą tego łączyć tekst (`"a" + "b"` da na `"ab"`), albo dodawać liczby (`1 + 2` da na `3`).
7. Wiemy, że większość operacji musi odbywać się na danych tego samego typu (nie możemy dodawać `1` i `"tekst"`). 
8. Możemy zmieniać typ danych. Np. sprawić by 10 (`int`) stało się "10" (`str`) poprzez wbudowaną funkcję `str(10)`.
9. Inną wbudowaną funckją jest `len()`, które mówi nam jak jest długość danego obiektu (np. ile liter ma `"tekst"`).
10. Dowiedzieliśmy się, że gdy definiujemy funckje, możemy przekazywać do niej dane (nazywamy je "argumentami"). `def nazwa_funkcji(argument1, argument2):`. Takie argumenty są dostępne wewnątrz funkcji jako zmienne.
11. Gdy wywołujemy naszą funkcję to mozemy przekazać do niej dane albo bezpośrednio (`nazwa_funkcji("2010", "01")`), albo pośrednio poprzez zmienne (`nazwa_funkcji(rok, msc)`).
12. Niektórym fragmentom kodu możemy postawić warunek, by działy się tylko wtedy gdy warunek jest spełniony. Robimy to przez `if`. Np. `if x > 1:` (i w następnej linijce, **po wcięciu** piszemy co ma się w tym przypadku wstać).
13. Poznaliśmy też pętle (loop). Zaczynamy ją poprzez `for`. Mówimy wtedy, że iterujemy przez jakieś elementy. Np. elementy w liście (`for x in [1, 2, 3]:`). Co więcej - wewnątrz pętli możemy używać tego `x` który w danym momencie jest aktualnie przetwarzany.
