# Narzędzia — Rogue AP / Evil Twin: Atak, Detekcja, Fingerprinting

> **Projekt:** BBSK-Evil-Twin | **Data researchu:** 2026-06-14
>
> Poniżej znajduje się przegląd i analiza ciekawych narzędzi związanych z atakami
> typu Rogue AP / Evil Twin — zarówno ofensywnych (do przeprowadzania ataków),
> jak i defensywnych (do wykrywania). Dla każdego narzędzia podano instrukcję
> instalacji, podstawowe użycie oraz ocenę przydatności dla naszego projektu.

---

## 📊 Narzędzia — przegląd

| # | Narzędzie | Typ | Język | Status w Kali | Przydatność |
|---|---|---|---|---|---|
| 1 | **hostapd-mana** | Atak (KARMA/MANA) | C | ✅ `apt install` | 🔥🔥🔥 Podstawa KARMA/MANA |
| 2 | **Snappy** (SpiderLabs) | Detekcja | Python | ❌ Wymaga instalacji | 🔥🔥🔥 Alternatywny fingerprinting |
| 3 | **Eaphammer** | Atak (Enterprise) | Python | ✅ `apt install` | 🔥🔥 WPA2-Enterprise |
| 4 | **RogueAP-Detector** | Detekcja | Python | ❌ Wymaga instalacji | 🔥🔥 Modułowa detekcja |
| 5 | **Wifiphantom** | Detekcja + Atak | JavaScript/Python | ❌ Wymaga instalacji | 🔥 Dashboard + fingerprinting |
| 6 | **Evil-M5Project** | Atak (ESP32) | C++ | ❌ Osobny hardware | 🔥 Mobilne, tanie |
| 7 | **Bettercap** | MITM + Atak | Go | ✅ `apt install` | 🔥 Uniwersalne |

---

## 1. hostapd-mana (SensePost)

### Opis

hostapd-mana to zmodyfikowana wersja demona hostapd (standardowego narzędzia do tworzenia punktów dostępowych w Linuksie), rozwinięta przez SensePost na potrzeby ataków rogue AP. Zaprezentowana na Defcon 22 (2014) jako część MANA Toolkit.

**Kluczowe możliwości:**
- Tryb **KARMA** — odpowiada beaconem na każdy probe request
- Tryb **MANA** — odpowiada również na directed probe requests (ignoruje BSSID)
- **Loud Mode** — emituje beacony z listą popularnych SSID (z pliku `ssid-mana`)
- **EAP credential capture** — przechwytuje handshake EAP (WPA2-Enterprise)
- Integracja z **asleap** i **hashcat** do łamania haseł
- **Wiele BSSID** na jednym interfejsie

### Instalacja

```bash
# Na Kali Linux — z repozytorium
sudo apt update
sudo apt install hostapd-mana mana-toolkit -y

# Sprawdzenie
which hostapd-mana
# → /usr/bin/hostapd-mana

which berate_ap
# → /usr/bin/berate_ap (skrypt pomocniczy MANA)

# Z źródła (jeśli potrzebujesz najnowszej wersji)
git clone https://github.com/sensepost/hostapd-mana.git
cd hostapd-mana
make -j$(nproc)
sudo make install
```

### Podstawowe użycie

```bash
# 1. Tryb KARMA (klasyczny)
sudo hostapd-mana /etc/mana-toolkit/hostapd-karma.conf

# 2. Tryb MANA (zaawansowany)
sudo hostapd-mana /etc/mana-toolkit/hostapd-mana.conf

# 3. Przez skrypt berate_ap (najprościej)
sudo berate_ap --karma wlan1 wlan0    # KARMA
sudo berate_ap --mana wlan1 wlan0     # MANA
sudo berate_ap --mana --loud wlan1 wlan0  # MANA + Loud Mode

# 4. Dodawanie własnych SSID do Loud Mode
echo "AGH_WiFi" | sudo tee -a /usr/share/mana-toolkit/ssid-mana
echo "eduroam" | sudo tee -a /usr/share/mana-toolkit/ssid-mana
echo "Starbucks_WiFi" | sudo tee -a /usr/share/mana-toolkit/ssid-mana
```

### Kluczowe pliki konfiguracyjne

| Plik | Opis |
|---|---|
| `/etc/mana-toolkit/hostapd-karma.conf` | Konfiguracja trybu KARMA |
| `/etc/mana-toolkit/hostapd-mana.conf` | Konfiguracja trybu MANA |
| `/etc/mana-toolkit/hostapd-mana-eaponly.conf` | Tylko EAP capture |
| `/usr/share/mana-toolkit/ssid-mana` | Lista SSID dla Loud Mode |

### Przydatność dla projektu

