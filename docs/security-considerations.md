# Security Considerations

## Podstawa prawna w Polsce

Przeprowadzanie ataków Evil Twin na sieci bez wyraźnej zgody właściciela jest nielegalne.

### Art. 267 §1 Kodeksu karnego

> Kto bez uprawnienia uzyskuje dostęp do systemu komputerowego albo pozostaje w nim wbrew żądaniu osoby uprawnionej, podlega grzywnie, karze ograniczenia wolności albo pozbawienia wolności do lat 2.

### Art. 269a Kodeksu karnego

> Kto, niszcząc, uszkadzając, usuwając lub zmieniając dane komputerowe albo zakłócając pracę systemu komputerowego lub sieci telekomunikacyjnej, popełnia przestępstwo przeciwko bezpieczeństwu danych, podlega karze pozbawienia wolności od 3 miesięcy do lat 5.

### Ustawa o krajowym systemie cyberbezpieczeństwa

Testy penetracyjne na własnej infrastrukturze lub w ramach autoryzowanego laboratorium są dozwolone. Działania na sieciach osób trzecich wymagają pisemnej zgody.

---

## Odpowiedzialne ujawnianie (Responsible Disclosure)

Jeśli z wykorzystaniem metod opisanych w tym projekcie odkryjesz podatność w produkcyjnej sieci Wi-Fi:

1. **NIE wykorzystuj jej dalej** — natychmiast przerwij analizę
2. **Udokumentuj** — zapisz, co odkryłeś i w jakich okolicznościach
3. **Zgłoś** — skontaktuj się z właścicielem sieci (najlepiej przez security@domena)
4. **Usuń ślady** — nie przechowuj plików .pcap z produkcyjnych sieci
5. **Nie publikuj** szczegółów do czasu załatania podatności

---

## Bezpieczeństwo danych w projekcie

### Pliki .pcap

Pliki .pcap mogą zawierać:

- **MAC adresy urządzeń** — można je zanonimizować (np. narzędziem `tcprewrite`)
- **SSID sieci** — wrażliwe w kontekście lokalizacji
- **Elementy sieciowe** — mapowanie urządzeń

**Zasady postępowania:**
- Pliki .pcap są wykluczone z Git (.gitignore)
- Przechowuj tylko w katalogu `przechwycony_ruch/`
- Przetwarzaj lokalnie, nie wysyłaj na zewnętrzne serwery
- Po zakończeniu projektu usuń pliki produkcyjne

### Wyniki analizy

Wykresy i raporty generowane przez `analyze_pcap.py` zawierają MAC adresy w formie czytelnej. Przed publikacją w raporcie końcowym:

- Zastąp rzeczywiste MAC adresy placeholderami (np. `AA:BB:CC:DD:EE:01`)
- Nie zamieszczaj zdjęć z paskiem adresu telefonu, nr IMEI, lokalizacji GPS

---

## Bezpieczeństwo środowiska laboratoryjnego

| Obszar | Rekomendacja |
|---|---|
| **Sieć** | Izolowana sieć laboratoryjna — brak dostępu do Internetu |
| **Sprzęt** | Wyłącznie własne urządzenia (telefon A, B, Kali VM) |
| **Kanał** | Dedykowany kanał (np. 6) — nie zakłócać innych sieci |
| **Moc nadawania** | Minimalna wystarczająca do komunikacji (zmniejszyć zasięg) |
| **Po ataku** | Wyłączyć Evil Twin AP, przywrócić oryginalną konfigurację |

---

## Ochrona przed podobnymi atakami

### Dla użytkowników

| Praktyka | Opis |
|---|---|
| **Zwracaj uwagę na certyfikat** | Przy logowaniu do sieci korporacyjnych (EAP-TLS) |
| **Używaj VPN** | Chroni ruch nawet przy połączeniu z niebezpieczną siecią |
| **Sprawdzaj SSID** | Literówki, znaki specjalne — popularna technika |
| **Włącz PMF (802.11w)** | Jeśli urządzenie i AP obsługują |

### Dla administratorów

| Technika | Opis |
|---|---|
| **WIDS/WIPS** | Monitorowanie Beacon frames, alarm przy duplikatach SSID |
| **Analiza seq numbers** | Automatyczna detekcja rozbieżnych strumieni |
| **PMF obowiązkowo** | Wymuszaj Protected Management Frames |
| **EAP-TLS** | Zamiast haseł współdzielonych — certyfikaty |
| **Audyt radiowy** | Regularne skanowanie kanałów w poszukiwaniu rogue AP |
