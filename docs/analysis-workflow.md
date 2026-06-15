# Workflow analizy pcap (v2.0)

Ten dokument opisuje szczegółową procedurę analizy pliku `.pcap` w celu wykrycia ataku Evil Twin, z wykorzystaniem Wireshark i narzędzi projektu `BBSK-Evil-Twin`.

**Dostępne narzędzia:**

| Narzędzie | Opis | Output |
|---|---|---|
| `analyze_pcap.py` (v2.0) | Automatyczna analiza wszystkich AP | Raport tekstowy + JSON + CSV + wykres PNG |
| `beacon_diff.py` (v1.0) | Szczegółowe porównanie IE między dwoma AP | Raport tekstowy + JSON + Markdown |
| `generate_report.py` (v1.0) | Generator raportu końcowego | Raport Markdown → DOCX/PDF |

---

## 1. Analiza automatyczna (analyze_pcap.py v2.0)

### Uruchomienie

```bash
# Tryb podstawowy (legacy compatible)
python3 skrypty/analyze_pcap.py <ścieżka/do/pliku.pcap> [SSID]

# Tryb rozszerzony — JSON + CSV + wykres
python3 skrypty/analyze_pcap.py plik.pcap SSID --json --csv -o ./wyniki/

# Tryb cichy — bez wykresu
python3 skrypty/analyze_pcap.py plik.pcap SSID --no-plot --quiet
```

### Co robi skrypt

| Krok | Opis |
|---|---|
| 1. Wczytanie | `rdpcap()` — załadowanie pliku .pcap |
| 2. Filtrowanie | Tylko ramki Beacon (Dot11 subtype 8) |
| 3. Ekstrakcja IE | SSID, Supported Rates, Vendor Specific, HT Capabilities, Country, ERP, Power Constraint, Extended Capabilities |
| 4. Odczyt | Sequence Number (SC >> 4), RSSI z RadioTap, kanał (DSSS), interwał beaconów |
| 5. Raport | Szczegółowa tabela AP z metrykami + podsumowanie statystyczne |
| 6. Eksport | JSON (dla innych narzędzi), CSV (dla arkuszy) |
| 7. Wykres | Seq num + RSSI w czasie, zapis do .png (opcjonalnie) |

### Nowości w v2.0

- `--json` — eksport do JSON z metadanymi (znacznik czasu UTC, liczba AP)
- `--csv` — eksport do CSV (kompatybilny z Excel/Google Sheets)
- `-o / --output-dir` — jawny katalog wyjściowy
- `--no-plot` — wyłączenie wykresów (gdy brak GUI)
- `--quiet` — tryb cichy (tylko komunikaty o błędach)
- Rozszerzona baza OUI (50+ producentów)
- Parsowanie: HT Capabilities, HT Operation, Country, ERP, Power Constraint, Extended Capabilities
- Śledzenie interwałów między beaconami
- Podsumowanie statystyczne (zakres RSSI, liczba unikalnych SSID)

### Interpretacja wyników

**Sygnały ostrzegawcze:**

| Wskaźnik | Interpretacja |
|---|---|
| `[!] UWAGA: N urządzeń nadaje z SSID='...'` | Potencjalny Evil Twin — N ≥ 2 |
| Różne Supported Rates dla tego samego SSID | Różne urządzenia (różni producenci) |
| Różne Vendor Specific OUI | Różni producenci sprzętu |
| Rozwidlenie na wykresie Sequence Numbers | Dwa niezależne liczniki sprzętowe |

---

## 2. Analiza ręczna (Wireshark)

### 2.1 Otwórz plik w Wireshark

```bash
wireshark /tmp/evil_twin_demo-01.pcap
```

### 2.2 Filtr dla ramek Beacon

```
wlan.fc.type_subtype == 8 && wlan.ssid == "AGH_Test"
```

### 2.3 Metoda 1: Fingerprinting IE

1. Kliknij na dowolną ramkę Beacon z oryginalnego AP (telefon)
2. Rozwiń **IEEE 802.11 Beacon frame → Tagged parameters**
3. Zanotuj wartości:

| Pole | AP #1 (telefon) | AP #2 (Evil Twin) | Wniosek |
|---|---|---|---|
| Supported Rates (tag 1) | 6, 12, 24, 36 | 6, 12, 24, 36, 48, 54 | Różne → różne urządzenia |
| Extended Supported Rates (tag 50) | 48, 54 | — | Różne → różne urządzenia |
| Vendor Specific (tag 221) | OUI: 00:0C:03 (Apple) | OUI: 00:03:7F (Atheros) | Inny producent = dowód |
| HT Capabilities (tag 45) | Obecne/brak | Brak/obecne | Różna konfiguracja |

4. Powtórz dla ramki z Evil Twin (drugi BSSID)
5. Zrób **screenshot** z zakładką Tagged parameters dla obu ramek

### 2.4 Metoda 2: Analiza RSSI

1. Wróć do listy pakietów
2. Kliknij na ramkę → rozwiń **Radiotap Header → dBm Antenna Signal**
3. Porównaj wartości RSSI dla ramek z obu BSSID:

| BSSID | RSSI zakres | Średnia | Uwagi |
|---|---|---|---|
| Telefon A (oryginalny) | -35 do -50 dBm | ~-42 dBm | Telefon w pewnej odległości |
| Evil Twin | -25 do -30 dBm | ~-28 dBm | Karta USB blisko |

**Jeśli różnica średnich RSSI > 15 dBm** — nienaturalne, wskazuje na Evil Twin (karta atakującego celowo blisko ofiary).

### 2.5 Metoda 3: Sequence Number analysis

1. Dodaj kolumnę Sequence Number w Wireshark:
   - **Edit → Preferences → Appearance → Columns**
   - Dodaj: `wlan.seq` z tytułem "Seq"
