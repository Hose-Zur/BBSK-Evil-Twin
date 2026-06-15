---
theme: none
title: Ataki Evil Twin, KARMA i MANA
class: text-center
transition: fade
---

<style>
:root { --agh-red: #D41920; --agh-dark: #1A1A2E; --agh-gray: #666; }
h1 { color: var(--agh-red) !important; font-size: 2.2em !important; }
h2 { color: var(--agh-dark) !important; border-bottom: 3px solid var(--agh-red); padding-bottom: 0.2em; }
.slidev-layout { padding: 2em 3em !important; }
.col-left { border-right: 1px solid #ddd; padding-right: 2em; }
.col-right { padding-left: 2em; }
.highlight { color: var(--agh-red); font-weight: bold; }
</style>

---
layout: center
---

# Ataki Evil Twin, KARMA i MANA

## Analiza, detekcja i przeciwdziałanie

<br>

**Bezpieczenstwo Sieci Bezprzewodowych**  
AGH WIEiT | 2026

---
layout: default
---

# Agenda

<div class="grid grid-cols-2 gap-4">

<div>

### Ataki
1. Czym jest Rogue AP?
2. **Evil Twin** — klonowanie SSID
3. **KARMA** — pasywne przechwytywanie
4. **MANA** — zaawansowany atak

### Detekcja
5. Metoda 1: Fingerprinting IE
6. Metoda 2: Analiza RSSI
7. Metoda 3: Sequence Numbers

</div>

<div>

### Eksperyment
8. 10 cykli ON/OFF — wyniki
9. Evil Twin vs KARMA — porownanie
10. **WiFiSlayer** — narzedzie zewnetrzne

### Wnioski
11. Mitygacja i ochrona
12. Podsumowanie

</div>

</div>

---
layout: two-cols
---

# Czym jest Rogue Access Point?

Nieautoryzowany punkt dostepowy podszywajacy sie pod legalna siec WiFi.

Standard **802.11 nie weryfikuje tozsamosci AP**. Klient nie widzi roznicy miedzy oryginalnym AP a atakujacym.

### Zagrozenia:
- Kradziez hasel (captive portal)
- Przechwycenie ruchu (MITM)
- Kradziez poswiadczen EAP

### Nasze srodowisko:
- **Kali Linux VM** + 2 karty TP-Link RT5572
- Oryginalny AP: SSID **601A** (BSSID: 7C:F1:7E:C1:7B:95)
- Ofiara: **iPhone** (BA:A1:0E:08:E0:35)

::right::

<br><br>

```
┌─────────────────┐     ┌─────────────────┐
│  Oryginalny AP  │     │   Evil Twin AP  │
│  7C:F1:7E:...   │     │  64:70:02:...   │
│  SSID: 601A     │     │  SSID: 601A     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
    ┌─────────────────────────────────┐
    │         iPhone                   │
    │   Nie widzi roznicy             │
    │   Wybiera silniejszy sygnal     │
    └─────────────────────────────────┘
```

---
layout: default
---

# Atak 1: Evil Twin

<div class="grid grid-cols-2 gap-4">

<div>

### Jak dziala:
1. Klonujemy SSID (601A)
2. Wysylamy ramki **deauth** do klientow
3. Klient traci polaczenie z oryginalem
4. Klient laczy sie z **naszym AP** (blizej = silniejszy sygnal)

### Nasze wyniki praktyczne:

| Metryka | Oryginal | Evil Twin |
|---|---|---|
| **BSSID** | 7C:F1:7E:C1:7B:95 | 64:70:02:18:B9:22 |
| **SSID** | 601A | 601A |
| **Beacony** | 3.882 | 2.928 |
| **RSSI** | -42.1 dBm | **-22.8 dBm** |
| **Vendor** | Microsoft WPS | **brak** (karta USB) |
| **HT Cap.** | LDPC, HT40, SGI | **brak** |

</div>

<div>

### Dowod: 2 BSSID z tym samym SSID

<img src="/wyniki/charts/evil_twin_comparison.png" style="width:100%; border:1px solid #ddd; margin-top:10px"/>

**Wniosek:** Dwa rozne urzadzenia nadaja ten sam SSID.  
<span class="highlight">Delta RSSI = 20.3 dBm</span> — nienaturalna roznica.

</div>

</div>

---
layout: two-cols
---

# Atak 2: KARMA

KARMA = **K**arma **A**ttacks **R**adio **M**achines **A**utomatically

### Jak dziala:
1. Rogue AP **nasluchuje** probe requestow
2. Kazdy klient wysyla zapytania o znane sieci
3. KARMA **odpowiada beaconem** z zadanym SSID
4. Klient widzi "swoja" siec i moze sie polaczyc

### Roznica od Evil Twin:

| Cecha | Evil Twin | KARMA |
|---|---|---|
| Deauth | **TAK** | NIE |
| Zna SSID? | **TAK** | NIE |
| BSSID:SSID | Wiele : 1 | **1 : wiele** |
| Wykrywanie | Duplikat SSID | 1 BSSID → wiele SSID |

::right::

### Nasze wyniki:

KARMA AP (hostapd-mana, enable_mana=0):  
BSSID **64:70:02:18:B9:22** przechwycil probe requesty iPhone'a:

```
Probe Request: SSID=601A, RSSI=-34 dBm
Probe Request: SSID=FreeWiFi, RSSI=-34 dBm
```

**Kluczowa anomalia:**  
Jeden BSSID nadaje 2 rozne SSID (601A + FreeWiFi). Normalny AP nadaje tylko swoj SSID.

<div class="highlight">

Detection signature:  
**1 BSSID → wiele SSID** (RSSI stale = jedno urzadzenie)

</div>

---
layout: two-cols
---

# Atak 3: MANA

MANA Toolkit (SensePost, Defcon 22) — ewolucja KARMY.

### Ulepszenia:
- Odpowiada na **directed probe requests** (ignoruje docelowy BSSID)
- **Loud Mode** — emituje popularne SSID co ~10s
- **EAP Capture** — przechwytuje handshake Enterprise
- **Multiple BSSID** — jeden interfejs, wiele wirtualnych AP

### Nasze wyniki:

MANA AP (hostapd-mana, enable_mana=1) przechwycil **directed probe requesty** iPhone'a:

```
MANA - Directed probe request
       for SSID '601A'
       from ba:a1:0e:08:e0:35
```

::right::

### Status eksperymentu:

| Element | Wynik |
|---|---|
| MANA AP uruchomiony | TAK |
| Directed probe przechwycony | TAK |
| Captive Portal iOS | **NIE** — Apple CNA zablokowal |
| Pelen atak MANA | **NIE** — ograniczenia sprzetowe |

<br>

<div style="background:#FFF3CD; padding:10px; border-radius:5px">

MANA to atak **pasywny** — nie wymusza rozlaczenia.  
Czeka az klient sam przejdzie do naszego AP.  
**Evil Twin** uzywa deauth do silowego przelaczenia.  
**KARMA** odpowiada na probe requesty bez deauth.

</div>

---
layout: default
---

# Metoda 1: Fingerprinting IE

<div class="grid grid-cols-2 gap-4">

<div>

### Co porownujemy?

Information Elements w ramkach Beacon — to "odcisk palca" sprzetu.

Kazdy producent implementuje standard 802.11 inaczej.  
Roznice w **Supported Rates**, **Vendor OUI**, **HT Capabilities**  
wskazuja na rozne urzadzenia.

### Nasze dane:

| IE | Oryginal AP | Evil Twin |
|---|---|---|
| Producent | Microsoft WPS | **brak** |
| HT Capabilities | LDPC, HT40, SGI20, SGI40 | **brak** |
| Ograniczenie mocy | 0 dB | **brak** |
| Szeroki kanal 40MHz | TAK | **NIE** |
| Dodatkowe funkcje | TAK | **NIE** |

</div>

<div>

### Wynik: 15 z 18 IE rozni sie

<img src="/wyniki/experiment/evil_twin_analysis.png" style="width:100%; border:1px solid #ddd"/>

<div class="highlight" style="font-size:1.2em; text-align:center; margin-top:10px">
Roznice w Vendor OUI i HT Capabilities = twardy dowod
</div>

<div style="font-size:0.85em; margin-top:10px">

**Interpretacja:** Oryginalny router (czerwony) ma wszystkie  
zaawansowane funkcje. Nasza prosta karta USB (zielony) nie ma zadnych.

To jednoznacznie wskazuje na **dwa rozne urzadzenia sprzetowe**.

</div>

</div>

</div>

---
layout: default
---

# Metoda 2: Analiza RSSI

<div class="grid grid-cols-2 gap-4">

<div>

### Co mierzymy?

Poziom sygnalu (RSSI) z naglowka Radiotap kazdej ramki Beacon.  
Im wyzsza wartosc (blizej 0), tym silniejszy sygnal.

### Nasze pomiary:

| AP | Sredni RSSI | Interpretacja |
|---|---|---|
| Evil Twin | **-22.8 dBm** | Karta USB na biurku |
| Oryginalny | **-42.1 dBm** | Router w innym pokoju |

<div class="highlight">

**Delta = 20.3 dBm**  
Roznica sygnalu ~100 razy wieksza

</div>

</div>

<div>

### Wizualizacja:

<br>
<img src="/wyniki/charts/evil_twin_comparison.png" style="width:100%; border:1px solid #ddd"/>

<br>

<div style="font-size:0.9em">

**Wniosek:** Dwa AP z tym samym SSID nie powinny miec tak roznego sygnalu.  
Jeden z nich jest **nienaturalnie blisko** — to karta atakujacego.

**Ograniczenie:** Atakujacy moze dostosowac moc nadawania.

**Zaleta:** Wykrycie nie wymaga dodatkowego sprzetu.

</div>

</div>

</div>

---
layout: default
---

# Metoda 3: Sequence Numbers

<div class="grid grid-cols-2 gap-4">

<div>

### Na czym polega?

Kazda karta Wi-Fi ma **12-bitowy sprzetowy licznik** (0-4095).  
Z kazda ramka Beacon numer rosnie o 1.  
Po osiagnieciu 4095 zawija sie do 0.

Jesli **dwa AP** nadaja ten sam SSID, kazdy ma **wlasny, niezalezny licznik**.  
Na wykresie widac **dwa osobne strumienie**.

### Nasze dane:

| AP | Zakres seq |
|---|---|
| Oryginalny | 0 – 4095 (pelny cykl) |
| Evil Twin | 0 – 2045 |

**Brak nakladania sie zakresow** = dwa rozne urzadzenia.

</div>

<div>

### Wykres: 10 cykli ON/OFF

<img src="/wyniki/experiment/evil_twin_analysis.png" style="width:100%; border:1px solid #ddd"/>

<div style="font-size:0.85em; margin-top:5px">

"Gorki" na zielonej linii = momenty wlaczania/wylaczania AP.  
Czerwona linia (oryginal) nadaje ciagle.  
**Wrap-around** co 4096 — naturalne zachowanie licznika 12-bit.

</div>

<div class="highlight" style="margin-top:10px">

Zaleta: licznik jest w hardware — nie da sie zmanipulowac.

</div>

</div>

</div>

---
layout: default
---

# Eksperyment: 10 cykli ON/OFF Evil Twin

<div class="grid grid-cols-2 gap-4">

<div>

### Przebieg:

1. iPhone polaczony z **Evil Twin** (64:70:02:18:B9:22)
2. **Wylaczenie** AP (`pkill hostapd`) — iPhone traci Wi-Fi na ~5s
3. **Wlaczenie** AP (`create_ap`) — iPhone reconnectuje w ~6s
4. Powtorzono **10 razy**

### Statystyki:

| Metryka | Wartosc |
|---|---|
| Pakiety | **55 490** |
| Beacony Evil Twin | 2 928 |
| Beacony Oryginal | 3 882 |
| Sukces reconnectu | **10/10** (100%) |
| Sredni czas reconnectu | ~6s |

</div>

<div>

### Co udowodnilismy:

1. iPhone **przechodzi** miedzy AP bez interwencji uzytkownika
2. Czas reconnectu ~6s — **niezauwazalny** dla ofiary
3. Sequence Numbers jednoznacznie potwierdzaja **2 urzadzenia**
4. **Kazde przelaczenie** zostalo zarejestrowane w pcap

<br>

<div style="background:#FFF3CD; padding:10px; border-radius:5px">

Wykres Seq Numbers z 10 cykli znajduje sie na poprzednim slajdzie.

</div>

</div>

</div>

---
layout: default
---

# Porownanie: Evil Twin vs KARMA

<div class="grid grid-cols-2 gap-4">

<div style="border:2px solid #D41920; padding:15px; border-radius:8px">

### Evil Twin

**Wiele BSSID → 1 SSID**

- Celuje w **konkretna** siec
- Uzywa **deauth** (silowe rozlaczenie)
- Wykrywalny przez **duplikat SSID**
- Potrzebuje **znac SSID** ofiary

**Nasze dane:**
- 2 BSSID z SSID "601A"
- RSSI: -22.8 vs -42.1 (delta 20.3 dBm)
- Rozne Vendor OUI

</div>

<div style="border:2px solid #2A9D8F; padding:15px; border-radius:8px">

### KARMA

**1 BSSID → wiele SSID**

- Lapie **wszystkie** probe requesty
- **Bez deauth** (pasywny)
- Wykrywalny przez **anomalie SSID**
- **Nie musi znac** SSID ofiary

**Nasze dane:**
- 1 BSSID z 2 roznymi SSID (601A + FreeWiFi)
- RSSI: stale (to samo urzadzenie)
- Przechwycone probe requesty iPhone'a

</div>

</div>

<div style="margin-top:20px; font-size:0.9em">

**Wniosek:** Evil Twin jest latwiejszy do wykrycia (jawny duplikat), ale skuteczniejszy w przelamywaniu konkretnej ofiary.  
KARMA jest trudniejsza do wykrycia (wyglada jak multi-SSID AP), ale mniej skuteczna na nowszych systemach (iOS/Android pasywne skanowanie).

</div>

---
layout: default
---

# WiFiSlayer — narzedzie pomocnicze

<div class="grid grid-cols-2 gap-4">

<div>

### Co to jest?

Framework do audytu sieci WiFi.  
https://github.com/waheeb71/WiFiSlayer

### Funkcjonalnosci:
- Evil Twin z **captive portalem**
- WPA/WPA2 Handshake capture
- PMKID attack
- Deauth / Beacon flooding
- Auto-Pwn (automatyczna sekwencja ataku)

### Nasze doswiadczenia:

| Funkcja | Wynik |
|---|---|
| Captive Portal | **DZIALA** |
| Haslo przechwycone | **TAK** (mama1234) |
| Strona logowania | Router Firmware Update |
| Lamanie WPA | NIE testowane |

</div>

<div>

### Dlaczego WiFiSlayer?

Wlasna implementacja captive portala nie zadzialala z iOS (Apple CNA). WiFiSlayer rozwiazal ten problem przez:

```
address=/#/192.168.1.1
```
w konfiguracji DNS — przekierowuje wszystkie zapytania na serwer captive portal.

### Zdjecie strony logowania:

<img src="/media/captive_portal_screen.png" style="width:100%; border:1px solid #ddd; margin-top:10px"/>

<div style="font-size:0.85em">

**Wniosek:** Zewnetrzne narzedzia moga skutecznie przeprowadzac ataki.  
Nasze wlasne skrypty sluza do **DETEKCJI** (analyze_pcap.py, beacon_diff.py).

</div>

</div>

</div>

---
layout: default
---

# Mitygacja — jak sie chronic?

<div class="grid grid-cols-2 gap-4">

<div style="background:#F5F5F5; padding:15px; border-radius:8px">

### Dla administratorow sieci:

**802.11w (PMF)** — Protected Management Frames  
Szyfruje ramki zarzadzania — blokuje ataki deauth.

**WIDS/WIPS** — systemy detekcji  
Monitoruja duplikaty SSID i anomalie RSSI.

**EAP-TLS** — certyfikaty dla AP  
Klient weryfikuje tozsamosc punktu dostepowego.

**Regularne skanowanie eteru**  
W poszukiwaniu nieznanych AP — dokladnie to, co robi nasz analyze_pcap.py.

</div>

<div style="background:#F5F5F5; padding:15px; border-radius:8px">

### Dla uzytkownikow:

**VPN** — szyfruje caly ruch  
Nawet na rogue AP dane sa bezpieczne.

**Unikanie otwartych sieci**  
Publiczne Wi-Fi to latwy cel.

**Wylaczenie auto-join**  
Nie lacz sie automatycznie z "znanymi" sieciami.

**DNS-over-HTTPS**  
Chroni przed podslychem zapytan DNS.

### Nasze narzedzia jako lekki WIDS:

`analyze_pcap.py` + `beacon_diff.py` moga sluzyc jako podstawowy system detekcji — open source, Python, MIT license.

</div>

</div>

---
layout: center
---

# Podsumowanie

<div class="grid grid-cols-3 gap-4" style="margin-top:30px">

<div style="text-align:center">
<div style="font-size:3em; color:#D41920; font-weight:bold">3</div>
<div>typy atakow<br>przeprowadzone</div>
<div style="font-size:0.8em; color:#666">Evil Twin · KARMA · MANA</div>
</div>

<div style="text-align:center">
<div style="font-size:3em; color:#2A9D8F; font-weight:bold">3</div>
<div>metody detekcji<br>zaimplementowane</div>
<div style="font-size:0.8em; color:#666">IE · RSSI · Seq Numbers</div>
</div>

<div style="text-align:center">
<div style="font-size:3em; color:#264653; font-weight:bold">55k+</div>
<div>pakietow<br>przechwyconych</div>
<div style="font-size:0.8em; color:#666">10 cykli ON/OFF</div>
</div>

</div>

<div style="margin-top:40px; line-height:2">

- Wszystkie ataki przeprowadzone i udokumentowane
- **Evil Twin** — najskuteczniejszy, najlatwiejszy do wykrycia
- **KARMA** — stealthowy, mniej skuteczny na nowych systemach
- **MANA** — najbardziej zaawansowany technicznie
- **3 metody detekcji** niezaleznie potwierdzaja obecnosc Evil Twin
- **WiFiSlayer** uzupelnia nasze narzedzia o captive portal

</div>

---
layout: center
---

# Dziekujemy za uwage

<br>

## Pytania?

<br>

github.com/Hose-Zur/BBSK-Evil-Twin

`analyze_pcap.py` · `beacon_diff.py` · `generate_report.py`
