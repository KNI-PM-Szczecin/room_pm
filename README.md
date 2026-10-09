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


## Wdrożenie na Macu mini przez Jenkins

`Jenkinsfile` pobiera `main`, buduje obraz na Macu mini, sprawdza menu godzin, konfigurację i odczyt Supabase, a następnie uruchamia kontener `room_pm_bot`. Sukces wymaga komunikatu gotowości Discord i braku restartów kontenera. Pipeline odpytuje Git co 2 minuty. Obrazy mają tag `<commit>-<numer buildu>`.

- Konfiguracja: `/Users/wiit1/Containers/room_pm/config.json` (uprawnienia `600`, montowana tylko do odczytu).
- SQLite: `/Users/wiit1/Containers/room_pm/data/roompm.db` — zachowana pomiędzy wdrożeniami.
- Logi: `docker logs --tail 80 room_pm_bot`. Bot nie wystawia portów.
- Job: `http://mac-mini-wiit1.tailab0a78.ts.net:8080/job/room_pm/`.

Skopiuj `config.example.json` do `config.json` i uzupełnij `bot.token`, `bot.id`, `supabase.url` i `supabase.key`. Konfiguracja robocza jest wykluczona z Git i obrazu Dockera. Token musi należeć do RoomPM. W Discord Developer Portal bot wymaga włączonych intentów **Server Members** i **Message Content** oraz dodania go do docelowego serwera.

Pipeline używa jawnego socketu Docker Desktop i osobnego `DOCKER_CONFIG` w workspace. Publiczne obrazy pobiera bez credential helpera macOS Keychain. Nie zmienia konfiguracji Dockera innych usług.

Wdrożenie 2026-10-09: build #3 zakończył się SUCCESS; RoomPM jest połączony z Discordem, cztery komendy są zarejestrowane, SQLite zawiera dwa serwery, kontener ma zero restartów. Poprawiono brak `custom_id` menu godzin, który powodował błąd Discord 400/50035 i pozostawiał komendę na „thinking”. Test obsługi komendy z symulowanym Discordem i rzeczywistą Supabase potwierdził wyświetlenie menu i wynik wyszukiwania.

### Otwarte pytania

Job na Macu mini używa zapisanej kopii pipeline'u jako **Pipeline script**. Aby pobierał również Jenkinsfile z GitHub, przełączyć go na **Pipeline script from SCM**, repo `https://github.com/KNI-PM-Szczecin/room_pm.git`, gałąź `*/main`, Script Path `Jenkinsfile`. Obecna kopia pipeline'u stosuje tymczasowy patch menu godzin, pomijany, gdy poprawka jest już w kodzie; wersja Jenkinsfile w repo nie potrzebuje tego etapu.
