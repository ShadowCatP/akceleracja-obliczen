# Akceleracja obliczeń – Projekt

- **Termin zajęć:** Środa, godz. 8:15 (Grupa nr 4)
- **Prowadzący:** dr inż. Piotr Dębski

## Skład zespołu

- Bohdan Koshkin (282276)
- Bohdan Stepanenko (283017)
- Nazarii Yasinskyi (280972)

---

## Wybrany temat: 3. Symulacje Fizyczne – Przepływ Ciepła 1D (1D Stencil)

### 1. Opis problemu

Symulacja rozchodzenia się temperatury w jednowymiarowym pręcie o długości $N$ w czasie. Nowa wartość elementu w kroku czasowym $t+1$ zależy od jego bezpośrednich sąsiadów:
$$u_i^{t+1} = 0.5 \cdot (u_{i-1}^t + u_{i+1}^t)$$

### 2. Oczekiwane kroki i zrównoleglenie

- **CPU:**
  - Implementacja bazowa wykorzystująca podwójną pętlę (po czasie oraz po elementach pręta).
  - Zastosowanie techniki podwójnego buforowania (ang. _double buffering_).
- **GPU:**
  - Przypisanie poszczególnych elementów pręta do niezależnych wątków.
  - Wykorzystanie pamięci współdzielonej (ang. _Shared Memory_) do szybkiego lokalnego przechowywania danych sąsiadów.
- **Profilowanie i analiza:**
  - Badanie oraz porównanie przepustowości pasma pamięci przed i po zastosowaniu optymalizacji z użyciem pamięci współdzielonej.
