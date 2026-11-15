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

- CMake 3.15 lub nowszy.
- Kompilator C++ obsługujący standard C++17.
- CUDA Toolkit z kompilatorem `nvcc` wymagany do budowania i uruchamiania algorytmu `cuda`.
- Na Windows: Visual Studio z obsługą C++.
- Na Linux: kompilator C++ oraz `make` lub Ninja.

#### **Konfiguracja środowiska**

Skrypt konfiguracyjny sprawdza wymagane narzędzia i ustawia ścieżkę do hooków Git.

Na Bash/Linux lub Git Bash uruchom:

```bash
./setup.sh
```

Na Windows Command Prompt uruchom:

```bat
setup.bat
```

Hook `pre-commit` formatuje zmienione pliki C++, a następnie buduje projekt, jeśli commit zawiera kod źródłowy lub pliki CMake. Dla Bash używany jest `.githooks/pre-commit`, a dla Windows `.githooks/pre-commit.bat`.

Konfiguracja ręczna w Bash:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

Konfiguracja ręczna w Windows:

```bat
git config core.hooksPath .githooks
```

#### **Kompilacja i uruchomienie:**

Skonfiguruj projekt i zbuduj konfigurację Debug za pomocą CMake:

```bash
cmake -S . -B build
cmake --build build --config Debug
```

Na Windows uruchom program:

```bat
build\Debug\main.exe
```

Na Linux uruchom program:

```bash
./build/main
```

Jeśli używasz CUDA 13.x, projekt domyślnie buduje kod dla architektury CUDA 75.
Możesz ustawić inną obsługiwaną architekturę podczas konfiguracji:

```bash
cmake -S . -B build -DCMAKE_CUDA_ARCHITECTURES=75
```

**Dostępne parametry programu:**

Program przyjmuje następujące opcjonalne flagi:

| Flaga                       | Opis                                                                                                                                                                       |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-a`, `--algorithm <nazwa>` | Wybór algorytmu symulacji (domyślnie: `naive`). Dostępne opcje: `naive`, `avx2`, `avx512`, `cuda`.                                                                         |
| `-n`, `--size <liczba>`     | Długość pręta $N$, min. 3 (domyślnie: `10`).                                                                                                                               |
| `-s`, `--steps <liczba>`    | Liczba kroków czasowych (domyślnie: `5`).                                                                                                                                  |
| `-v`, `--verbose`           | Tryb rozszerzony: wyświetla stan początkowy oraz końcowy pręta.                                                                                                            |
| `-i`, `--improved-formula`  | Używa ulepszonego wzoru na obliczenie temperatury: $u_{\text{next}}[i] = 0.5 \cdot u_{\text{current}}[i] + 0.25 \cdot (u_{\text{current}}[i-1] + u_{\text{current}}[i+1])$ |

**Przykłady użycia:**

```bash
# Uruchomienie z domyślnymi parametrami (naive, N=10, steps=5)
./build/main

# Uruchomienie algorytmu AVX2 dla pręta o rozmiarze 10000 i 1000 krokach
./build/main -a avx2 -n 10000 -s 1000

# Wykonanie algorytmu AVX-512 z wypisaniem wyników (tryb verbose)
./build/main -a avx512 -n 20 -s 10 -v

# Uruchomienie algorytmu CUDA
./build/main -a cuda -n 10000 -s 1000
```
