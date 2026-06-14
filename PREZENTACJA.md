# Skrypt Prezentacji — Evil Twin / Rogue AP: Ataki i Detekcja

> **Projekt:** BBSK-Evil-Twin | **Przedmiot:** Bezpieczeństwo Sieci Bezprzewodowych
>
> **Czas:** ~15 minut | **Slajdów:** 16 | **AGH WIEiT**

---

## 📐 Struktura prezentacji

| # | Slajd | Czas | Minuta |
|---|---|---|---|
| 1 | Tytułowy | 0:30 | 0:00–0:30 |
| 2 | Agenda | 0:30 | 0:30–1:00 |
| 3 | Czym jest Evil Twin / Rogue AP? | 1:00 | 1:00–2:00 |
| 4 | Atak KARMA | 1:00 | 2:00–3:00 |
| 5 | Atak MANA | 1:00 | 3:00–4:00 |
| 6 | Porównanie trzech ataków | 1:00 | 4:00–5:00 |
| 7 | Metody detekcji — przegląd | 1:00 | 5:00–6:00 |
| 8 | Metoda 1: Fingerprinting IE | 1:00 | 6:00–7:00 |
| 9 | Metoda 2: Analiza RSSI | 1:00 | 7:00–8:00 |
| 10 | Metoda 3: Sequence Numbers | 1:00 | 8:00–9:00 |
| 11 | Środowisko laboratoryjne | 1:00 | 9:00–10:00 |
| 12 | Wyniki: Evil Twin | 1:00 | 10:00–11:00 |
| 13 | Wyniki: KARMA i MANA | 1:00 | 11:00–12:00 |
| 14 | Mitygacja i przeciwdziałanie | 1:00 | 12:00–13:00 |
| 15 | Podsumowanie i wnioski | 1:00 | 13:00–14:00 |
| 16 | Pytania | 1:00 | 14:00–15:00 |

---

## Slajd 1 — Tytułowy [0:00–0:30]

### Na slajdzie:
```
─────────────────────────────────────────
  Evil Twin i Rogue Access Points

  Analiza ataku oraz metody wykrywania
  i przeciwdziałania

  KARMA • MANA • Evil Twin

  [Imię Nazwisko, nr albumu]
  [Imię Nazwisko, nr albumu]

  Bezpieczeństwo Sieci Bezprzewodowych
  AGH WIEiT, 2025/2026
─────────────────────────────────────────
```

### Co powiedzieć:
> "Dzień dobry. Nazywam się [Imię] i razem z [Imię] przedstawimy wyniki naszego projektu dotyczącego ataków typu Evil Twin i Rogue Access Point. Skupimy się na trzech typach ataków — klasycznym Evil Twin, ataku KARMA oraz zaawansowanym ataku MANA — oraz pokażemy, jak można je wykryć analizując ramki Beacon w standardzie 802.11."

---

## Slajd 2 — Agenda [0:30–1:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Agenda

  1. Wprowadzenie — czym są rogue AP
  2. Trzy typy ataków:
     • Evil Twin (klasyczny)
     • KARMA (probe-based)
     • MANA (zaawansowany)
  3. Trzy metody detekcji:
     • Fingerprinting IE
     • Analiza RSSI
     • Sequence Numbers
  4. Demonstracja praktyczna
  5. Mitygacja i wnioski
─────────────────────────────────────────
```

### Co powiedzieć:
> "Zaczniemy od wyjaśnienia, czym są rogue access pointy i dlaczego stanowią zagrożenie. Potem omówimy trzy typy ataków — od najprostszego Evil Twin, przez KARMA, aż po zaawansowany MANA. Następnie pokażemy, jak wykrywać te ataki analizując ramki Beacon — to jest główna część badawcza naszego projektu. Na koniec zaprezentujemy wyniki praktycznej demonstracji i omówimy metody przeciwdziałania."

---

## Slajd 3 — Czym jest Evil Twin / Rogue AP? [1:00–2:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Czym jest Rogue Access Point?

  Definicja:
  Nieautoryzowany punkt dostępowy, który
  podszywa się pod legalną sieć Wi-Fi

  ┌──────────────┐         ┌──────────────────┐
  │ Legalny AP   │         │ Rogue AP         │
  │ SSID: AGH    │         │ SSID: AGH        │
  │ MAC: XX:01   │         │ MAC: YY:02       │
  └──────────────┘         └──────────────────┘
         │                          │
         └──────────┬───────────────┘
                    │
            ┌───────▼────────┐
            │ Klient (ofiara)│
            │ Nie widzi      │
            │ różnicy        │
            └────────────────┘

  Zagrożenie:
  • Kradzież haseł (captive portal)
  • Przechwycenie ruchu (MITM)
  • Atak na WPA2-Enterprise (EAP)
─────────────────────────────────────────
```

