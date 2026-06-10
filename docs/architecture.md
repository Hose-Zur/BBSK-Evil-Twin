# Architektura systemu

## Przegląd

System `BBSK-Evil-Twin` składa się z dwóch logicznych środowisk połączonych bezprzewodowo:

1. **Środowisko ofiary** — hotspot telefonu (oryginalny AP) + klient
2. **Środowisko atakującego** — Kali Linux VM z dwoma kartami Wi-Fi
3. **Środowisko analityczne** — warstwa oprogramowania do detekcji

---

## Diagram architektury

```
┌─────────────────────────────────────────────────────────────────┐
│                     ŚRODOWISKO FIZYCZNE                          │
│                                                                  │
│  ┌──────────────────────┐         ┌──────────────────────────┐   │
│  │  Telefon A (Hotspot)  │         │     Kali Linux VM         │   │
│  │  SSID: AGH_Test       │         │                            │   │
│  │  Kanał 6, 2.4 GHz     │         │  ┌────────────────────┐   │   │
│  │  WPA2-Personal        │         │  │ Karta 1: wlan0     │   │   │
│  │  MAC: XX:XX:XX:XX:1   │         │  │ (monitor)          │   │   │
│  └──────────┬────────────┘         │  │ airodump-ng        │   │   │
│             │                      │  │ → przechwytywanie  │   │   │
│             │ Ramki Beacon         │  │ → plik .pcap       │   │   │
│             ▼                      │  └────────┬───────────┘   │   │
│  ┌──────────────────────┐         │           │               │   │
│  │  Telefon B (ofiara)   │         │  ┌────────▼───────────┐   │   │
│  │  Połączony z A       │         │  │ Karta 2: wlan1     │   │   │
│  │  → deauth z Evil     │         │  │ (AP mode)          │   │   │
│  │  → łączy się z B     │         │  │ airgeddon          │   │   │
│  │  → captive portal    │         │  │ → Evil Twin AP     │   │   │
│  └──────────────────────┘         │  │ → captive portal   │   │   │
│                                    │  └────────────────────┘   │   │
│                                    └──────────────────────────┘   │
│                                             │                      │
│                                             ▼                      │
│                               ┌──────────────────────────┐        │
│                               │     ANALIZA               │        │
│                               │                            │        │
│                               │  ┌────────────────────┐   │        │
│                               │  │ analyze_pcap.py     │   │        │
│                               │  │ → Scapy: parsowanie │   │        │
│                               │  │ → raport tekstowy   │   │        │
│                               │  │ → wykres (.png)     │   │        │
│                               │  └────────────────────┘   │        │
│                               │                            │        │
│                               │  ┌────────────────────┐   │        │
│                               │  │ Wireshark           │   │        │
│                               │  │ → ręczna analiza   │   │        │
│                               │  │ → IE fingerprinting│   │        │
│                               │  │ → RSSI porównanie  │   │        │
│                               │  └────────────────────┘   │        │
│                               └──────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Komponenty sprzętowe

### Karta Wi-Fi #1 — tryb monitor (przechwytywanie)

| Parametr | Wartość |
|---|---|
| Model | TP-Link TL-WDN3200 |
| Chipset | Ralink RT5572 |
| Tryb | Monitor |
| Rola | Przechwytywanie ramek Beacon do pliku .pcap |
| Narzędzie | `airodump-ng` |

Karta działa w trybie monitor (RFMON) — przechwytuje wszystkie ramki 802.11 na zadanym kanale, bez konieczności łączenia się z siecią.

### Karta Wi-Fi #2 — tryb AP (atak)

| Parametr | Wartość |
|---|---|
| Model | TP-Link TL-WDN3200 |
| Chipset | Ralink RT5572 |
| Tryb | Master/AP |
| Rola | Emisja Evil Twin AP z captive portalem |
| Narzędzie | `airgeddon` |

Karta emuluje punkt dostępu o tym samym SSID co oryginalny AP, z własnym BSSID i modułem captive portal.

### Telefon A — oryginalny AP

| Parametr | Wartość |
|---|---|
| Rola | Legitymny punkt dostępowy |
| Pasmo | 2.4 GHz |
| Kanał | 6 |
| Zabezpieczenia | WPA2-Personal |
| SSID | `AGH_Test` (lub inny wybrany) |

---

## Komponenty programowe

### analyze_pcap.py

Główny skrypt analityczny projektu. Implementuje trzy metody detekcji:

| Moduł | Funkcja | Zależności |
|---|---|---|
| Parser ramek | Ekstrakcja ramek Beacon z pliku .pcap | `scapy` |
| Ekstrakcja IE | Parsowanie Supported Rates, Vendor Specific, SSID | `scapy` |
| Analiza RSSI | Odczyt dBm_AntSignal z RadioTap header | `scapy` |
| Śledzenie seq | Ekstrakcja Sequence Number (SC >> 4) | `scapy` |
| Raportowanie | Formatowany raport tekstowy w terminalu | — |
| Wizualizacja | Wykresy seq + RSSI w czasie | `matplotlib` |

### airodump-ng

Narzędzie z pakietu aircrack-ng do przechwytywania ramek 802.11 w trybie monitor.

### airgeddon

Narzędzie do przeprowadzania ataków Evil Twin — automatyzuje konfigurację fałszywego AP, deauthentication oraz captive portal.

### Wireshark

Analityczne narzędzie wspomagające — ręczna weryfikacja i szczegółowe porównanie IE między ramkami.

---

## Przepływ danych

```
┌──────────┐     Ramki Beacon (kanał 6)     ┌──────────────┐
│ Telefon A ├─────── 802.11 frames ──────────▶│ Karta 1      │
│ (AP)      │                                  │ (monitor)    │
└──────────┘                                  └──────┬───────┘
                                                      │ airodump-ng
                                                      ▼
┌──────────┐                                ┌──────────────┐
│ Karta 2   │◄──── sygnał deauth ───────────▶│  plik .pcap   │
│ (Evil AP) │                                │  (binarny)    │
└──────────┘                                      │
                                                  │ rdpcap()
                                                  ▼
                                          ┌────────────────┐
                                          │ analyze_pcap.py │
                                          └───┬────────────┘
                                              │
                                    ┌─────────┼─────────┐
                                    ▼         ▼         ▼
                              ┌────────┐ ┌────────┐ ┌────────┐
                              │Raport  │ │Wykres  │ │Ostrzeż.│
                              │tekstowy│ │.png    │ │EW      │
                              └────────┘ └────────┘ └────────┘
```

---

## Sieć logiczna

- **Oryginalny AP:** SSID `AGH_Test`, BSSID (MAC telefonu), kanał 6, 2.4 GHz
- **Evil Twin AP:** SSID `AGH_Test` (taki sam!), BSSID (MAC karty #2), kanał 6, 2.4 GHz
- **Pasmo:** 2.4 GHz (jedno pasmo — oba AP na tym samym kanale)
- **Klient:** Łączy się początkowo z oryginalnym AP, po deauth przełącza na Evil Twin

---

## Warstwy analizy

| Warstwa | Narzędzie | Co bada | Wynik |
|---|---|---|---|
| 1. Automatyczna | `analyze_pcap.py` | IE, RSSI, seq | Raport + wykres |
| 2. Ręczna | Wireshark | Szczegółowe: Tagged Parameters, Capabilities | Screenshoty + wnioski |
| 3. Porównawcza | Oba narzędzia | Różnice między AP z tym samym SSID | Dowód ataku |
