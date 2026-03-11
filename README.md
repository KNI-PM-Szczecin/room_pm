# 🏫 RoomPM – Znajdź wolną salę na PM

**RoomPM** to wewnętrzne narzędzie stworzone przez **Koło Naukowe Informatyki (KNI)** Politechniki Morskiej w Szczecinie. Służy do błyskawicznego sprawdzania dostępności sal wykładowych i laboratoriów na podstawie bazy danych aplikacji [PlanPM](https://github.com/KNI-PM-Szczecin/plan_pm).

---

## 🚀 O projekcie

Narzędzie powstało, aby ułatwić studentom i członkom koła znajdowanie wolnych przestrzeni do pracy, nauki czy spotkań projektowych. RoomPM eliminuje potrzebę ręcznego sprawdzania planów każdego kierunku z osobna, agregując dane o zajętości sal w czasie rzeczywistym.

### Główne funkcje:
* **Wyszukiwanie dynamiczne:** Automatyczne filtrowanie zajętych sal w wybranych budynkach (np. Wały Chrobrego).
* **Precyzyjne okna czasowe:** Sprawdzanie dostępności dla konkretnych bloków godzinowych lub całych przedziałów czasowych.
* **Pełna baza uczelniana:** Obsługa sal ogólnych, laboratoriów specjalistycznych (LSO), symulatorów (CSO) oraz auli.
* **Czytelne raporty:** Wyniki prezentowane w formie przejrzystej listy, idealnej do szybkiego odczytu na urządzeniach mobilnych i komunikatorach.

---

## 📸 Przykład działania

Narzędzie generuje raporty w następującym formacie:

> **Budynek:** WChrobrego  
> **Data:** 11-03-2026  
> **Wybrane godziny:** 11: 17:20-18:05, 12: 18:15-19:00  
> **Dostępne sale:** 117, 339, 307/308/309 ARPA, CIRM, 320, 33, 405/408, 318, 36, 036, 048, 40, 177, symulator siłowni - CSO, 19, LSO (lab. siłowni okrętowych), 275, 13, 247, LNG, 112, 12, 208, 210, 218, 407, 22, 131, aula prof. Łaskiego, 172, 212, 55, 169, 267, 178, 265, 176, 226, 216, 317, 319, 110, 065, 043, 246, 220, 14, 301, 044, 411, 111

---

## 🛠 Architektura i Dane

RoomPM stanowi integralną część ekosystemu narzędzi KNI.

* **Źródło danych:** Bezpośrednia integracja z bazą danych/API [PlanPM](https://github.com/KNI-PM-Szczecin/plan_pm).
* **Interfejs:** Bot zintegrowany z Discord (framework nextcord).

---

## 👥 Autorzy

Projekt jest rozwijany i utrzymywany przez członków **Koła Naukowego Informatyki PM**. 

---