### Co powiedzieć:
> "Rogue Access Point to nieautoryzowany punkt dostępowy, który podszywa się pod legalną sieć Wi-Fi. Atakujący stawia własny AP o takim samym SSID jak sieć ofiary. Klient — czy to telefon, czy laptop — nie jest w stanie odróżnić prawdziwego AP od fałszywego, ponieważ standard 802.11 nie przewiduje mechanizmu weryfikacji tożsamości punktu dostępowego w sieciach domowych. Konsekwencje? Kradzież haseł przez captive portal, przechwycenie całego ruchu sieciowego, a w przypadku sieci Enterprise — przechwycenie poświadczeń EAP."

---

## Slajd 4 — Atak KARMA [2:00–3:00]

### Na slajdzie:
```
─────────────────────────────────────────
  KARMA Attack
  (Karma Attacks Radio Machines Automatically)

  Mechanizm:
  1. Rogue AP nasłuchuje probe requestów
  2. Każdy klient wysyła zapytania o znane sieci
  3. KARMA odpowiada beaconem z żądanym SSID
  4. Klient łączy się automatycznie

  ┌──────────┐  probe: "Starbucks_WiFi?"  ┌────────────┐
  │ Telefon  │ ──────────────────────────▶ │ KARMA AP   │
  │ (ofiara) │ ◀────────────────────────── │            │
  └──────────┘  beacon: "Tak, jestem!"     └────────────┘

  Kluczowa cecha:
  • Nie trzeba znać SSID-u z góry
  • Łapie KAŻDEGO klienta w zasięgu
  • JEDEN BSSID → WIELE SSID

  Ograniczenia:
  • iOS 10+, Android 8+ — skanowanie pasywne
  • Directed probe requests
─────────────────────────────────────────
```

### Co powiedzieć:
> "Atak KARMA — Karma Attacks Radio Machines Automatically — działa na innej zasadzie niż klasyczny Evil Twin. Tutaj nie celujemy w konkretną sieć. Zamiast tego nasłuchujemy probe requestów — to zapytania, które każdy telefon wysyła, szukając znanych sobie sieci. Jeśli telefon kiedykolwiek łączył się z 'Starbucks_WiFi', to co jakiś czas wysyła zapytanie: 'Hej, jest tu Starbucks_WiFi?'. KARMA przechwytuje to zapytanie i natychmiast odpowiada: 'Tak, to ja!'. Klient łączy się automatycznie. Kluczowa cecha: nie musimy znać SSID-u — łapiemy wszystko, co klienci sami zdradzą w probe requestach. W空气ze widać to jako JEDEN BSSID nadający WIELE różnych SSID."

---

## Slajd 5 — Atak MANA [3:00–4:00]

### Na slajdzie:
```
─────────────────────────────────────────
  MANA Attack
  (SensePost, Defcon 22)

  Ulepszenia względem KARMY:

  ✓ Odpowiada na DIRECTED probe requests
    (ignoruje docelowy BSSID)

  ✓ Loud Mode — emituje popularne SSID
    co ~10 sekund (beacony z 20+ SSID)

  ✓ Multiple BSSID — jeden interfejs
    emuluje wiele wirtualnych AP

  ✓ EAP Capture — przechwytuje handshake
    dla sieci Enterprise (eduroam itp.)

  Narzędzie: hostapd-mana
  sudo apt install hostapd-mana
─────────────────────────────────────────
```

### Co powiedzieć:
> "MANA Toolkit to rozwinięcie ataku KARMA, zaprezentowane przez SensePost na Defcon 22. MANA rozwiązuje trzy główne ograniczenia KARMY. Po pierwsze — odpowiada nawet na directed probe requests, czyli zapytania skierowane do konkretnego BSSID. Po drugie — ma tryb Loud Mode: co 10 sekund emituje beacony z listą 20-30 popularnych SSID, aktywnie 'reklamując' się klientom. Po trzecie — potrafi przechwytywać handshake EAP, co oznacza że działa również przeciwko sieciom Enterprise jak eduroam. Narzędziem jest hostapd-mana, dostępny w standardowym repozytorium Kali."

