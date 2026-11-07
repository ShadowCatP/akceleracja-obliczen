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

1. **Wymagania wstępne:**
   - Zainstalowany kompilator C++ obsługujący standard C++17 lub nowszy (np. `g++`).
   - Narzędzie `make` (opcjonalnie).

2. **Kompilacja i uruchomienie:**
   Utwórz katalog na pliki wynikowe i skompiluj program za pomocą polecenia:

   ```bash
   mkdir -p build
   g++ main.cpp -o build/main
   ./build/main
   ```

   lub za pomocą skryptu (nie zapomnij o nadaniu praw do wykonywania `chmod +x ./build.sh`)

   ```bash
   ./build.sh
   ```
