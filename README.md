# Java learning — jak korzystać

To moje repozytorium do nauki Javy i JVM z LLM jako nauczycielem.
Przechowuje zasady prowadzenia lekcji, mój profil i zatwierdzone postępy.
Dzięki temu nowy czat może kontynuować naukę bez odtwarzania całej poprzedniej rozmowy.

**Ten README jest instrukcją dla mnie.** Punktem wejścia dla nauczyciela jest [AGENTS.md](AGENTS.md).
Repozytorium przechowuje ustalenia o nauce; fakty techniczne nauczyciel sprawdza w dokumentacji Javy i JVM.

## Szybki start kolejnej lekcji

1. Otwieram nowy czat w swoim projekcie nauki Javy w ChatGPT.
2. Upewniam się, że czat ma dostęp do repozytorium przez plugin GitHub.
3. Wysyłam:

   > Rozpocznij kolejną lekcję. Odczytaj zatwierdzony stan z repozytorium i zaproponuj temat oraz plan sesji.

4. Nauczyciel sprawdza zapisaną wersję, odczytuje potrzebne pliki i proponuje temat. Mogę go zaakceptować, zmienić albo odłożyć.
5. Na koniec przeglądam podsumowanie po polsku. Zatwierdzam dopiero treść, którą chcę zapisać.
6. Po zapisie oczekuję linku do lekcji, commita i wyników obu kontroli GitHub Actions.

Nie muszę kopiować historii poprzedniego czatu ani ręcznie przygotowywać JSON-a.
Rozmowa staje się trwałym stanem nauki dopiero po zatwierdzeniu, zapisie i pomyślnej walidacji.

## Jednorazowe przygotowanie projektu

- Używam osobnego projektu ChatGPT dla Javy. Inny przedmiot ma osobny projekt.
- Do pola instrukcji projektu wklejam **całą treść** [`.agents/project-instructions.md`](.agents/project-instructions.md), nie sam link.
- Zapewniam pluginowi GitHub dostęp do `kamil-kazmierczak/java-learning`.
- Nauczyciel musi móc odczytać pliki z konkretnego commita, sprawdzić wyniki CI i zapisać zatwierdzone zmiany.
- Samo podłączenie GitHuba nie gwarantuje wszystkich tych możliwości. Jeśli czegoś brakuje, nauczyciel powinien wskazać ograniczenie.

Pracujemy na gałęzi **`develop`**, bez pull requestów.
W GitHubie wybieram tę gałąź, gdy chcę zobaczyć aktualne pliki.
Po zmianie pliku instrukcji projektu ponownie wklejam jego treść do ustawień ChatGPT.
Zmiana pliku w repozytorium nie aktualizuje automatycznie wcześniej wklejonych instrukcji.

## Jak wygląda sesja

Aktualny budżet wynosi **30 minut**, zgodnie z [profilem](profile.json).
Obejmuje teorię, ćwiczenia, podsumowanie i zatwierdzenie zapisu.
Na początku nauczyciel proponuje jeden główny cel, zadania i szacowany czas etapów.

Najpierw odpowiadam na pytania lub przewiduję zachowanie kodu.
Gdy potrzebuję pomocy, nauczyciel zaczyna od pytania naprowadzającego, potem daje bardziej konkretną wskazówkę.
Mogę od razu poprosić o pełne wyjaśnienie.
Po wyjaśnieniu dostaję nowe zadanie, które pozwala sprawdzić samodzielne rozumienie.

Pracuję w IntelliJ IDEA z Eclipse Temurin Java 25.
Przy samodzielnym zadaniu mogę używać IDE, testów i dokumentacji; podpowiedzi LLM muszą być odnotowane.
Przewidzenie wyniku w rozmowie nie oznacza, że kod został uruchomiony.
Gdy uruchamiam kod u siebie, wklejam rzeczywisty wynik lub błąd.

Czas jest budżetem planowania, nie gwarantowanym automatycznym minutnikiem.
Jeżeli zadanie trwa dłużej, nauczyciel ogranicza pozostały zakres i proponuje przeniesienie niedokończonej pracy.
Powinien zapowiedzieć ostatnie zadanie i przejść do podsumowania bez czekania na dodatkową komendę.

## Przydatne wiadomości

To przykłady wiadomości, a nie specjalne komendy programu.

| Co chcę zrobić | Co mogę napisać |
| --- | --- |
| Zacząć sesję | „Rozpocznij kolejną lekcję na podstawie repozytorium.” |
| Zmienić temat | „Ten temat odkładamy. Zaproponuj inny i wyjaśnij dlaczego.” |
| Dostać małą podpowiedź | „Zadaj pytanie naprowadzające.” |
| Poznać wyjaśnienie | „Wyjaśnij mi to wprost, potem daj nowe zadanie.” |
| Ograniczyć zakres | „Mam jeszcze 10 minut. Dostosuj plan i zostaw czas na podsumowanie.” |
| Zakończyć wcześniej | „Kończymy.” |
| Poprawić zapis | „Nie zatwierdzam jeszcze. Popraw informację o…” |
| Zatwierdzić zapis | „Zatwierdzam podsumowanie i pokazane zmiany. Zapisz je.” |

## Co sprawdzam przed zatwierdzeniem

Nauczyciel pokazuje podsumowanie i proponowane zmiany stanu po polsku, mimo że zapisuje je w repozytorium po angielsku.
Sprawdzam, czy:

- opis zadań i moich odpowiedzi zgadza się z rozmową;
- zapis uwzględnia otrzymane podpowiedzi;
- wyniki uruchomienia kodu są oddzielone od przewidywań i analizy;
- błędy nauczyciela nie zostały zapisane jako moje luki;
- ocena postępu ma uzasadnienie w wykonanych zadaniach;
- niedokończona praca i kolejny proponowany krok są jasne.