2. Posortuj ramki dla każdego BSSID
3. Zaobserwuj:

- Ramki z BSSID telefonu A: Sequence Numbers rosną od wartości X
- Ramki z BSSID Evil Twin: Sequence Numbers rosną od wartości Y (innej)

**Dwa niezależne strumienie Sequence Numbers** = dwa fizyczne urządzenia nadające z tym samym SSID = Evil Twin.

---

## 3. Synteza wyników

### Matryca decyzyjna

| Metoda | Wynik | Wnioskowanie |
|---|---|---|
| IE fingerprinting | Różne Supported Rates / Vendor Specific | ★★★ Prawie pewny Evil Twin |
| IE fingerprinting | Identyczne IE | Brak przesłanek (mogą być takie same urządzenia) |
| RSSI | Δ średniej > 15 dBm | ★★ Prawdopodobny Evil Twin (podatne na manipulację) |
| RSSI | Δ średniej < 5 dBm | Brak przesłanek |
| Seq numbers | Rozwidlenie na wykresie | ★★★ Pewny Evil Twin (twardy dowód) |
| Seq numbers | Pojedynczy strumień | Brak przesłanek |

### Ostateczna ocena

| Warunek | Werdykt |
|---|---|
| 3/3 metody wskazują | **Evil Twin potwierdzony** |
| 2/3 metody wskazują | **Wysoce prawdopodobny Evil Twin** |
| 1/3 metoda wskazuje | **Podejrzenie — wymaga potwierdzenia** |
| 0/3 metod wskazuje | **Brak dowodów na atak** |

---

## 4. Szczegółowe porównanie IE (beacon_diff.py v1.0)

### Uruchomienie

```bash
# Automatyczne — porównaj dwa pierwsze AP z tym samym SSID
python3 skrypty/beacon_diff.py plik.pcap AGH_Test

# Ręczne — porównaj konkretne BSSIDy
python3 skrypty/beacon_diff.py plik.pcap --bssid1 AA:BB:CC:DD:EE:01 --bssid2 AA:BB:CC:DD:EE:02

# Z eksportem
python3 skrypty/beacon_diff.py plik.pcap AGH_Test --json --markdown -o ./wyniki/
```

### Co robi skrypt

| Krok | Opis |
|---|---|
| 1. Ekstrakcja | Wszystkie IE z ramek Beacon dla dwóch BSSID |
| 2. Parsowanie | SSID, Supported Rates, Vendor Specific (z OUI), HT Capabilities, ERP, Country, RSN |
| 3. Porównanie | Identyfikacja IE które się różnią między AP |
| 4. Metryki | Różnica RSSI, nakładanie Sequence Numbers, liczba ramek |
| 5. Werdykt | Automatyczna klasyfikacja: EVIL_TWIN_CONFIRMED / SUSPICIOUS / NO_EVIDENCE |
| 6. Eksport | JSON + Markdown (do raportu końcowego) |

### Interpretacja wyników

| Status | Znaczenie |
|---|---|
| `DIFFERENT` | Ten IE różni się między AP — potencjalny dowód Evil Twin |
| `IDENTICAL` | IE identyczny w obu AP — brak przesłanek |
| `Różnica RSSI > 10 dBm` | Anomalia sygnału — typowe dla Evil Twin |
| `Seq overlap = 0` | Dwa całkowicie niezależne strumienie seq |

---

## 5. Generowanie raportu końcowego (generate_report.py v1.0)

### Uruchomienie

```bash
python3 skrypty/generate_report.py \
    --analyze-json wyniki/evil_twin_analysis.json \
    --diff-json wyniki/beacon_diff.json \
    --autorzy "Piotr Straszak, Jan Kowalski" \
    --przedmiot "Bezpieczeństwo Sieci Bezprzewodowych" \
    --ssid "AGH_Test" \
    -o raport_koncowy.md
```

### Konwersja do DOCX

```bash
# Wymaga pandoc: sudo apt install pandoc
pandoc raport_koncowy.md -o raport_koncowy.docx --from markdown --to docx
```

---

## 6. Generowanie dowodów

Dla każdej metody wygeneruj materiał dowodowy do raportu końcowego:

| Metoda | Materiał dowodowy | Narzędzie |
|---|---|---|
| IE fingerprinting | Screenshot Tagged parameters × 2 AP + raport JSON/MD | Wireshark + `beacon_diff.py` |
| RSSI | Screenshot Radiotap header × kilka ramek + JSON | Wireshark + `analyze_pcap.py` |
| Seq numbers | Wykres seq w czasie + JSON z zakresami | `analyze_pcap.py` |
| Captive portal | Screenshot strony logowania | Telefon B / airgeddon |
| Atak | Screenshot airgeddon z przechwyconym hasłem | Terminal |
| Raport końcowy | Plik DOCX z wszystkimi sekcjami | `generate_report.py` + pandoc |

---

## 7. Pełny workflow (wszystkie narzędzia)

```bash
# 1. Analiza automatyczna
python3 analyze_pcap.py /tmp/demo.pcap AGH_Test --json --csv -o ./wyniki/

# 2. Porównanie IE
python3 beacon_diff.py /tmp/demo.pcap AGH_Test --json --markdown -o ./wyniki/

# 3. Raport końcowy
python3 generate_report.py \
    --analyze-json wyniki/evil_twin_analysis.json \
    --diff-json wyniki/beacon_diff.json \
    --autorzy "Imię Nazwisko" \
    -o raport_koncowy.md

# 4. Konwersja
pandoc raport_koncowy.md -o raport_koncowy.docx
```

Szczegółowa instrukcja krok-po-kroku: [`PLAN_PRAKTYCZNY.md`](../PLAN_PRAKTYCZNY.md)