| Aspekt | Ocena |
|---|---|
| **KARMA / MANA** | 🔥🔥🔥 Podstawa — to JEST narzędzie do tych ataków |
| **Loud Mode** | 🔥🔥🔥 Unikalna cecha MANA, świetny materiał na slajd |
| **EAP capture** | 🔥🔥 Rozszerza projekt o sieci Enterprise |
| **Ograniczenia sprzętowe** | ✅ Działa na TP-Link TL-WDN3200 (Ralink RT5572) |
| **Trudność instalacji** | ✅ `apt install` — trywialne |

---

## 2. Snappy (SpiderLabs / Trustwave)

### Opis

Snappy to lekkie narzędzie w Pythonie do fingerprintingu punktów dostępowych, stworzone przez SpiderLabs. Działa na zasadzie robienia "migawki" (snapshot) — zapisuje hashe SHA256 charakterystyk AP, a następnie porównuje je przy kolejnych wizytach. Jeśli coś się zmieniło — alarm.

**Technika fingerprintingu (nowatorska):**
Snappy nie tylko porównuje SSID czy BSSID. Tworzy fingerprint z:
- Kolejności i obecności Information Elements w ramce Beacon
- Długości pól IE
- Supported Rates i Extended Rates (kolejność, nie tylko wartości)
- Vendor Specific OUI

To **inna technika** niż nasza — Snappy porównuje **strukturę ramki**, nie tylko zawartość IE. Nasz `beacon_diff.py` porównuje wartości IE. Snappy dodaje wymiar: czy ramki z danego BSSID są **strukturalnie identyczne** jak poprzednio.

**Repozytorium:** https://github.com/SpiderLabs/snappy

### Instalacja

```bash
# Wymagania
pip3 install scapy

# Pobranie
git clone https://github.com/SpiderLabs/snappy.git
cd snappy

# Użycie (nie wymaga instalacji — pojedynczy plik)
python3 snap.py --help
```

### Podstawowe użycie

```bash
# 1. Zrób snapshot sieci w zasięgu
sudo python3 snap.py -i wlan0mon -o baseline.json

# 2. Przy kolejnej wizycie — porównaj z baseline
sudo python3 snap.py -i wlan0mon -b baseline.json

# 3. Output (jeśli wykryto zmianę):
# [!] ALERT: New BSSID detected for known SSID 'AGH_Test'
# [!] ALERT: Beacon fingerprint changed for BSSID XX:XX:XX:XX:XX:01
```

### Przydatność dla projektu

| Aspekt | Ocena |
|---|---|
| **Inna technika fingerprintingu** | 🔥🔥🔥 Struktura ramki vs. wartości IE — komplementarne |
| **Materiał do prezentacji** | 🔥🔥🔥 "Snappy robi to inaczej" — świetne porównanie |
| **Jako alternatywa** | 🔥🔥 Można pokazać że istnieją inne podejścia |
| **Ograniczenia** | Wymaga baseline (pierwszego snapshotu). Nie działa na jednorazowym pcap. |
| **Trudność instalacji** | ✅ Pojedynczy plik Python |

---

## 3. Eaphammer

### Opis

Eaphammer to toolkit do przeprowadzania **celowanych** ataków Evil Twin przeciwko sieciom **WPA2-Enterprise**. Stworzony przez s0lst1c3 (Gabriel Ryan).

**Kluczowe możliwości:**
- **Targeted evil twin** — atak na konkretny BSSID (w przeciwieństwie do KARMA/MANA które łapią wszystko)
- **RADIUS server** — wbudowany serwer RADIUS do przechwytywania poświadczeń
- **Hostile portal** — przekierowuje ofiarę na fałszywą stronę logowania (np. firmowy SSO)
- **PMF bypass** — radzi sobie z Protected Management Frames (802.11w)
- **Multi-SSID** — wiele sieci jednocześnie

**Repozytorium:** https://github.com/s0lst1c3/eaphammer

### Instalacja

```bash
# Na Kali Linux
sudo apt install eaphammer -y

# LUB z źródła
git clone https://github.com/s0lst1c3/eaphammer.git
cd eaphammer
sudo ./setup.sh
```

### Podstawowe użycie

```bash
# 1. Skanowanie sieci Enterprise
sudo eaphammer --scan --interface wlan0

# 2. Atak na konkretny BSSID
sudo eaphammer \
    --bssid XX:XX:XX:XX:XX:01 \
    --essid "Corporate_WiFi" \
    --channel 6 \
    --interface wlan1 \
    --auth wpa-eap \
    --creds

# 3. Z hostile portalem
sudo eaphammer \
    --bssid XX:XX:XX:XX:XX:01 \
    --essid "Corporate_WiFi" \
    --interface wlan1 \
    -- hostile-portal
```

### Przydatność dla projektu

