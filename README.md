# Akceleracja obliczeń – Projekt

- **Termin zajęć:** Środa, godz. 8:15 (Grupa nr 4)
- **Prowadzący:** dr inż. Piotr Dębski

## Skład zespołu

- Bohdan Koshkin (282276)
- Bohdan Stepanenko (283017)
- Nazarii Yasinskyi (280972)

---

## Wybrany temat: 3. Symulacje Fizyczne – Przepływ Ciepła 1D (1D Stencil)

### Opis problemu

Symulacja rozchodzenia się temperatury w jednowymiarowym pręcie o długości $N$ w czasie. Nowa wartość elementu w kroku czasowym $t+1$ zależy od jego bezpośrednich sąsiadów:
$$u_i^{t+1} = 0.5 \cdot (u_{i-1}^t + u_{i+1}^t)$$

### Oczekiwane kroki i zrównoleglenie

- **CPU:**
  - Implementacja bazowa wykorzystująca podwójną pętlę (po czasie oraz po elementach pręta).
  - Zastosowanie techniki podwójnego buforowania (ang. _double buffering_).
- **GPU:**
  - Przypisanie poszczególnych elementów pręta do niezależnych wątków.
  - Wykorzystanie pamięci współdzielonej (ang. _Shared Memory_) do szybkiego lokalnego przechowywania danych sąsiadów.
- **Profilowanie i analiza:**
  - Badanie oraz porównanie przepustowości pasma pamięci przed i po zastosowaniu optymalizacji z użyciem pamięci współdzielonej.

### Jak uruchomić projekt

#### **Wymagania wstępne:**

- Zainstalowany kompilator C++ obsługujący standard C++17 lub nowszy (np. `g++`).
- Narzędzie `make` (opcjonalnie).

#### **Konfiguracja środowiska**

Warto skonfigurować środowisko projektu na jeden z dwóch sposobów:

- **Opcja A: Automatycznie (zalecane)**

  Uruchom przygotowany skrypt konfiguracyjny, który sprawdzi wymagane narzędzia (`git`, `g++`), skonfiguruje ścieżkę do hooków oraz nada odpowiednie uprawnienia:

  ```bash
  ./setup.sh
  ```

- **Opcja B: Ręcznie**

  Jeśli wolisz przeprowadzić konfigurację manualnie, upewnij się, że posiadasz zainstalowane narzędzia `git` oraz `g++`, a następnie wykonaj w terminalu następujące polecenia:

  ```bash
  git config core.hooksPath .githooks
  chmod +x .githooks/pre-commit
  ```

#### **Kompilacja i uruchomienie:**

Utwórz katalog na pliki wynikowe i skompiluj program za pomocą polecenia:

```bash
mkdir -p build
g++ -O2 -c main.cpp -o build/main.o
g++ -O2 -c naive.cpp -o build/naive.o
g++ -O2 -c utils.cpp -o build/utils.o
g++ -O2 -mavx2 -c avx2.cpp -o build/avx2.o
g++ -O2 -mavx512f -c avx512.cpp -o build/avx512.o
g++ build/*.o -o build/main
./build/main
```

lub za pomocą skryptu (nie zapomnij o nadaniu praw do wykonywania `chmod +x ./build.sh`):

```bash
./build.sh
```

**Dostępne parametry programu:**

Program przyjmuje następujące opcjonalne flagi:

| Flaga                       | Opis                                                                                       |
| --------------------------- | ------------------------------------------------------------------------------------------ |
| `-a`, `--algorithm <nazwa>` | Wybór algorytmu symulacji (domyślnie: `naive`). Dostępne opcje: `naive`, `avx2`, `avx512`. |
| `-n`, `--size <liczba>`     | Długość pręta $N$, min. 3 (domyślnie: `10`).                                               |
| `-s`, `--steps <liczba>`    | Liczba kroków czasowych (domyślnie: `5`).                                                  |
| `-v`, `--verbose`           | Tryb rozszerzony: wyświetla stan początkowy oraz końcowy pręta.                            |

**Przykłady użycia:**

```bash
# Uruchomienie z domyślnymi parametrami (naive, N=10, steps=5)
./build.sh

# Uruchomienie algorytmu AVX2 dla pręta o rozmiarze 10000 i 1000 krokach
./build.sh -a avx2 -n 10000 -s 1000

# Wykonanie algorytmu AVX-512 z wypisaniem wyników (tryb verbose)
./build.sh -a avx512 -n 20 -s 10 -v
```
