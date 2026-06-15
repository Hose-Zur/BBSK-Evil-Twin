# Detekcja Ataków Evil Twin i Rogue Access Point

**Analiza metod wykrywania fałszywych punktów dostępowych w sieciach 802.11**

---

**Autorzy:** Hubert Czernicki, Piotr Straszak  
**Akademia Górniczo-Hutnicza im. Stanisława Staszica w Krakowie**  
Wydział Informatyki, Elektroniki i Telekomunikacji  

Bezpieczeństwo Sieci Bezprzewodowych | Projekt grupowy | 15 czerwca 2026

---

## 1. Cel i zakres opracowania

Niniejszy raport stanowi dokumentację badawczą projektu poświęconego analizie ataków Evil Twin, KARMA oraz MANA (Rogue Access Point) w sieciach bezprzewodowych standardu IEEE 802.11. Projekt zrealizowany został w warunkach laboratoryjnych z wykorzystaniem dedykowanego sprzętu oraz oprogramowania penetration-testingowego.

Głównym przedmiotem badań jest strona defensywna — identyfikacja i analiza artefaktów umożliwiających wykrycie fałszywego punktu dostępowego. Ataki stanowiły narzędzia do wygenerowania kontrolowanego środowiska testowego.

Zakres prac praktycznych: ataki deauthentykacji, Evil Twin (z DHCP i NAT), KARMA (hostapd-mana), MANA (hostapd-mana z directed probe), przechwycenie WPA handshake, eksperyment 10 cykli ON/OFF Evil Twin, analiza TLS/SNI, testy WiFiSlayer.

---

## 2. Środowisko laboratoryjne

### 2.1 Sprzęt

| Komponent | Specyfikacja |
|---|---|
| System operacyjny | Kali Linux 2024.3 ARM64, VMware |
| Karty Wi-Fi | 2× TP-Link TL-WDN3200 (Ralink RT5572, ID 148f:5572) |
| Karta #1 (monitor/AP) | wlan0, phy4, MAC: 64:70:02:18:B9:22 |
| Karta #2 (monitor) | wlan1, phy5, MAC: 64:70:02:27:0A:9C |
| Oryginalny AP | SSID: 601A, BSSID: 7C:F1:7E:C1:7B:95, kanał 4, WPA2-PSK |
| Urządzenie ofiary | iPhone (BA:A1:0E:08:E0:35) |
| Dodatkowe urządzenia | iPad/Lenovo (1E:89:C2:FF:08:10), E0:1F:FC:86:92:B3 |

### 2.2 Uzasadnienie wyboru sprzętu

Karty TP-Link TL-WDN3200 (chipset Ralink RT5572) wybrano ze względu na natywne wsparcie dla trybów: monitor mode, packet injection (100% po reloadzie sterownika), AP mode, VIF (do 8 interfejsów na PHY). Chipset obsługiwany przez sterownik rt2800usb wbudowany w jądro Linux.

### 2.3 Oprogramowanie

| Narzędzie | Wersja | Przeznaczenie |
|---|---|---|
| airgeddon | latest (git) | Evil Twin + Captive Portal |
| hostapd-mana | 2.6 | Ataki KARMA / MANA |
| airodump-ng / aireplay-ng | latest | Przechwytywanie / deauth |
| mdk4 | latest | Deauth flooding |
| Wireshark | latest | Ręczna analiza ramek |
| Scapy / matplotlib | 2.5.0 / 3.6.3 | Analiza i wykresy |
| hashcat | latest | Łamanie WPA PMKID |
| WiFiSlayer | github.com/waheeb71 | Captive Portal (DNS redirect) |
| **analyze_pcap.py** | **v2.0 (własny)** | **Automatyczna detekcja** |
| **beacon_diff.py** | **v1.0 (własny)** | **Porównanie IE** |

### 2.4 Napotkane problemy

| Problem | Rozwiązanie |
|---|---|
| SSH rozłączał się podczas długich komend | Pliki tymczasowe na hoście + scp |
| Injection 0% | `modprobe -r rt2800usb && modprobe rt2800usb` |
| dnsmasq dpkg broken | Binarka działa bezpośrednio |
| create_ap nie nadawał beaconów | Ręczna konfiguracja hostapd + dnsmasq |
| `pkill -f eviltwin` zabijał SSH | `pgrep -x` zamiast `pkill -f` |
| Captive Portal zablokowany przez Apple CNA | WiFiSlayer + DNS redirect |