---

## Slajd 6 — Porównanie trzech ataków [4:00–5:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Porównanie trzech typów ataków

  |             | Evil Twin | KARMA  | MANA   |
  |-------------|-----------|--------|--------|
  | Cel         | 1 SSID    | Wszystkie probe req | Wszystkie + loud |
  | Deauth      | ✅ Tak    | ❌ Nie | ❌ Nie |
  | BSSID:SSID  | 1:N       | 1:N    | 1:N    |
  | Wykrywanie  | Duplikat  | 1 BSSID | Loud   |
  |             | SSID      | → wiele| beacony|
  |             |           | SSID   |        |

  W skrócie:
  Evil Twin = klonowanie KONKRETNEJ sieci
  KARMA/MANA = łapanie KAŻDEGO klienta
─────────────────────────────────────────
```

### Co powiedzieć:
> "Podsumujmy różnice między trzema typami ataków. Evil Twin klonuje jedną, konkretną sieć — do tego potrzebuje znać SSID i używa deauth, żeby zmusić klienta do przełączenia. KARMA i MANA działają odwrotnie: nie celują w konkretną sieć, tylko czekają aż klient sam się 'przedstawi' w probe requeście. W eterze wygląda to zupełnie inaczej: Evil Twin to ta sama nazwa sieci z dwóch różnych urządzeń. KARMA i MANA to jedno urządzenie nadające wiele różnych nazw sieci. To fundamentalne rozróżnienie, które wykorzystamy w detekcji."

---

## Slajd 7 — Metody detekcji — przegląd [5:00–6:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Trzy metody detekcji ataku Rogue AP

  Metoda 1: Fingerprinting IE
  → Porównanie Information Elements
    w ramkach Beacon (Supported Rates,
    Vendor Specific, HT Capabilities)

  Metoda 2: Analiza RSSI
  → Monitorowanie poziomu sygnału
    (Radiotap dBm Antenna Signal)

  Metoda 3: Sequence Numbers
  → Śledzenie numerów sekwencyjnych
    ramek Beacon (802.11 SC field)

  Wszystkie 3 metody bazują na
  ANALIZIE RAMek BEACON 802.11
─────────────────────────────────────────
```

### Co powiedzieć:
> "Jak wykryć atak rogue AP, skoro klient nie widzi różnicy? Odpowiedź leży w ramkach Beacon — to 'ogłoszenia', które każdy punkt dostępowy wysyła co ~100 milisekund, informując o swoim istnieniu. My, jako obserwatorzy z kartą w trybie monitor, możemy przechwycić te ramki i porównać je między sobą. Zidentyfikowaliśmy trzy komplementarne metody: fingerprinting Information Elements, analizę RSSI, oraz śledzenie Sequence Numbers. Żadna z nich pojedynczo nie daje 100% pewności, ale wszystkie trzy razem — tak."

---

## Slajd 8 — Metoda 1: Fingerprinting IE [6:00–7:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Metoda 1: Fingerprinting IE

  Information Elements w ramce Beacon:

  Tag 0:  SSID = "AGH_Test"
  Tag 1:  Supported Rates = 6,12,24,36 Mbps
  Tag 3:  DSSS Channel = 6
  Tag 45: HT Capabilities = LDPC, SGI20...
  Tag 50: Extended Rates = 48,54 Mbps
  Tag 221: Vendor Specific
          • Apple (OUI: 00:0C:03)      ← AP #1
          • Ralink (OUI: A4:C0:C7)     ← AP #2

  RÓŻNY producent układu Wi-Fi
  → RÓŻNE urządzenie sprzętowe
  → DOWÓD na Evil Twin!

  Narzędzie: beacon_diff.py (nasz skrypt)
