# BBSK-Evil-Twin — Detekcja ataków Evil Twin przez fingerprinting AP

Projekt badawczy realizowany w ramach przedmiotu **Bezpieczeństwo Sieci Bezprzewodowych (BBSK)**
na **Akademii Górniczo-Hutniczej (AGH), Wydział Informatyki, Elektroniki i Telekomunikacji (WIEiT)**.

Celem projektu jest opracowanie i demonstracja metod detekcji ataków typu
**Evil Twin / Rogue Access Point** poprzez analizę ramek Beacon 802.11 —
fingerprinting urządzeń na podstawie Information Elements (IE), RSSI oraz
numerów sekwencyjnych (Sequence Numbers).

---

## Spis treści

- [Architektura](#architektura)
- [Wymagania](#wymagania)
  - [Sprzętowe](#sprzętowe)
  - [Programowe](#programowe)
- [Struktura repozytorium](#struktura-repozytorium)
- [Instalacja](#instalacja)
- [Użycie](#użycie)
  - [Podstawowe](#podstawowe)
  - [Pełny workflow](#pełny-workflow)
  - [Wyjście skryptu](#wyjście-skryptu)
- [Metodyka badawcza](#metodyka-badawcza)
  - [Metoda 1: Fingerprinting Beacon frames](#metoda-1-fingerprinting-beacon-frames)
  - [Metoda 2: Analiza RSSI](#metoda-2-analiza-rssi)
  - [Metoda 3: Sequence Number analysis](#metoda-3-sequence-number-analysis)
- [Ostrzeżenie prawne](#ostrzeżenie-prawne)
- [Autorzy](#autorzy)
- [Licencja](#licencja)

---

## Architektura

```
┌──────────────────────┐     ┌──────────────────────────────────┐
│  ŚRODOWISKO OFIARY    │     │  ŚRODOWISKO ATAKUJĄCE (Kali VM)  │
│                       │     │                                  │
│  Telefon A (hotspot)  │     │  Karta 1 (TP-Link WDN3200 #1)    │
│  SSID: AGH_Test       │     │  └─ tryb monitor (airodump-ng)   │
│  Kanał: 6, 2.4 GHz    │     │     → zbiera ramki Beacon        │
│  WPA2-Personal        │     │     → plik .pcap                 │
│                       │     │                                  │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │     │  Karta 2 (TP-Link WDN3200 #2)    │
│  Telefon B (ofiara)   │     │  └─ tryb AP (airgeddon)          │
│  Podłączony do A      │     │     → emituje Evil Twin SSID     │
│  → otrzymuje deauth   │     │     → captive portal             │
│  → łączy się z        │     │                                  │
│     Evil Twin         │     └──────────────────────────────────┘
│                       │                      │
└───────────────────────┘                      │
                                               ▼
                               ┌──────────────────────────┐
                               │  ANALIZA                  │
                               │                           │
                               │  Wireshark                │
                               │  → ręczne porównanie IE   │
                               │  → RSSI z Radiotap        │
                               │  → Sequence Numbers       │
                               │                           │
                               │  analyze_pcap.py          │
                               │  → raport tekstowy        │
                               │  → wykres seq + rssi      │
                               └──────────────────────────┘
```

Szczegółowy opis: [`docs/architecture.md`](docs/architecture.md)

---

## Wymagania

### Sprzętowe

| Komponent | Specyfikacja | Uwagi |
|---|---|---|
| Karta Wi-Fi #1 | TP-Link TL-WDN3200 (Ralink RT5572) | Tryb monitor + injection ✅ |
| Karta Wi-Fi #2 | TP-Link TL-WDN3200 (Ralink RT5572) | Tryb AP (airgeddon) ✅ |
| Komputer host | 8 GB RAM, obsługa USB passthrough | Rekomendacja |
| Telefon A | Hotspot Wi-Fi, 2.4 GHz, WPA2 | Źródło oryginalnego AP |
| Telefon B | Dowolny klient Wi-Fi | "Ofiara" w scenariuszu |

### Programowe

| Narzędzie | Wersja minimalna | Źródło |
|---|---|---|
| Kali Linux | 2024.x | [kali.org](https://www.kali.org) |
| Python | 3.8+ | `apt install python3` |
| Scapy | 2.5.0 | `pip install scapy` |
| Matplotlib | 3.7.0 | `pip install matplotlib` |
| Airgeddon | latest | `apt install airgeddon` |
| Wireshark | latest | `apt install wireshark` |
| Aircrack-ng | latest | `apt install aircrack-ng` |

---

## Struktura repozytorium

```
BBSK-Evil-Twin/
│
├── README.md                        # Niniejszy plik — punkt wejścia
├── LICENSE                          # Licencja MIT
├── .gitignore                       # Reguły ignorowania plików
├── requirements.txt                 # Zależności Pythona
│
├── docs/                            # Dokumentacja formalna
│   ├── architecture.md              # Architektura systemu
│   ├── threat-model.md              # Model zagrożeń
│   ├── security-considerations.md   # Kwestie bezpieczeństwa i prawne
│   ├── setup.md                     # Konfiguracja środowiska
│   ├── attack-procedure.md          # Procedura ataku Evil Twin
│   ├── analysis-workflow.md         # Workflow analizy pcap
│   ├── use-cases.md                 # Przypadki użycia
│   ├── development.md               # Workflow deweloperski
│   └── known-limitations.md         # Znane ograniczenia
│
├── dokumentacja/                    # Opracowania w formatach biurowych
│   ├── opracowanie_wstepne.docx     # Opracowanie wstępne (DOCX)
│   └── PLAN_PRAKTYCZNY.md           # Instrukcja wykonania części praktycznej
│
├── notatki/                         # Notatki robocze (nieformalne)
│   ├── odp.md                       # Konsultacje — plan działania
│   └── odp2.md                      # Konsultacje — szczegółowy przegląd
│
├── skrypty/                         # Kod źródłowy
│   ├── analyze_pcap.py              # Główny skrypt analityczny (v2.0)
│   ├── beacon_diff.py               # Szczegółowe porównanie IE między AP (v1.0)
│   └── generate_report.py           # Generator raportu końcowego (v1.0)
│
├── tests/                           # Testy jednostkowe
│   └── test_analyze_pcap.py         # Testy skryptu analitycznego
│
├── przechwycony_ruch/               # Pliki .pcap (.gitignored)
│   └── .gitkeep                     # Placeholder zachowujący katalog
│
└── wyniki/                          # Wyniki analizy (.gitignored)
    └── .gitkeep                     # Placeholder zachowujący katalog
```

---

## Instalacja

```bash
# 1. Sklonuj repozytorium
git clone <repo-url>
cd BBSK-Evil-Twin

# 2. (Opcjonalnie) Środowisko wirtualne
python3 -m venv venv
source venv/bin/activate

# 3. Zainstaluj zależności Pythona
pip install -r requirements.txt

# 4. Na Kali Linux — narzędzia systemowe
sudo apt update
sudo apt install airgeddon wireshark aircrack-ng -y
```

Kompletna konfiguracja środowiska: [`docs/setup.md`](docs/setup.md)

---

## Użycie

### Narzędzia

| Narzędzie | Opis |
|---|---|
| `analyze_pcap.py` (v2.0) | Automatyczna analiza AP — raport + JSON + CSV + wykres |
| `beacon_diff.py` (v1.0) | Szczegółowe porównanie IE między dwoma AP |
| `generate_report.py` (v1.0) | Generator raportu końcowego (Markdown → DOCX) |

### Podstawowe

```bash
# Analiza wszystkich AP w pliku pcap
python3 skrypty/analyze_pcap.py /tmp/demo-01.pcap

# Analiza z filtrowaniem po SSID + eksport JSON/CSV
python3 skrypty/analyze_pcap.py /tmp/demo-01.pcap AGH_Test --json --csv -o ./wyniki/

# Porównanie IE między dwoma AP
python3 skrypty/beacon_diff.py /tmp/demo-01.pcap AGH_Test --json --markdown -o ./wyniki/

# Generowanie raportu końcowego
python3 skrypty/generate_report.py \
    --analyze-json wyniki/evil_twin_analysis.json \
    --diff-json wyniki/beacon_diff.json \
    -o raport_koncowy.md
```

### Pełny workflow

1. **Przechwyć ruch** — airodump-ng w trybie monitor
2. **Przeprowadź atak** — airgeddon z captive portalem
3. **Analizuj** — `analyze_pcap.py` + `beacon_diff.py`
4. **Weryfikuj w Wireshark** — ręczna analiza IE, RSSI, seq
5. **Generuj raport** — `generate_report.py` → DOCX

Szczegółowa procedura: [`docs/attack-procedure.md`](docs/attack-procedure.md)
Instrukcja krok-po-kroku: [`PLAN_PRAKTYCZNY.md`](PLAN_PRAKTYCZNY.md)

### Wyjście skryptów

| Narzędzie | Wyniki |
|---|---|
| `analyze_pcap.py` | Raport tekstowy + ostrzeżenie Evil Twin + JSON + CSV + wykres PNG |
| `beacon_diff.py` | Raport porównania IE + JSON + Markdown z werdyktem |
| `generate_report.py` | Raport końcowy `.md` (gotowy do konwersji na DOCX przez pandoc) |

---

## Metodyka badawcza

Projekt implementuje trzy uzupełniające się metody detekcji ataku Evil Twin:

### Metoda 1: Fingerprinting Beacon frames

**Co analizujemy:** Ramki Beacon (type 0, subtype 8) — konkretnie pola Information Elements.

**Kluczowe wskaźniki:**
- **Supported Rates (ID=1, 50)** — różne zestawy obsługiwanych prędkości wskazują na różne urządzenia
- **Vendor Specific (ID=221)** — różne OUI (np. Apple vs Ralink) jednoznacznie identyfikują różnych producentów
- **Capabilities flags** — różne konfiguracje (np. QoS, Short Preamble)

**Implementacja:** `analyze_pcap.py` — ekstrakcja z ramek Beacon, porównanie między BSSID.

### Metoda 2: Analiza RSSI

**Co analizujemy:** `dBm_AntSignal` z nagłówka Radiotap.

**Kluczowy wskaźnik:** Karta USB Evil Twin trzymana blisko ofiary generuje nienaturalnie wysoki RSSI w porównaniu z oryginalnym AP (np. telefon w drugim kącie pokoju). Skok o >15 dBm w krótkim czasie to red flag.

**Implementacja:** `analyze_pcap.py` — wykres RSSI w czasie, średnia dla każdego BSSID.

### Metoda 3: Sequence Number analysis

**Co analizujemy:** Pole Sequence Number (SC >> 4) w nagłówku 802.11.

**Kluczowy wskaźnik:** Każde urządzenie ma niezależny licznik sekwencyjny. Dwa urządzenia nadające z tym samym SSID generują dwa rozbieżne strumienie seq. number. Rozwidlenie na wykresie = dowód na dwa różne urządzenia.

**Implementacja:** `analyze_pcap.py` — scatter plot seq. number w czasie.

---

## Ostrzeżenie prawne

> **Ten projekt służy wyłącznie celom edukacyjnym i badawczym.**

- Przeprowadzanie ataków Evil Twin na sieci bez wyraźnej zgody właściciela jest nielegalne w świetle polskiego prawa (art. 267 §1 Kodeksu karnego: "Kto bez uprawnienia uzyskuje dostęp do systemu komputerowego, podlega grzywnie, karze ograniczenia wolności albo pozbawienia wolności do lat 2").
- Wszystkie testy należy przeprowadzać w izolowanym środowisku laboratoryjnym, z wykorzystaniem własnych urządzeń.
- Autorzy nie ponoszą odpowiedzialności za nieuprawnione wykorzystanie narzędzi i metod opisanych w tym repozytorium.

Szczegółowe informacje: [`docs/security-considerations.md`](docs/security-considerations.md)

---

## Autorzy

Piotr Straszak,
Hubert Czernicki

**Akademia Górniczo-Hutnicza im. Stanisława Staszica w Krakowie**
Wydział Informatyki, Elektroniki i Telekomunikacji
Kierunek: Cyberbezpieczeństwo
Rok akademicki 2025/2026

---

## Licencja

MIT — zobacz plik [LICENSE](LICENSE) po szczegóły.

Copyright (c) 2026 Autorzy projektu.
