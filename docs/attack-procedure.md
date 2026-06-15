# Procedura ataku Evil Twin

**UWAGA:** Procedura przeznaczona WYŁĄCZNIE do celów edukacyjnych w izolowanym środowisku laboratoryjnym. Atak na sieci bez zgody właściciela jest nielegalny.

---

## Schemat czasowy

```
Czas: ~45–60 minut (przygotowany zestaw)

┌───────────────────────────────────────────────────────────────────┐
│  Faza 1 (10 min)   │  Faza 2 (15 min)   │  Faza 3 (20 min)      │
│                     │                     │                         │
│  Setup środowiska   │  Atak właściwy      │  Analiza i weryfikacja  │
│  ┌───────────────┐  │  ┌───────────────┐  │  ┌───────────────────┐  │
│  │ airodump start │  │ │ deauth +       │  │ │ uruchom skrypt    │  │
│  │ airgeddon      │  │ │ captive portal │  │ │ Wireshark review  │  │
│  │ konfiguracja   │  │ │ ofiara traci   │  │ │ zapisz wyniki     │  │
│  │                 │  │ │ połączenie     │  │ │                    │  │
│  └───────────────┘  │  │ ofiara łączy   │  │ └───────────────────┘  │
│                      │  │ się z Evil     │  │                         │
│                      │  │ wpisuje hasło  │  │                         │
│                      │  └───────────────┘  │                         │
│                      │                     │                         │
└───────────────────────────────────────────────────────────────────┘
```

---

## Faza 1 — Setup środowiska

### Setup fizyczny

| Urządzenie | Rola | Czynność |
|---|---|---|
| Telefon A | Hotspot (oryginalny AP) | Włącz hotspot: SSID `AGH_Test`, WPA2, kanał 6 |
| Telefon B | Ofiara | Podłącz do hotspotu telefonu A |
| Kali VM | Atakujący | Uruchom VM, podłącz obie karty przez passthrough |

### 1A — Przygotowanie karty monitor

```bash
# Zabij procesy zakłócające monitor mode
sudo airmon-ng check kill

# Przełącz wlan0 w tryb monitor
sudo airmon-ng start wlan0

# Sprawdź czy interfejs się pojawił
iw dev
```

Oczekiwany wynik: pojawi się `wlan0mon`.

### 1B — Rozpocznij przechwytywanie ruchu

```bash
# Rozpocznij zbieranie ramek Beacon na kanale 6
# (dostosuj kanał do aktualnie używanego przez telefon A)
sudo airodump-ng wlan0mon -c 6 -w /tmp/evil_twin_demo --output-format pcap
```

**Zostaw to uruchomione w tle przez cały czas trwania ataku.** Plik `/tmp/evil_twin_demo-01.pcap` będzie zawierał wszystkie ramki z kanału, w tym beacony z oryginalnego AP i z Evil Twin.

### 1C — Przygotuj airgeddon

```bash
# Otwórz nowy terminal
sudo airgeddon
```

W interfejsie airgeddon:
1. Wybierz interfejs **wlan1** (karta #2 — ta, która będzie Evil Twin AP)
2. Potwierdź tryb monitor (jeśli pyta)
3. Wybierz opcję: **Evil Twin AP attacks**

---

## Faza 2 — Atak właściwy

### 2A — Skanowanie i wybór SSID

W airgeddon:
1. Wybierz **Beacon's Evil Twin attack** (lub podobną nazwę)
2. Wykonaj skan sieci — poczekaj aż znajdzie `AGH_Test`
3. Wybierz `AGH_Test` z listy

### 2B — Konfiguracja ataku

1. Wybierz metodę deauth: **mDK3** (zalecane) lub **aireplay-ng**
2. Wybierz: **Evil Twin AP with captive portal**
3. Wybierz szablon captive portala (np. "Generic" lub "Login")
4. Potwierdź konfigurację

### 2C — Wykonanie ataku

Airgeddon automatycznie:

1. **Postawi fałszywy AP** (hostapd + dnsmasq) z SSID `AGH_Test`
2. **Rozpocznie deauthentication** klientów oryginalnego AP
3. **Uruchomi captive portal** na adresie IP fałszywego AP

Obserwuj ekran telefonu B (ofiara):

1. Telefon B straci połączenie z oryginalnym AP (deauth)
2. Telefon B automatycznie połączy się z Evil Twin (silniejszy sygnał)
3. Pojawi się strona captive portala (logowanie)
4. Wpisz dowolne "hasło" i kliknij "Zaloguj"

**Sukces ataku:** Hasło pojawi się w terminalu airgeddon.

### 2D — Zatrzymanie przechwytywania

W terminalu z airodump-ng naciśnij `Ctrl+C`. Plik `.pcap` został zapisany do `/tmp/evil_twin_demo-01.pcap`.

---

## Faza 3 — Podstawowa analiza

### 3A — Uruchom analyze_pcap.py

```bash
python3 ~/analyze_pcap.py /tmp/evil_twin_demo-01.pcap AGH_Test
```

Oczekiwany wynik:

```
[*] Wczytuję plik: /tmp/evil_twin_demo-01.pcap
[*] Załadowano X pakietów.

======================================================================
  WYKRYTE PUNKTY DOSTĘPOWE — SSID: AGH_Test
======================================================================

  [!] UWAGA: 2 urządzeń nadaje z SSID='AGH_Test'
      To jest wskaźnik ataku Evil Twin!

  AP #1
  BSSID           : AA:BB:CC:DD:EE:01
  SSID            : AGH_Test
  Ramki Beacon    : 150
  Avg RSSI        : -42.3 dBm
  Supported Rates : 6, 9, 12, 18, 24, 36, 48, 54 Mbps
  ...

  AP #2
  BSSID           : AA:BB:CC:DD:EE:02
  SSID            : AGH_Test
  Ramki Beacon    : 200
  Avg RSSI        : -29.1 dBm
  ...

[*] Wykres zapisany: /tmp/evil_twin_analysis.png
```

### 3B — Otwórz wykres

Sprawdź plik `evil_twin_analysis.png` — dwa podwykresy:

1. **Sequence Numbers** — rozdzielające się linie = dwa różne urządzenia
2. **RSSI w czasie** — różne poziomy sygnału dla obu AP

### 3C — Weryfikacja w Wireshark (opcjonalna)

Szczegółowy workflow analizy w Wireshark: [`analysis-workflow.md`](analysis-workflow.md)

---

## Podsumowanie ataku

| Etap | Status | Uwagi |
|---|---|---|
| Setup środowiska | ✅ | karty, telefony, Kali VM |
| Przechwytywanie | ✅ | plik .pcap |
| Deauth + Evil Twin | ✅ | ofiara straciła i odzyskała połączenie |
| Captive portal | ✅ | hasło przechwycone |
| Analiza skryptem | ✅ | raport + wykres |
| Weryfikacja Wireshark | Opcjonalnie | szczegółowe porównanie IE |
