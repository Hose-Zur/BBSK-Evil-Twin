---
theme: none
title: Ataki Evil Twin KARMA i MANA
transition: fade
class: text-center
fonts:
  sans: Calibri, Arial, Helvetica
---

<style>
:root {
  --agh-red: #D41920;
  --agh-dark: #1A1A2E;
  --agh-gray: #666666;
  --agh-light: #F5F5F5;
}
.slidev-layout { 
  padding: 2.5em 3em !important;
  font-family: Calibri, Arial, sans-serif;
}
h1 { 
  color: white !important; 
  font-size: 2.4em !important; 
  margin-bottom: 0 !important;
}
h2 { 
  color: var(--agh-dark) !important; 
  font-size: 1.6em !important;
  border: none !important;
  padding: 0 !important;
}
.slidev-layout h1 + p { margin-top: 0.5em; }
.agh-header {
  position: absolute; top: 0; left: 0; right: 0;
  height: 70px;
  background: var(--agh-red);
  display: flex; align-items: center; padding: 0 2em;
  color: white; font-weight: bold; font-size: 1.3em;
}
.agh-footer {
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 25px; font-size: 0.5em;
  color: #999; padding: 0 2.5em; line-height: 25px;
  border-top: 1px solid #eee;
}
.content-area { margin-top: 30px; }
.red { color: var(--agh-red); font-weight: bold; }
.gray { color: var(--agh-gray); font-size: 0.85em; }
table { border-collapse: collapse; width: 100%; font-size: 0.85em; }
td, th { padding: 6px 10px; border-bottom: 1px solid #ddd; }
th { background: var(--agh-red); color: white; font-weight: bold; }
tr:nth-child(even) { background: #f9f9f9; }
.box { background: var(--agh-light); border-radius: 6px; padding: 12px; margin: 8px 0; }
</style>

---
layout: center
---

<div style="position:absolute;top:0;left:0;right:0;height:60px;background:#D41920;display:flex;align-items:center;padding:0 2em">
  <span style="color:white;font-size:0.8em">AGH — Bezpieczenstwo Sieci Bezprzewodowych</span>
</div>

<br><br><br><br>

# Ataki Evil Twin, KARMA i MANA

<div style="margin-top:0.5em;font-size:1.1em;color:#666">
Analiza, detekcja i przeciwdzialanie atakom Rogue Access Point
</div>

<br><br>

<div style="font-size:0.9em;color:#666;line-height:2">
  AGH WIEiT · 2026
</div>

---
layout: default
---

<div class="agh-header">Agenda</div>
<div class="content-area">

<div style="display:flex;gap:3em;margin-top:1em">

<div style="flex:1">

**1. Wprowadzenie**  
Czym jest Rogue AP, zagrozenia, cel projektu

**2. Ataki**  
Evil Twin · KARMA · MANA

**3. Detekcja**  
Fingerprinting IE · Analiza RSSI · Sequence Numbers

</div>

<div style="flex:1">

**4. Eksperyment**  
10 cykli ON/OFF Evil Twin — wyniki

**5. Porownanie**  
Evil Twin vs KARMA — dane i roznice

**6. Narzedzia**  
WiFiSlayer · analyze_pcap.py · beacon_diff.py

**7. Wnioski**  
Mitygacja i podsumowanie

</div>

</div>



---
layout: default
---

<div class="agh-header">Czym jest Rogue Access Point?</div>
<div class="content-area">

<div style="display:flex;gap:2em">

<div style="flex:1">

**Definicja**  
Nieautoryzowany punkt dostepowy podszywajacy sie pod legalna siec WiFi. Standard 802.11 nie weryfikuje tozsamosci AP.

**Zagrozenia**  
- Kradziez hasel przez captive portal
- Przechwycenie ruchu (MITM)
- Kradziez poswiadczen EAP

**Nasze srodowisko**  
- Kali Linux VM + 2x TP-Link RT5572 (Ralink)
- AP ofiary: 601A (BSSID: 7C:F1:7E:C1:7B:95)
- Ofiara: iPhone (BA:A1:0E:08:E0:35)
- Narzedzia: create_ap, hostapd-mana, aireplay-ng, tcpdump

</div>

<div style="flex:1;display:flex;align-items:center;justify-content:center">

<div style="background:var(--agh-light);border-radius:8px;padding:20px;font-family:monospace;font-size:0.8em;line-height:1.5;width:100%">

<span style="color:var(--agh-red)">AP ofiary</span><br>
SSID: 601A  | BSSID: 7C:F1:7E:C1:7B:95<br>
RSSI: -42.1 dBm (oddalony router)<br><br>

<span style="color:#2A9D8F">Nasz Evil Twin</span><br>
SSID: 601A  |  BSSID: 64:70:02:18:B9:22<br>
RSSI: -22.8 dBm (karta obok ofiary)<br><br>

<span style="color:#D41920">Delta RSSI: 20.3 dBm</span>

</div>

</div>

</div>



---
layout: default
---

<div class="agh-header">Atak 1: Evil Twin</div>
<div class="content-area">

<div style="display:flex;gap:2em">

<div style="flex:1">

**Mechanizm**  
1. Klonujemy SSID ofiary (601A)  
2. Wysylamy deauth (aireplay-ng) do klientow  
3. Klient traci polaczenie z oryginalem  
4. Klient laczy sie z naszym AP (silniejszy sygnal)  
5. Captive portal przechwytuje haslo

**Nasze wyniki**  

| Parametr | Oryginalny AP | Evil Twin |
|---|---|---|
| BSSID | 7C:F1:7E:C1:7B:95 | 64:70:02:18:B9:22 |
| Beacony | 3882 | 2928 |
| RSSI | -42.1 dBm | -22.8 dBm |
| Vendor | Microsoft WPS | brak |
| HT Cap. | LDPC, HT40, SGI | brak |

</div>

<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center">

<img src="/evil_twin_detection.png" style="width:100%;max-width:550px;border:1px solid #ddd;border-radius:4px"/>

<div style="font-size:0.85em;margin-top:8px">

**Dowod**: Dwa rozne BSSID nadaja ten sam SSID "601A".  
Rozny vendor OUI + inny poziom sygnalu = <span class="red">Evil Twin potwierdzony</span>

</div>

</div>

</div>



---
layout: default
---

<div class="agh-header">Atak 2: KARMA</div>
<div class="content-area">

<div style="display:flex;gap:2em">

<div style="flex:1">

**Karma Attacks Radio Machines Automatically**

**Mechanizm**  
1. AP nasluchuje probe requestow od klientow  
2. iPhone wysyla zapytania o znane sieci  
3. KARMA odpowiada beaconem z zadanym SSID  
4. Klient widzi "swoja" siec i moze sie polaczyc

**Kluczowa roznica od Evil Twin**  

| Cecha | Evil Twin | KARMA |
|---|---|---|
| Deauth | TAK | NIE |
| Zna SSID ofiary? | TAK | NIE |
| BSSID:SSID | Wiele : 1 | **1 : wiele** |

</div>

<div style="flex:1">

**Nasze wyniki**

Hostapd-mana (enable_mana=0) przechwycil probe requesty:

```
Probe Request: SSID=601A (RSSI -34 dBm)
    from ba:a1:0e:08:e0:35
```

<div class="box">

**KARMA wykrywanie**  
Normalny AP nadaje 1 SSID.  
KARMA nadaje wiele SSID z 1 BSSID → **anomalia**.  
RSSI stale (to samo urzadzenie fizyczne).

</div>

<img src="/karma_detection.png" style="width:100%;max-width:500px;border:1px solid #ddd;border-radius:4px"/>

</div>

</div>



---
layout: default
---

<div class="agh-header">Atak 3: MANA (SensePost, Defcon 22)</div>
<div class="content-area">

<div style="display:flex;gap:2em">

<div style="flex:1">

**Ulepszenia KARMY**  
- Odpowiada na **directed probe requests** (ignoruje docelowy BSSID)  
- **Loud Mode** — emituje popularne SSID co ~10s  
- **EAP Capture** — przechwytuje handshake Enterprise  
- **Multiple BSSID** — jeden interfejs, wiele AP

**Nasze wyniki**  

Hostapd-mana (enable_mana=1):

<div style="background:var(--agh-light);border-radius:4px;padding:10px;font-family:monospace;font-size:0.85em">
MANA - Directed probe request<br>
&nbsp;&nbsp;&nbsp;&nbsp;for SSID '601A'<br>
&nbsp;&nbsp;&nbsp;&nbsp;from ba:a1:0e:08:e0:35
</div>

</div>

<div style="flex:1">

<div class="box">

**Status**  

| Element | Wynik |
|---|---|
| MANA AP uruchomiony | TAK |
| Directed probe przechwycony | TAK |
| Captive Portal iOS | NIE (Apple CNA) |
| Pelen atak | NIE (ograniczenia) |

**Uwaga**  
MANA to atak pasywny — nie wymusza rozlaczenia.  
Klient sam decyduje czy przejsc do naszego AP.  
Razem z deauth z Evil Twin stanowilby kompletny atak.

</div>

</div>

</div>



---
layout: default
---

<div class="agh-header">Trzy metody detekcji</div>
<div class="content-area">

<div style="display:flex;gap:1.5em">

<div class="box" style="flex:1;border-left:4px solid #D41920">

**Metoda 1: Fingerprinting IE**  
Porownanie Information Elements w ramkach Beacon.  
Kazdy AP ma unikalna konfiguracje IE.  

**Wynik: 15 z 18 IE rozni sie**  
- Oryginal: Microsoft WPS, HT Capabilities (LDPC, HT40)  
- Evil Twin: brak wszystkich  

To **twardy dowod** sprzetowy.

</div>

<div class="box" style="flex:1;border-left:4px solid #2A9D8F">

**Metoda 2: Analiza RSSI**  
Porownanie poziomu sygnalu z naglowka Radiotap.  

**Wynik: Delta 20.3 dBm**  
- Evil Twin: -22.8 dBm (obok ofiary)  
- Oryginal: -42.1 dBm (oddalony)  

Anomalia = atakujacy jest blisko.

</div>

<div class="box" style="flex:1;border-left:4px solid #264653">

**Metoda 3: Sequence Numbers**  
Sledzenie 12-bitowego licznika ramek.  
Kazde urzadzenie ma wlasny licznik.  

**Wynik: 2 niezalezne strumienie**  
- Oryginal: 0-4095 (pelny cykl)  
- Evil Twin: 0-2045  

Brak nakladania = dwa urzadzenia.

</div>

</div>

<div style="text-align:center;margin-top:15px;font-size:1.1em">
<span class="red">Wszystkie 3 metody zgodnie potwierdzaja: EVIL TWIN DETECTED</span>
</div>



---
layout: default
---

<div class="agh-header">Eksperyment: 10 cykli ON/OFF Evil Twin</div>
<div class="content-area">

<div style="display:flex;gap:2em">

<div style="flex:1">

**Przebieg**  
1. iPhone na Evil Twin (64:70:02:18:B9:22)  
2. Wylaczenie AP (`pkill hostapd`) → iPhone traci Wi-Fi (~5s)  
3. Wlaczenie AP (`create_ap`) → iPhone reconnectuje (~6s)  
4. Powtorzono 10 razy

**Statystyki**  

| Metryka | Wartosc |
|---|---|
| Pakiety lacznie | 55 490 |
| Beacony Evil Twin | 2 928 |
| Beacony Oryginal | 3 882 |
| Sukces reconnectu | **10/10 (100%)** |
| Sredni czas | ~6 sekund |

**Wniosek**  
iPhone przechodzi miedzy AP automatycznie, bez wiedzy uzytkownika. Czas ~6s jest niezauwazalny.

</div>

<div style="flex:1;display:flex;flex-direction:column;align-items:center">

<img src="/evil_twin_detection.png" style="width:100%;max-width:450px;border:1px solid #ddd;border-radius:4px"/>

<div style="font-size:0.85em;margin-top:8px">

Wykres: liczba beaconow i RSSI dla obu AP — 2 urzadzenia nadajace ten sam SSID.

</div>

</div>

</div>



---
layout: default
---

<div class="agh-header">Porownanie: Evil Twin vs KARMA</div>
<div class="content-area">

<div style="display:flex;gap:2em;margin-bottom:15px">

<div style="flex:1;border:2px solid #D41920;border-radius:8px;padding:12px">

### <span style="color:#D41920">Evil Twin</span>

**Wiele BSSID → 1 SSID**  

- Celuje w konkretna, znana siec  
- Uzywa deauth (silowe rozlaczenie)  
- Wykrywalny przez duplikat SSID  
- Wymaga znajomosci SSID ofiary  
- <span class="red">LATWIEJSZY DO WYKRYCIA</span>

</div>

<div style="flex:1;border:2px solid #2A9D8F;border-radius:8px;padding:12px">

### <span style="color:#2A9D8F">KARMA</span>

**1 BSSID → wiele SSID**  

- Lapie wszystkie probe requesty  
- Bez deauth (pasywny)  
- Wykrywalny przez anomalie SSID  
- Nie musi znac SSID ofiary  
- <span style="color:#2A9D8F;font-weight:bold">STEALTHOWY</span>

</div>

</div>

<table>
<tr><th>Cecha</th><th>Evil Twin (nasze dane)</th><th>KARMA (nasze dane)</th></tr>
<tr><td>BSSID pattern</td><td>2 BSSID → 1 SSID (601A)</td><td>1 BSSID → 2+ SSID</td></tr>
<tr><td>RSSI</td><td>Delta = 20.3 dBm (anomalia)</td><td>Stale (jedno urzadzenie)</td></tr>
<tr><td>Vendor OUI</td><td>Rozny (MS vs brak)</td><td>Ten sam</td></tr>
<tr><td>Deauth w eterze</td><td>TAK — widoczny atak</td><td>NIE — brak sladu</td></tr>
<tr><td>Skutecznosc</td><td>WYSOKA — celowany</td><td>SREDNIA — iOS pasywny scan</td></tr>
<tr><td>Wykrycie</td><td>LATWE — jawny duplikat</td><td>TRUDNIEJSZE — anomalia SSID</td></tr>
</table>



---
layout: default
---

<div class="agh-header">WiFiSlayer — narzedzie zewnetrzne</div>
<div class="content-area">

<div style="display:flex;gap:2em">

<div style="flex:1">

**Czym jest?**  
Framework do audytu WiFi (github.com/waheeb71/WiFiSlayer).  
Zintegrowane: Evil Twin, handshake capture, PMKID, WPS, deauth.

**Dlaczego go uzyliśmy?**  
Nasza wlasna implementacja captive portala nie dzialala z iOS (CNA detection). WiFiSlayer rozwiazal to przez DNS redirect w dnsmasq:

<div style="background:var(--agh-light);border-radius:4px;padding:8px;font-family:monospace;font-size:0.85em;margin:8px 0">
address=/#/192.168.1.1
</div>

Przekierowuje wszystkie zapytania DNS na serwer captive portal.

</div>

<div style="flex:1">

**Nasze testy**  

| Funkcja | Wynik |
|---|---|
| Captive Portal uruchomiony | TAK |
| Strona logowania wyswietlona | TAK |
| Haslo przechwycone | **TAK (mama1234)** |
| Lamanie WPA | NIE testowane |

<div class="box">

**Wniosek**  
WiFiSlayer = narzedzie **ofensywne** (do ataku).  
Nasze narzedzia (`analyze_pcap.py`, `beacon_diff.py`) = **defensywne** (do detekcji).  
Razem stanowia kompletny zestaw narzedzi.

</div>

</div>

</div>



---
layout: default
---

<div class="agh-header">Mitygacja — jak sie chronic?</div>
<div class="content-area">

<div style="display:flex;gap:2em">

<div style="flex:1;background:#F5F5F5;border-radius:8px;padding:15px">

**Dla administratorow sieci**  

**802.11w (PMF)** — Protected Management Frames  
Szyfruje ramki zarzadzania → blokuje deauth.  

**WIDS/WIPS** — systemy detekcji  
Monitoruja duplikaty SSID i anomalie RSSI.  

**EAP-TLS** — certyfikaty dla AP  
Klient weryfikuje tozsamosc punktu dostepowego.  

**Regularne skanowanie eteru**  
Tak jak nasz analyze_pcap.py — wykrywa nieznane AP.

</div>

<div style="flex:1;background:#F5F5F5;border-radius:8px;padding:15px">

**Dla uzytkownikow**  

**VPN** — szyfruje caly ruch  
Nawet na rogue AP dane sa bezpieczne.  

**Unikanie otwartych sieci WiFi**  
Publiczne sieci to latwy cel dla atakujacych.  

**Wylaczenie auto-join**  
Nie lacz sie automatycznie z zapisanymi sieciami.  

**DNS-over-HTTPS**  
Chroni przed podslychem zapytan DNS.

</div>

</div>

<div class="box" style="text-align:center">

<span class="red">Nasze narzedzia jako lekki WIDS:</span>  
`analyze_pcap.py` + `beacon_diff.py` — open source, Python, MIT license  
github.com/Hose-Zur/BBSK-Evil-Twin

</div>



---
layout: center
---

<div style="position:absolute;top:0;left:0;right:0;height:60px;background:#D41920;display:flex;align-items:center;padding:0 2em">
  <span style="color:white;font-size:0.8em">AGH — Podsumowanie</span>
</div>

<br><br>

# Podsumowanie

<div style="display:flex;gap:3em;margin:2em 0;justify-content:center">

<div style="text-align:center">
<div style="font-size:2.5em;color:#D41920;font-weight:bold">3</div>
<div style="font-size:0.9em">typy atakow<br>przeprowadzone</div>
<div style="font-size:0.75em;color:#666">Evil Twin · KARMA · MANA</div>
</div>

<div style="text-align:center">
<div style="font-size:2.5em;color:#2A9D8F;font-weight:bold">3</div>
<div style="font-size:0.9em">metody detekcji<br>zaimplementowane</div>
<div style="font-size:0.75em;color:#666">IE · RSSI · Seq Numbers</div>
</div>

<div style="text-align:center">
<div style="font-size:2.5em;color:#264653;font-weight:bold">55k+</div>
<div style="font-size:0.9em">pakietow<br>przechwyconych</div>
<div style="font-size:0.75em;color:#666">10 cykli ON/OFF</div>
</div>

</div>

<div style="line-height:2;max-width:600px;margin:0 auto">

- Wszystkie ataki przeprowadzone i udokumentowane  
- 3 metody detekcji niezaleznie potwierdzaja Evil Twin  
- Evil Twin — najskuteczniejszy i najlatwiejszy do wykrycia  
- KARMA — stealthowa, ale slabsza na nowych systemach  
- WiFiSlayer uzupelnia zestaw o captive portal  
- Wlasne narzedzia: analyze_pcap.py, beacon_diff.py

</div>

<br>

<div style="font-size:1em;color:#D41920;font-weight:bold">Dziekujemy za uwage</div>
<div style="font-size:0.8em;color:#666">github.com/Hose-Zur/BBSK-Evil-Twin</div>