| Aspekt | Ocena |
|---|---|
| **WPA2-Enterprise** | 🔥🔥 Rozszerza projekt poza WPA2-Personal |
| **Celowany atak** | 🔥🔥 Inny wektor niż KARMA/MANA |
| **Ograniczenia sprzętowe** | ⚠️ Nie testowaliśmy na RT5572 |
| **Złożoność** | ⚠️ Więcej zależności niż hostapd-mana |
| **Trudność instalacji** | ✅ `apt install` na Kali |

---

## 4. RogueAP-Detector

### Opis

RogueAP Detector to otwarto-źródłowe, modułowe narzędzie do wykrywania rogue AP. Składa się z trzech warstw:

- **Scanners** — zbierają dane o AP (np. z airodump-ng, iwlist)
- **Detectors** — stosują heurystyki do wykrywania rogue AP (duplikat SSID, anomalia RSSI, nieznany BSSID...)
- **Actuators** — wykonują akcje zaradcze (np. wysyłają deauth do rogue AP)

**Repozytorium:** https://github.com/anotherik/RogueAP-Detector

### Instalacja

```bash
git clone https://github.com/anotherik/RogueAP-Detector.git
cd RogueAP-Detector
pip3 install -r requirements.txt
```

### Podstawowe użycie

```bash
# Skanowanie i detekcja
sudo python3 rogueAP-detector.py -i wlan0mon

# Z zapisem do pliku
sudo python3 rogueAP-detector.py -i wlan0mon -o results.json

# Z automatyczną akcją (deauth rogue AP)
sudo python3 rogueAP-detector.py -i wlan0mon --defend
```

### Przydatność dla projektu

| Aspekt | Ocena |
|---|---|
| **Modułowa architektura** | 🔥🔥 Ciekawe podejście — Scanners/Detectors/Actuators |
| **Automatyczna obrona** | 🔥🔥 Aktywnie deauth-uje rogue AP |
| **Porównanie z naszym** | 🔥 Nasz analyze_pcap.py jest offline (pcap → raport), RogueAP-Detector jest online |
| **Trudność instalacji** | ✅ Standardowe (git clone + pip) |

---

## 5. Wifiphantom

### Opis

Wifiphantom to zaawansowane narzędzie monitorujące Wi-Fi, łączące detekcję rogue AP z fingerprintingiem DNS i analizą zachowania atakującego. Oferuje dashboard webowy w czasie rzeczywistym.

**Kluczowe możliwości:**
- **Wi-Fi deception monitoring** — wykrywa rogue AP przez anomalie beaconów
- **DNS fingerprinting** — śledzi zapytania DNS wysyłane przez atakującego
- **Web dashboard** — wyniki w czasie rzeczywistym
- **Alerty** — powiadomienia o podejrzanych AP

**Repozytorium:** https://github.com/capgarrick/Wifiphantom

### Instalacja

```bash
git clone https://github.com/capgarrick/Wifiphantom.git
cd Wifiphantom
pip3 install -r requirements.txt
npm install      # Dashboard webowy
```

### Podstawowe użycie

```bash
# Uruchom z dashboardem
sudo python3 wifiphantom.py -i wlan0mon --web

# Otwórz w przeglądarce: http://localhost:8080
```

### Przydatność dla projektu

| Aspekt | Ocena |
|---|---|
| **Dashboard** | 🔥🔥 Wizualny, efektowny |
| **Złożoność** | ⚠️ Wymaga Node.js, więcej zależności |
| **Testowanie** | ⏳ Do sprawdzenia (możliwe ograniczenia sprzętowe) |

---

## 6. Evil-M5Project (ESP32/M5Stack)

### Opis

Evil-M5Project to projekt implementujący ataki Evil Twin i KARMA na mikrokontrolerze **ESP32** (m.in. M5Stack Cardputer, M5Atom, M5Fire). To przenośne, tanie (~$30) urządzenie wielkości karty kredytowej.

**Kluczowe możliwości:**
- **KARMA attack** — automatyczne przechwytywanie probe requestów
- **Captive portal** — wbudowany serwer HTTP
- **Deauth attack** — wysyłanie ramek deauth
- **Beacon spam** — emisja setek fałszywych SSID
- **W pełni mobilne** — zasilane baterią

**Repozytorium:** https://github.com/7h30th3r0n3/Evil-M5Project

### Instalacja

```bash
# Wymaga Arduino IDE + ESP32 board support
# Nie instalowalne na Kali — wymaga wgrania na ESP32

# Po wgraniu — sterowanie przez przyciski na urządzeniu
# lub przez USB Serial
```

### Podstawowe użycie

Na urządzeniu M5Stack:
1. Wybierz "Karma Attack" z menu
2. Urządzenie skanuje probe requesty
3. Wybierz SSID z listy przechwyconych
4. Captive portal automatycznie się uruchamia