─────────────────────────────────────────
```

### Co powiedzieć:
> "Pierwsza metoda to fingerprinting Information Elements. Każda ramka Beacon zawiera zestaw tagów — tzw. Information Elements — które opisują możliwości punktu dostępowego. Dwa różne urządzenia sprzętowe — nawet jeśli nadają ten sam SSID — będą miały różne charakterystyki. Na przykład telefon Apple wyśle Vendor Specific tag z identyfikatorem 00:0C:03, podczas gdy karta Wi-Fi na chipsecie Ralink — A4:C0:C7. To jest twardy dowód: jeśli dwa AP z tym samym SSID mają różne OUI, to na pewno są to dwa różne fizyczne urządzenia. Napisaliśmy do tego narzędzie beacon_diff.py, które automatycznie porównuje wszystkie IE między dwoma BSSID."

---

## Slajd 9 — Metoda 2: Analiza RSSI [7:00–8:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Metoda 2: Analiza RSSI

  RSSI = Received Signal Strength Indicator
  Źródło: Radiotap Header → dBm Antenna Signal

  ┌────────────────────────────────────┐
  │ RSSI [dBm]                         │
  │ -20 ┤                    ● Evil    │
  │ -30 ┤          ● ● ● ● ● ● Twin    │
  │ -40 ┤    ● ● ●                      │
  │ -50 ┤ ● ●                           │
  │ -60 ┤              Oryginalny AP    │
  │     └──────────────────────── czas  │
  │                                     │
  │  Δ RSSI > 15 dBm → ANOMALIA        │
  └────────────────────────────────────┘

  Jeśli jedno urządzenie ma
  nienaturalnie silny sygnał →
  prawdopodobnie atakujący
  z bliskiej odległości
─────────────────────────────────────────
```

### Co powiedzieć:
> "Druga metoda to analiza RSSI — poziomu sygnału. Wartość RSSI jest zapisana w nagłówku Radiotap każdej przechwyconej ramki. Atakujący zwykle umieszcza swoją kartę Wi-Fi blisko ofiary, żeby mieć silniejszy sygnał niż odległy, legalny AP. Jeśli widzimy dwa urządzenia nadające ten sam SSID, a różnica w średnim RSSI przekracza 10-15 dBm — to jest anomalia. Oryginalny AP, stojący gdzieś w kącie sali, będzie miał -50 dBm, a karta atakującego na stole obok ofiary pokaże -25 dBm. Ta metoda ma ograniczenie — doświadczony atakujący może dostosować moc nadawania."

---

## Slajd 10 — Metoda 3: Sequence Numbers [8:00–9:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Metoda 3: Sequence Numbers

  Każde urządzenie Wi-Fi ma własny,
  sprzętowy licznik ramek (12-bit)

  ┌────────────────────────────────────┐
  │ Sequence Number                     │
  │ 4000 ┤                    ● ● ● ●  │
  │ 3000 ┤              ● ● ●          │
  │ 2000 ┤        ● ● ●                │ AP #2
  │ 1000 ┤  ● ● ●                      │ (Evil Twin)
  │    0 ┤ ●                  AP #1    │
  │      └─────────────────────── czas  │
  │                                     │
  │  DWA strumienie = DWA urządzenia   │
  │  → DOWÓD na Evil Twin              │
  └────────────────────────────────────┘

  Zaleta: niezależne od producenta
  Sequence Number rośnie z każdą ramką
─────────────────────────────────────────
```

### Co powiedzieć:
> "Trzecia metoda — moim zdaniem najmocniejsza — to analiza Sequence Numbers. Każda karta Wi-Fi ma 12-bitowy sprzętowy licznik, który inkrementuje się z każdą wysłaną ramką. Jeśli dwa urządzenia nadają ten sam SSID, to każde z nich ma swój własny, niezależny licznik. Na wykresie zobaczymy DWA osobne strumienie numerów sekwencyjnych — to jest fizyczny dowód, że nadają dwa różne urządzenia. W przeciwieństwie do RSSI, tej metody nie da się zmanipulować — licznik jest w hardware. W przeciwieństwie do IE fingerprintingu, działa nawet jeśli oba urządzenia są tego samego producenta."

---

## Slajd 11 — Środowisko laboratoryjne [9:00–10:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Środowisko laboratoryjne

  Sprzęt:
  • Kali Linux VM (VirtualBox/Parallels)
  • 2× TP-Link TL-WDN3200 (Ralink RT5572)
    - Karta 1: tryb monitor (airodump-ng)
    - Karta 2: tryb AP (evil twin)
  • Telefon A: hotspot (oryginalny AP)
  • Telefon B: klient-ofiara

  Narzędzia:
  • airgeddon — klasyczny Evil Twin
  • hostapd-mana — KARMA i MANA
  • airodump-ng — przechwytywanie ramek
  • analyze_pcap.py — automatyczna analiza
  • beacon_diff.py — porównanie IE
  • Wireshark — weryfikacja ręczna
─────────────────────────────────────────
```