---

## 3. Przebieg praktyczny

### 3.1 Rekonesans

Skanowanie `airodump-ng wlan1 -c 4` wykryło 3 urządzenia w sieci 601A. Wszystkie MAC-e zrandomizowane (locally administered).

| Urządzenie | MAC | RSSI |
|---|---|---|
| iPhone (Piotr) | BA:A1:0E:08:E0:35 | -23 dBm |
| iPad/Lenovo | 1E:89:C2:FF:08:10 | -27 dBm |
| Nieznane | E0:1F:FC:86:92:B3 | -33 dBm |

### 3.2 Atak deauthentykacji

Po reloadzie sterownika injection osiągnął 100%. Deauth broadcast (`--deauth 200`) rozłączył wszystkie 3 urządzenia. iPhone po reconnect dostał nowy MAC (iOS randomizacja).

### 3.3 Atak Evil Twin

Evil Twin AP postawiony przez ręczną konfigurację hostapd + dnsmasq. DHCP: 192.168.200.50-150, NAT przez eth0.

| Parametr | Oryginalny AP | Evil Twin |
|---|---|---|
| BSSID | 7C:F1:7E:C1:7B:95 | 64:70:02:18:B9:22 |
| SSID | 601A | 601A |
| Beacony | 3 882 | 2 928 |
| RSSI | -42.1 dBm | **-22.8 dBm** |
| Vendor OUI | Microsoft WPS | **brak** |
| HT Capabilities | LDPC, HT40, SGI | **brak** |

**Rezultat:** iPhone dostał IP 192.168.200.127, iPad 192.168.200.103. Internet działał przez NAT.

### 3.4 Atak KARMA

Hostapd-mana (`enable_mana=0`). KARMA AP przechwycił probe requesty iPhone'a dla SSID "601A" (RSSI -34 dBm), odpowiadając beaconem. Anomalia: 1 BSSID → wiele SSID.

Ograniczenie: iOS 10+ używa pasywnego skanowania — mniej probe requestów.

### 3.5 Atak MANA

Hostapd-mana (`enable_mana=1`) przechwycił directed probe request:  
*"MANA - Directed probe request for SSID '601A' from ba:a1:0e:08:e0:35"*

Captive Portal na iOS zablokowany przez Apple CNA. MANA to atak pasywny — bez deauth.

### 3.6 Captive Portal przez WiFiSlayer

WiFiSlayer (github.com/waheeb71) z DNS redirect `address=/#/192.168.1.1` rozwiązał problem iOS CNA. Hasło **mama1234** przechwycone na stronie "Router Firmware Update".

### 3.7 Eksperyment: 10 cykli ON/OFF Evil Twin

Schemat: iPhone na Evil Twin → wyłączenie AP (`pkill hostapd`, ~5s) → włączenie AP (`create_ap`, ~6s reconnect) → powtórzone 10 razy.

| Metryka | Wartość |
|---|---|
| Pakiety łącznie | 55 490 |
| Beacony Evil Twin | 2 928 |
| Beacony Oryginalny | 3 882 |
| Sukces reconnectu | 10/10 (100%) |
| Średni czas reconnectu | ~6 sekund |

**Wnioski:** iPhone przechodzi automatycznie, ~6s jest niezauważalne. Sequence Numbers pokazują "górki" — wizualny dowód dwóch urządzeń.

### 3.8 WPA Handshake i łamanie

PMKID przechwycony z Evil Twin AP. Hasło `nbi8-yhs5-ajxp` (14 znaków) nie występuje w rockyou.txt. Wymagany mask attack: `?l?l?l?d-?l?l?l?l-?l?l?l?l`. Szacowany czas: godziny na GPU.

### 3.9 TLS SNI Capture

Mimo DoH/DoT przechwycono domeny z TLS Client Hello:  
`setup.icloud.com`, `smp-device-content.apple.com`, `p17-buy.itunes.apple.com`

---

## 4. Metodologia detekcji

### 4.1 Fingerprinting Information Elements

