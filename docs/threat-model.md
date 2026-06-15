# Threat Model — Atak Evil Twin

## Scope

Niniejszy model zagrożeń obejmuje atak typu Evil Twin / Rogue Access Point w środowisku laboratoryjnym. Model koncentruje się na trzech metodach detekcji zaimplementowanych w projekcie.

---

## Zaufane i niezaufane strefy

```
┌───────────────────────────────────────────────────────┐
│  STREFA NIEZAUFANA (przestrzeń radiowa)                │
│                                                       │
│  ┌──────────────────┐     ┌──────────────────────┐   │
│  │ Oryginalny AP    │     │ Evil Twin AP (atak)   │   │
│  │ Telefon A        │     │ Karta #2 (Kali)       │   │
│  │ SSID: AGH_Test   │     │ SSID: AGH_Test        │   │
│  │ ZAUFANY          │     │ NIEZAUFANY            │   │
│  └──────────────────┘     └──────────────────────┘   │
│                                                       │
│  ┌──────────────────┐     ┌──────────────────────┐   │
│  │ Klient (ofiara)  │     │ Karta #1 (monitor)   │   │
│  │ Telefon B        │     │ Narzędzie detekcyjne │   │
│  └──────────────────┘     └──────────────────────┘   │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## Aktorzy zagrożenia

| Aktor | Opis | Motywacja | Poziom wiedzy |
|---|---|---|---|
| **Atakujący** | Osoba z fizycznym dostępem do zasięgu sieci Wi-Fi, wyposażona w Kali Linux + 2× karty z obsługą monitor/injection | Przechwycenie danych uwierzytelniających (hasła WPA2) | Wysoki — zna protokół 802.11 |
| **Ofiara** | Użytkownik sieci Wi-Fi (telefon/tablet/laptop) | Chce uzyskać dostęp do Internetu | Niski/zero |
| **Analityk** | Osoba prowadząca detekcję (student, badacz, administrator) | Wykrycie i udokumentowanie ataku | Wysoki |

---

## Wektory ataku

### 1. Ramki deauthentication (deauth)

| Właściwość | Opis |
|---|---|
| **Mechanizm** | Atakujący wysyła fałszywe ramki deauth do klienta z adresem źródłowym oryginalnego AP |
| **Standard** | IEEE 802.11 — ramki zarządzania nie są szyfrowane (chyba że włączono PMF/802.11w) |
| **Narzędzie** | mDK3 / aireplay-ng (wbudowane w airgeddon) |
| **Efekt** | Klient rozłącza się z oryginalnym AP i automatycznie łączy z Evil Twin (silniejszy sygnał) |

### 2. Evil Twin AP

| Właściwość | Opis |
|---|---|
| **Mechanizm** | Postawienie punktu dostępowego o identycznym SSID co oryginalny AP |
| **Sygnał** | Celowo wyższy niż oryginalny AP (karta USB blisko klienta) |
| **Narzędzie** | airgeddon + hostapd/dnsmasq |
| **Efekt** | Klient łączy się z fałszywym AP bez świadomości różnicy |

### 3. Captive Portal

| Właściwość | Opis |
|---|---|
| **Mechanizm** | Strona logowania wyświetlana po połączeniu z Evil Twin |
| **Wygląd** | Naśladuje ekran logowania popularnych sieci (np. AGH, UAP, Starbucks) |
| **Narzędzie** | airgeddon (wbudowany moduł captive portal) |
| **Efekt** | Ofiara wpisuje hasło, które trafia do atakującego |

---

## Powierzchnia ataku

### Podatności protokołu 802.11

| Podatność | Opis | Wpływ na projekt |
|---|---|---|
| **Ramki zarządzania nieszyfrowane** | Deauth, Beacon, Probe — wszystkie ramki zarządzania 802.11 przesyłane są w czystym tekście | Umożliwia atak + pozwala na detekcję |
| **Brak PMF** | Protected Management Frames (802.11w) chronią przed deauth, ale nie są powszechnie stosowane | Jeśli PMF włączony — atak trudniejszy, ale detekcja wciąż możliwa |
| **Brak walidacji AP** | Klient nie weryfikuje tożsamości punktu dostępowego (brak certyfikatów, brak EAP-TLS w sieciach domowych) | Podstawa ataku Evil Twin |
| **RSSI easy to spoof** | Moc sygnału zależy od odległości — nie ma mechanizmu weryfikacji | Utrudnia detekcję |

### Powierzchnia ataku w projekcie

| Element | Czy zagrożony? | Uwagi |
|---|---|---|
| Telefon A (AP) | Tak — deauth | Nie można zabezpieczyć bez PMF |
| Telefon B (ofiara) | Tak — kradzież hasła | Captive portal |
| Karta #1 (monitor) | Nie — tylko nasłuch | Pasywna |
| Karta #2 (Evil) | N/A — narzędzie ataku | — |
| analyze_pcap.py | Nie — offline | Analiza po fakcie |

---

## Metody detekcji i ich skuteczność

| Metoda | Co wykrywa | Skuteczność | Ograniczenia |
|---|---|---|---|
| **Fingerprinting IE** | Różne Supported Rates, Vendor Specific | Wysoka — jeśli urządzenia różnych producentów | Niska — jeśli oba urządzenia tego samego producenta |
| **Analiza RSSI** | Nienaturalny skok sygnału | Średnia — zależna od fizycznego rozmieszczenia | Łatwa do zmaniпулирования dla doświadczonego atakującego |
| **Sequence Numbers** | Rozbieżne strumienie seq | Wysoka — niezależna od producenta | Wymaga analizy >1 ramki |

---

## Mitygacja (rekomendacje)

| Technika | Poziom ochrony | Uwagi |
|---|---|---|
| **PMF (802.11w)** | 🔒🔒🔒 | Chroni przed deauth — atak trudniejszy |
| **WIDS/WIPS** | 🔒🔒🔒 | Systemy wykrywania włamań Wi-Fi |
| **EAP-TLS / certyfikaty** | 🔒🔒🔒🔒 | Weryfikacja tożsamości AP |
| **Analiza seq numbers** | 🔒 | Wykrywa, nie zapobiega |
| **VPN na kliencie** | 🔒🔒 | Chroni ruch po połączeniu, nie wykrywa ataku |