### Co powiedzieć:
> "Do przeprowadzenia praktycznej części wykorzystaliśmy Kali Linux z dwoma kartami Wi-Fi TP-Link na chipsecie Ralink RT5572 — potwierdziliśmy, że obsługują zarówno tryb monitor, jak i tryb AP. Jako ofiarę użyliśmy dwóch telefonów — jeden jako hotspot udający legalną sieć, drugi jako klienta. Do ataku Evil Twin użyliśmy airgeddon, do KARMA i MANA — hostapd-mana. Do analizy napisaliśmy własne skrypty w Pythonie: analyze_pcap.py do automatycznej analizy i beacon_diff.py do szczegółowego porównania IE."

---

## Slajd 12 — Wyniki: Evil Twin [10:00–11:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Wyniki praktyczne: Evil Twin

  Screenshot: analyze_pcap.py
  [!] UWAGA: 2 urządzeń nadaje z SSID='AGH_Test'

  AP #1 (telefon):
    Vendor Specific: Apple (OUI: 00:0C:03)
    Avg RSSI: -42 dBm

  AP #2 (Kali):
    Vendor Specific: Ralink (OUI: A4:C0:C7)
    Avg RSSI: -28 dBm

  ✓ Fingerprinting IE: RÓŻNE OUI
  ✓ RSSI: anomalia Δ = 14 dBm
  ✓ Seq Numbers: 2 strumienie

  WERDYKT: EVIL TWIN POTWIERDZONY
  [Wykres: Sequence Numbers – rozwidlenie]
─────────────────────────────────────────
```

### Co powiedzieć:
> "Oto wyniki z praktycznego wykonania ataku Evil Twin. Nasz skrypt analyze_pcap.py automatycznie wykrył dwa urządzenia nadające SSID 'AGH_Test'. AP numer 1 — telefon Apple — ma charakterystyczny OUI 00:0C:03. AP numer 2 — nasza karta Kali na Ralinku — pokazuje OUI A4:C0:C7. Różnica w średnim RSSI to 14 dBm, co jest anomalią. Na wykresie Sequence Numbers widać dwa niezależne strumienie. Wszystkie trzy metody detekcji zgodnie wskazują: to jest atak Evil Twin."

---

## Slajd 13 — Wyniki: KARMA i MANA [11:00–12:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Wyniki praktyczne: KARMA i MANA

  KARMA — jeden BSSID, wiele SSID:
  BSSID: YY:YY:YY:YY:YY:02
  ├─ SSID: Starbucks_WiFi
  ├─ SSID: Hotel_Guest
  ├─ SSID: Airport_Free
  └─ SSID: Home_Network

  MANA — to samo + Loud Mode:
  Co 10s seria beaconów z 20+ SSID
  Wykryte przez analizę: 1 BSSID → 24 SSID

  Detekcja:
  ✓ Anomalia: 1 BSSID → wiele SSID
  ✓ Brak deauth (w przeciwieństwie do ET)
  ✓ Dla MANA: periodyczne serie beaconów

  [Screenshot: Wireshark z kolumną SSID]
─────────────────────────────────────────
```

### Co powiedzieć:
> "Ataki KARMA i MANA wyglądają w eterze zupełnie inaczej. Zamiast duplikatu SSID, widzimy JEDEN BSSID — jedną kartę — która nadaje WIELE różnych SSID. W przypadku KARMA, są to SSID-y z probe requestów klientów. W przypadku MANA, dodatkowo obserwujemy periodyczne serie beaconów — co 10 sekund karta 'reklamuje' 20-30 popularnych sieci. Nasze narzędzia wykryły tę anomalię: jeden BSSID z 24 różnymi SSID. To niemożliwe w normalnej sieci — legalny AP nadaje tylko swój jeden SSID."

---

## Slajd 14 — Mitygacja i przeciwdziałanie [12:00–13:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Mitygacja — jak się bronić?

  Dla administratorów sieci:
  ✓ WIDS/WIPS — systemy wykrywania włamań
    (monitorują duplikaty SSID, anomalie RSSI)
  ✓ 802.11w (PMF) — Protected Management
    Frames (chroni przed deauth)
  ✓ EAP-TLS — certyfikaty dla AP
    (klient weryfikuje tożsamość AP)

  Dla użytkowników:
  ✓ VPN — szyfruje ruch nawet na rogue AP
  ✓ Unikanie otwartych sieci Wi-Fi
  ✓ Sprawdzanie certyfikatów HTTPS

  Nasze narzędzie: analyze_pcap.py
  — może służyć jako lekki WIDS