Porównanie IE między AP. Narzędzie: **beacon_diff.py v1.0**.

| IE | Oryginalny AP | Evil Twin | Status |
|---|---|---|---|
| Vendor Specific | Microsoft WPS + 3 OUI | brak | **RÓŻNICA** |
| HT Capabilities | LDPC, HT40, SGI20, SGI40, Tx-STBC | brak | **RÓŻNICA** |
| HT Operation | Primary Ch=4, 20MHz | brak | **RÓŻNICA** |
| Extended Capabilities | obecne | brak | **RÓŻNICA** |
| Power Constraint | 0 dB | brak | **RÓŻNICA** |
| Country | obecne | brak | **RÓŻNICA** |
| Supported Rates | 6-54 Mbps | tożsame | IDENTYCZNE |

**Wynik: 15/18 IE różnych. WERDYKT: EVIL TWIN CONFIRMED.**

### 4.2 Analiza RSSI

| AP | Średni RSSI | Interpretacja |
|---|---|---|
| Evil Twin | **-22.8 dBm** | Karta USB na biurku |
| Oryginalny | **-42.1 dBm** | Router w innym pokoju |

**Delta = 20.3 dBm** — różnica ~100 razy (skala decybelowa jest logarytmiczna).

### 4.3 Sequence Number Analysis

Każde urządzenie ma własny 12-bitowy licznik (0-4095).

| AP | Zakres |
|---|---|
| Oryginalny | 0 – 4095 (pełny cykl) |
| Evil Twin | 0 – 2045 |

Brak nakładania = dwa różne urządzenia. "Górki" na wykresie = 10 cykli ON/OFF.

---

## 5. Porównanie metod ataku

| Cecha | Evil Twin | KARMA | MANA |
|---|---|---|---|
| Mechanizm | Klonowanie SSID + deauth | Odpowiada na probe req. | Directed probes + Loud |
| Deauth | **TAK** | NIE | NIE |
| BSSID:SSID | Wiele : 1 | 1 : wiele | 1 : wiele |
| Skuteczność | **WYSOKA** | ŚREDNIA | BARDZO WYSOKA |
| Stealth | Niski | **Wysoki** | **Wysoki** |
| Łatwość wykrycia | ŁATWE | Trudniejsze | Trudniejsze |
| Nasze wyniki | **PEŁEN SUKCES** | Częściowy | Częściowy |

---

## 6. Wnioski

1. Trzy metody detekcji (IE fingerprinting, RSSI, Sequence Numbers) są **komplementarne** — połączenie daje 100% pewności.

2. **Evil Twin** — najskuteczniejszy atak (100% reconnect rate), ale najłatwiejszy do wykrycia.

3. **KARMA** — stealthowy, pasywny. Ograniczony przez iOS (pasywne skanowanie).

4. **MANA** — najbardziej zaawansowany technicznie. Pełna funkcjonalność wymaga mana-toolkit.

5. **WiFiSlayer** — rozwiązał problem Captive Portala przez DNS redirect.

6. **Własne narzędzia** — `analyze_pcap.py` (v2.0) i `beacon_diff.py` (v1.0) mogą służyć jako lekki WIDS. Open source, MIT license.

---

## 7. Bibliografia

1. **airgeddon** — github.com/v1s1t0r1sh3r3/airgeddon — Framework Evil Twin + Captive Portal
2. **hostapd-mana** (SensePost) — github.com/sensepost/hostapd-mana — Ataki KARMA/MANA
3. **WiFiSlayer** — github.com/waheeb71/WiFiSlayer — DNS redirect captive portal
4. **Snappy** (SpiderLabs) — github.com/SpiderLabs/snappy — AP fingerprinting
5. **Eaphammer** — github.com/s0lst1c3/eaphammer — Evil Twin WPA2-Enterprise
6. **airodump-ng / aireplay-ng** — aircrack-ng.org
7. **hashcat** — hashcat.net — Łamanie WPA/WPA2
8. **analyze_pcap.py / beacon_diff.py** — github.com/Hose-Zur/BBSK-Evil-Twin

---

*Repozytorium: github.com/Hose-Zur/BBSK-Evil-Twin, branch: docs/complete-documentation-v2*