### Przydatność dla projektu

| Aspekt | Ocena |
|---|---|
| **Mobilność** | 🔥🔥🔥 Przenośne, nie wymaga laptopa |
| **Koszt** | 🔥🔥🔥 ~$30 za ESP32 |
| **Ograniczenia** | ❌ Wymaga osobnego hardware'u — nie dla nas |
| **Do prezentacji** | 🔥🔥 Można wspomnieć jako "kierunek rozwoju" |
| **Testowanie** | ❌ Nie mamy sprzętu ESP32 |

---

## 7. Bettercap

### Opis

Bettercap to szwajcarski scyzoryk do ataków sieciowych — modułowy framework w Go, który obsługuje Wi-Fi, Bluetooth, Ethernet, HTTP/HTTPS. Posiada wbudowane moduły do rogue AP.

**Repozytorium:** https://github.com/bettercap/bettercap

### Instalacja

```bash
# Na Kali
sudo apt install bettercap -y

# Sprawdzenie
bettercap -version
```

### Podstawowe użycie (moduł Wi-Fi)

```bash
# Interaktywna sesja
sudo bettercap -iface wlan0

# W lepszymcap:
> wifi.recon on       # Skanowanie sieci
> wifi.show           # Pokaż znalezione AP
> wifi.ap.ssid "AGH_Test"   # Ustaw SSID rogue AP
> wifi.ap on          # Włącz rogue AP
> net.sniff on        # Przechwytywanie ruchu
```

### Przydatność dla projektu

| Aspekt | Ocena |
|---|---|
| **Uniwersalność** | 🔥🔥 Jeden framework do wszystkiego |
| **Wi-Fi AP** | 🔥 Prosty rogue AP, ale bez KARMA/MANA |
| **Porównanie** | 🔥 Warto pokazać że istnieją alternatywy dla airgeddon |
| **Ograniczenia** | Rogue AP w Bettercap jest prostszy niż airgeddon |

---

## 📊 Macierz porównawcza z naszymi narzędziami

| Funkcjonalność | analyze_pcap.py | beacon_diff.py | Snappy | RogueAP-Detector |
|---|---|---|---|---|
| **Analiza pcap offline** | ✅ | ✅ | ✅ (przez baseline) | ❌ (online) |
| **Fingerprinting IE** | ✅ Wartości | ✅ Wartości (diff) | ✅ Struktura ramki | ✅ Podstawowy |
| **Wykrywanie KARMA/MANA** | ✅ 1 BSSID → wiele SSID | ✅ Porównanie BSSID | ⚠️ Przez zmianę baseline | ⚠️ Przez heurystyki |
| **JSON export** | ✅ | ✅ | ✅ | ✅ |
| **Wykresy** | ✅ | ❌ | ❌ | ❌ |
| **Działa na macOS** | ✅ | ✅ | ✅ | ✅ |

---

## 🧪 Które narzędzia testować?

### Priorytet 1 — testować teraz (działają na macOS + Kali):
1. **hostapd-mana** — na Kali VM (z kartami) — do ataków KARMA/MANA
2. **Snappy** — na macOS lub Kali — jako alternatywny fingerprinting

### Priorytet 2 — testować jeśli starczy czasu:
3. **Eaphammer** — na Kali VM — rozszerzenie o WPA2-Enterprise
4. **Bettercap** — na Kali VM — jako alternatywa uniwersalna

### Do wspomnienia w prezentacji (bez testowania):
5. **Evil-M5Project** — ciekawostka: ESP32 za $30
6. **Wifiphantom** — dashboard webowy (zbyt dużo zależności)
7. **RogueAP-Detector** — modułowe podejście do detekcji

---

## 📝 Wnioski z researchu

1. **hostapd-mana jest niezbędny** do KARMA/MANA i już jest w `PLAN_PRAKTYCZNY.md`
2. **Snappy to najciekawsze narzędzie defensywne** — inne podejście do fingerprintingu (struktura ramki vs. wartości IE). Warto przetestować i porównać z naszym `beacon_diff.py`
3. **Eaphammer rozszerza projekt** o WPA2-Enterprise, ale wymaga więcej setupu
4. **Większość narzędzi** jest dostępna przez `apt install` na Kali — zero problemów z instalacją
5. **Nasze narzędzia** (analyze_pcap.py, beacon_diff.py) są **komplementarne**, a nie konkurencyjne — Snappy robi strukturę, my robimy wartości

---

> 🔜 **Next steps:** Po otrzymaniu dostępu do Kali VM — instalacja i test hostapd-mana + Snappy.
> Wyniki testów dodać do raportu końcowego jako sekcję "Porównanie z istniejącymi narzędziami".