─────────────────────────────────────────
```

### Co powiedzieć:
> "Jak się bronić? Na poziomie enterprise: systemy WIDS/WIPS, które monitorują eter i wykrywają anomalie — dokładnie to, co robi nasz skrypt, tylko w czasie rzeczywistym. Protected Management Frames — 802.11w — chronią przed fałszywymi ramkami deauth, ale nie przed samym Evil Twin. Najskuteczniejsza ochrona to EAP-TLS: klient weryfikuje certyfikat punktu dostępowego, więc nie da się podszyć. Dla zwykłego użytkownika: VPN. Nawet jeśli połączy się z rogue AP, cały ruch jest szyfrowany i atakujący widzi tylko 'szum'."

---

## Slajd 15 — Podsumowanie i wnioski [13:00–14:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Podsumowanie

  ✓ Trzy typy ataków:
    Evil Twin → KARMA → MANA
    (od prostego klonowania do zaawansowanego
     przechwytywania EAP)

  ✓ Trzy metody detekcji:
    IE Fingerprinting + RSSI + Sequence Numbers
    → wszystkie bazują na ramkach Beacon 802.11

  ✓ Praktyczna weryfikacja:
    Wszystkie ataki przeprowadzone i wykryte
    w kontrolowanym środowisku lab.

  ✓ Opracowane narzędzia:
    analyze_pcap.py + beacon_diff.py
    (open source, Python, MIT license)
─────────────────────────────────────────
```

### Co powiedzieć:
> "Podsumowując. Po pierwsze: omówiliśmy trzy typy ataków — Evil Twin, KARMA i MANA — pokazując jak ewoluowała technika rogue AP od prostego klonowania SSID do zaawansowanego przechwytywania EAP. Po drugie: zademonstrowaliśmy trzy metody detekcji — fingerprinting IE, analizę RSSI i śledzenie Sequence Numbers — wszystkie oparte na analizie ramek Beacon. Po trzecie: wszystkie ataki zostały przez nas przeprowadzone i wykryte w praktyce. Po czwarte: opracowane przez nas narzędzia są dostępne jako open source i mogą służyć jako lekki system detekcji."

---

## Slajd 16 — Pytania [14:00–15:00]

### Na slajdzie:
```
─────────────────────────────────────────
  Pytania?

  Repozytorium: [link do repo]
  Narzędzia: analyze_pcap.py, beacon_diff.py
  Dokumentacja: docs/, PLAN_PRAKTYCZNY.md

  Dziękujemy za uwagę!
─────────────────────────────────────────
```

### Co powiedzieć:
> "To wszystko z naszej strony. Jeśli mają Państwo pytania — chętnie odpowiemy. Wszystkie narzędzia i dokumentacja są dostępne w naszym repozytorium. Dziękujemy za uwagę."

---

## 🎯 Notatki dla prezentera

### Timing:
- **Nie spiesz się.** Lepiej pominąć slajd 13 (KARMA/MANA wyniki) niż przyspieszać do niezrozumiałości.
- Slajdy 8-10 to **serce prezentacji** — tu pokazujesz metodologię badawczą. Daj im czas.
- Slajdy 12-13 to **dowód** — pokaż screenshoty, nie tylko mów o nich.

### Na co zwrócić uwagę prowadzącego:
- Że **wszystkie metody detekcji** opierają się na analizie ramek Beacon — to jest spójna metodologia
- Że **wykrywamy pasywnie** — nie zakłócamy ruchu, tylko obserwujemy (jak WIDS)
- Że narzędzia są **własne** (analyze_pcap.py, beacon_diff.py), nie tylko gotowe rozwiązania

### Jeśli zostanie czas na pytania:
- "Jak to się ma do WiFi 6/6E?" → Te same ramki Beacon, tylko więcej IE. Metody działają.
- "Czy WPA3 chroni przed Evil Twin?" → Częściowo — SAE utrudnia, ale nie zapobiega. Evil Twin z WPA3-Transition mode nadal działa.
- "Czy to wykryje Pineapple?" → Tak — WiFi Pineapple używa dokładnie tych samych mechanizmów (KARMA/MANA).

### Backup slide (jeśli czas):
- Slajd z tabelą porównawczą OUI (najpopularniejsi producenci)
- Slajd z architekturą systemu (diagram z docs/architecture.md)
- Slajd z omówieniem narzędzia Snappy (jako alternatywne podejście do fingerprintingu)