Akceptacja tematu nie oznacza zgody na zapis lekcji.
Po zatwierdzeniu nauczyciel zapisuje lekcję i powiązane zmiany w jednym commicie.
Każda lekcja ma osobny plik oraz odnośnik w indeksie w `AGENTS.md`.

## Jak rozumieć postęp

| Stan | Znaczenie |
| --- | --- |
| `not_assessed` | Nie ma jeszcze wystarczających dowodów, by ocenić temat. |
| `learning` | Potrzebuję pomocy albo mam rozpoznaną lukę. |
| `applied_independently` | Rozwiązałem nowy wariant i wyjaśniłem mechanizm bez podpowiedzi LLM. |
| `retained` | Potwierdziłem tę umiejętność samodzielnie w późniejszym dniu. |

Jedna poprawna odpowiedź ani poczucie, że rozumiem wyjaśnienie, nie wystarczają do potwierdzenia trwałego opanowania tematu.
Terminy powtórek są propozycją opartą na wynikach, a nie jednym stałym harmonogramem.

## Gdzie czego szukać

Na co dzień wystarczą mi profil, bieżący stan i indeks lekcji.

| Plik lub katalog | Do czego służy |
| --- | --- |
| [profile.json](profile.json) | Cele, doświadczenie, narzędzia i budżet sesji. |
| [state/current.json](state/current.json) | Punkt wznowienia, ostatnia lekcja, niedokończone zadania i kolejka powtórek. |
| [curriculum.json](curriculum.json) | Mapa tematów, zależności i decyzje o ich wyborze. |
| `topics/` | Stan poszczególnych tematów, luki i odnośniki do dowodów. |
| `lessons/` | Zatwierdzone podsumowania lekcji. Indeks znajduje się w [AGENTS.md](AGENTS.md). |
| `exercises/` | Opisy ćwiczeń, kod i testy. Katalog powstaje, gdy zapisujemy takie materiały. |
| `language/` | Konfiguracja kontroli języka i słownik terminów technicznych. |

Elementy odpowiedzialne za działanie systemu:

| Plik lub katalog | Do czego służy |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Punkt wejścia agenta, kolejność odczytu i zasady zapisu. |
| [.agents/project-instructions.md](.agents/project-instructions.md) | Krótka instrukcja do wklejenia w ustawieniach projektu ChatGPT. |
| [.agents/teaching.md](.agents/teaching.md) | Sposób prowadzenia lekcji, pomocy, oceny i kończenia sesji. |
| [.agents/language.md](.agents/language.md) | Zasady pisania angielskich dokumentów i danych. |
| [.agents/config.json](.agents/config.json) | Repozytorium, gałąź, workflow i wymagane kontrole. |
| `.agents/schemas/` | Wymagany format i dozwolone pola JSON. |
| `.agents/examples/` | Fikcyjne przykłady formatu, nie moje wyniki. |
| `.agents/scripts/` | Walidatory i ich testy. |
| [.github/workflows/validate.yml](.github/workflows/validate.yml) | Kontrole uruchamiane przez GitHub Actions po zapisie. |
| [planning/system-plan.md](planning/system-plan.md) | Wymagania, decyzje projektowe i scenariusze akceptacyjne systemu. |

Markdown opisuje zasady i sposób korzystania. JSON przechowuje dane o określonej strukturze.
Nie muszę czytać schematów ani skryptów przed lekcją.

## Jak sprawdzić, czy zapis się udał

W [GitHub Actions](https://github.com/kamil-kazmierczak/java-learning/actions) sprawdzam uruchomienie dla commita podanego przez nauczyciela.
Obie kontrole muszą zakończyć się sukcesem:

- `validate-data` — sprawdza strukturę danych, powiązania, indeks lekcji i lokalne odnośniki Markdown;
- `validate-language` — sprawdza wybrane reguły angielskiego stylu w danych i dokumentach objętych kontrolą.

Wynik dla wcześniejszego commita nie potwierdza nowego zapisu.
Status oczekujący, pominięty lub zakończony błędem nie jest sukcesem.
Walidacja nie dowodzi poprawności merytorycznej lekcji ani pełnej zgodności z ASD-STE100.
Nie uruchamia też automatycznie przykładów Javy z rozmowy.

Ten polski README jest poza kontrolą angielskiego stylu. Jego lokalne odnośniki nadal podlegają walidacji.

## Gdy coś przerwie naukę

- **Zamknąłem czat przed zatwierdzeniem:** nową sesję zaczynam od ostatniego zatwierdzonego i poprawnie sprawdzonego zapisu.
  Niezapisana część rozmowy nie jest automatycznie odzyskiwana; mogę przekazać brakujący kontekst nauczycielowi.
- **Zapisano commit, ale CI nie przeszło:** proszę nauczyciela o wskazanie błędu i przygotowanie poprawki.
  Do wznowienia używany jest wcześniejszy zatwierdzony stan z poprawnymi kontrolami, o ile taki istnieje.
- **Brakuje dostępu do GitHuba lub wyników kontroli:** najpierw przywracam dostęp.
  Nauczyciel nie powinien deklarować udanego zapisu lub sprawdzenia bez potwierdzenia.
- **Chcę zmienić czas, środowisko lub sposób nauki:** opisuję zmianę nauczycielowi i proszę o pokazanie odpowiednich zmian w repozytorium.
  Profil przechowuje moje ustawienia; reguły prowadzenia lekcji znajdują się w `.agents/teaching.md`.
