---
theme: seriph
title: 'Evil Twin, KARMA & MANA — Ataki i Detekcja'
titleTemplate: '%s'
info: 'Bezpieczeństwo bezprzewodowych sieci komputerowych | AGH WIEiT 2025/2026'
colorSchema: dark
fonts:
  sans: Inter
  mono: JetBrains Mono
transition: slide-left
drawings:
  enabled: false
mermaid:
  theme: dark
layout: cover
class: text-center
---

<div style="position:absolute; top:2rem; right:2rem; background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.2); border-radius:8px; padding:0.4em 1em; font-size:0.75em; color:rgba(0,212,255,0.8);">
  AGH WIEiT | 2025/2026
</div>

# Evil Twin, KARMA & MANA

<p style="font-size:1.2em; color:rgba(255,255,255,0.7); margin-top:0.5em;">
  Analiza ataków Rogue AP — metody detekcji i przeciwdziałanie
</p>

<div style="margin-top:3em; font-size:0.85em; color:rgba(255,255,255,0.45);">
  <span style="font-family:'JetBrains Mono',monospace; color:rgba(255,255,255,0.7);">Piotr Straszak</span>
  &nbsp;·&nbsp;
  <span style="font-family:'JetBrains Mono',monospace; color:rgba(255,255,255,0.7);">Hubert Czernicki</span>
  <br><br>
  Bezpieczeństwo bezprzewodowych sieci komputerowych
</div>

---

## Agenda

<div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:1em; margin-top:0.5em;">
<div v-click class="glass" style="border-left: 3px solid #ff3e3e;">
  <div style="display:flex; align-items:center; gap:0.8em;">
    <span style="font-size:1.8em; font-weight:700; color:#ff3e3e; font-family:'JetBrains Mono',monospace;">01</span>
    <div>
      <div style="font-weight:600;">Trzy typy ataków</div>
      <div style="font-size:0.8em; color:rgba(255,255,255,0.55);">Evil Twin → KARMA → MANA</div>
    </div>
  </div>
</div>
<div v-click class="glass" style="border-left: 3px solid #00d4ff;">
  <div style="display:flex; align-items:center; gap:0.8em;">
    <span style="font-size:1.8em; font-weight:700; color:#00d4ff; font-family:'JetBrains Mono',monospace;">02</span>
    <div>
      <div style="font-weight:600;">Trzy metody detekcji</div>
      <div style="font-size:0.8em; color:rgba(255,255,255,0.55);">IE Fingerprinting · RSSI · Seq Numbers</div>
    </div>
  </div>
</div>
<div v-click class="glass" style="border-left: 3px solid #00ff88;">
  <div style="display:flex; align-items:center; gap:0.8em;">
    <span style="font-size:1.8em; font-weight:700; color:#00ff88; font-family:'JetBrains Mono',monospace;">03</span>
    <div>
      <div style="font-weight:600;">Eksperymenty praktyczne</div>
      <div style="font-size:0.8em; color:rgba(255,255,255,0.55);">55 490 pakietów · 10 cykli ON/OFF</div>
    </div>
  </div>
</div>
<div v-click class="glass" style="border-left: 3px solid #a855f7;">
  <div style="display:flex; align-items:center; gap:0.8em;">
    <span style="font-size:1.8em; font-weight:700; color:#a855f7; font-family:'JetBrains Mono',monospace;">04</span>
    <div>
      <div style="font-weight:600;">Mitygacja i wnioski</div>
      <div style="font-size:0.8em; color:rgba(255,255,255,0.55);">802.11w · WIDS · VPN · EAP-TLS</div>
    </div>
  </div>
</div>
</div>

---

## Czym jest Rogue Access Point?

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em; align-items: start;">
<div>

<v-clicks>

- Nieautoryzowany AP podszywający się pod legalną sieć
- **Standard 802.11 nie weryfikuje tożsamości** AP
- Klient nie widzi różnicy między prawdziwym a fałszywym AP
- Konsekwencje: kradzież haseł, MITM, przechwycenie EAP

</v-clicks>

<div v-click class="glass" style="margin-top:1.5em; border-left: 3px solid #ff3e3e;">
  <div style="font-size:0.85em;">
    <strong style="color:#ff3e3e;">Zagrożenie:</strong> Captive portal, przechwycenie ruchu, atak na WPA2-Enterprise
  </div>
</div>
</div>
<div>

<div style="text-align: center; margin: 0 auto;">
  <img src="/diag1.svg" alt="Schemat sieci" style="max-height: 250px; display: inline-block; background: transparent;" />
</div>

</div>
</div>

---

## Atak Evil Twin

<div class="grid grid-cols-[1.2fr_1fr] gap-8">
<div>

<img src="/diag2.svg" alt="Evil Twin Sequence" class="w-full bg-transparent" />

</div>
<div>
<div v-click class="glass mb-4">
  <div class="text-sm">
    <span class="badge badge-red">Mechanizm</span>
    <div class="mt-2">
      <strong>1.</strong> Klonowanie SSID ofiary<br>
      <strong>2.</strong> Deauth → rozłączenie klienta<br>
      <strong>3.</strong> Silniejszy sygnał → auto-reconnect<br>
      <strong>4.</strong> Cały ruch przez atakującego
    </div>
  </div>
</div>
<div v-click class="glass">
  <div class="text-sm">
    <span class="badge badge-cyan">Sygnatura w eterze</span>
    <div class="mt-2 font-mono text-sm">
      2 BSSIDs → 1 SSID<br>
      Delta RSSI = <span class="text-red-500 font-bold">20.3 dBm</span><br>
      Różne Vendor OUI
    </div>
  </div>
</div>
</div>
</div>

---

## Atak KARMA

<div class="grid grid-cols-[1.2fr_1fr] gap-8">
<div>

<img src="/diag3.svg" alt="KARMA Sequence" class="w-full bg-transparent" />

</div>
<div>
<div v-click class="glass mb-4">
  <div class="text-sm">
    <span class="badge badge-orange">Kluczowe cechy</span>
    <div class="mt-2">
      + Nie trzeba znać SSID z góry<br>
      + Łapie <strong>każdego</strong> klienta w zasięgu<br>
      + Brak deauth — atak pasywny<br>
      – iOS 10+ — skanowanie pasywne
    </div>
  </div>
</div>
<div v-click class="glass">
  <div class="text-sm">
    <span class="badge badge-cyan">Sygnatura w eterze</span>
    <div class="mt-2 font-mono text-sm">
      1 BSSID → <span class="text-orange-400 font-bold">wiele SSIDs</span><br>
      RSSI = stałe (jedno urządzenie)<br>
      Brak ramek deauth
    </div>
  </div>
</div>
</div>
</div>

---

## Atak MANA <span style="font-size:0.5em; color:rgba(255,255,255,0.55);">SensePost · Defcon 22</span>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em; margin-top: 0.5em;">
<div>
<div class="glass" style="margin-bottom:1em;">
  <span class="badge badge-purple">Ulepszenia względem KARMA</span>
  <div style="margin-top:0.8em; font-size:0.9em;">

<v-clicks>

- **Directed Probe Response** — ignoruje docelowy BSSID
- **Loud Mode** — emituje 20+ popularnych SSIDs co ~10s
- **Multiple BSSID** — wirtualne AP z jednego interfejsu
- **EAP Capture** — przechwytuje handshake Enterprise

</v-clicks>

  </div>
</div>
</div>
<div>
<div v-click class="glass" style="margin-bottom:1em;">
  <span class="badge badge-green">Narzędzie</span>
  <div style="margin-top:0.6em;">

```bash
sudo apt install hostapd-mana
hostapd-mana /etc/mana.conf
```

  </div>
</div>
<div v-click class="glass">
  <span class="badge badge-red">Skuteczność vs KARMA</span>
  <div style="margin-top:0.6em; font-size:0.85em;">
    MANA odpowiada nawet gdy klient pyta <strong>konkretny BSSID</strong>
    — obchodzi zabezpieczenia iOS/Android
  </div>
</div>
</div>
</div>

---

## Porównanie trzech ataków

<div style="margin-top: 0.5em;">

|  | <span style="color:#ff3e3e;">Evil Twin</span> | <span style="color:#ffaa00;">KARMA</span> | <span style="color:#a855f7;">MANA</span> |
|---|---|---|---|
| **Cel** | 1 konkretny SSID | Wszystkie probe requesty | Wszystkie + Loud Mode |
| **Deauth** | Tak (widoczny) | Nie (stealth) | Nie (stealth) |
| **BSSID:SSID** | Wiele → 1 | 1 → wiele | 1 → wiele |
| **Zna SSID?** | Tak — musi znać | Nie — nasłuchuje | Nie + aktywne rozgłaszanie |
| **Wykrycie** | Łatwe (duplikat) | Średnie (anomalia SSID) | Średnie (loud beacony) |
| **Skuteczność** | Wysoka | Średnia | Wysoka |

</div>

<div v-click style="display:flex; gap:2em; margin-top:1.5em; justify-content:center;">
  <div class="glass" style="text-align:center; flex:1; border-top: 3px solid #ff3e3e;">
    <div style="font-weight:600; color:#ff3e3e;">Evil Twin</div>
    <div style="font-size:0.8em; color:rgba(255,255,255,0.55); margin-top:0.3em;">Klonowanie KONKRETNEJ sieci</div>
  </div>
  <div style="display:flex; align-items:center; font-size:1.5em; color:rgba(255,255,255,0.55);">vs</div>
  <div class="glass" style="text-align:center; flex:1; border-top: 3px solid #ffaa00;">
    <div style="font-weight:600; color:#ffaa00;">KARMA / MANA</div>
    <div style="font-size:0.8em; color:rgba(255,255,255,0.55); margin-top:0.3em;">Łapanie KAŻDEGO klienta</div>
  </div>
</div>

---

## Środowisko laboratoryjne

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em; margin-top: 0.5em;">
<div>
  <div class="glass" style="margin-bottom:1em;">
    <span class="badge badge-cyan">Sprzęt</span>
    <div style="margin-top:0.8em; font-size:0.85em;">

| Element | Specyfikacja |
|---|---|
| System | Kali Linux ARM64, VMware |
| Karty Wi-Fi | 2x TP-Link TL-WDN3200 |
| Chipset | Ralink RT5572 |
| AP ofiary | SSID: **601A** |
| Ofiara | iPhone |

  </div>
  </div>
</div>
<div>
  <div class="glass" style="margin-bottom:1em;">
    <span class="badge badge-green">Narzędzia ofensywne</span>
    <div style="margin-top:0.8em; font-size:0.85em;">
      <code>airgeddon</code> — Evil Twin + Captive Portal<br>
      <code>hostapd-mana</code> — KARMA i MANA<br>
      <code>WiFiSlayer</code> — Evil Twin framework<br>
      <code>airodump-ng</code> — przechwytywanie
    </div>
  </div>
  <div class="glass">
    <span class="badge badge-purple">Narzędzia defensywne (nasze)</span>
    <div style="margin-top:0.8em; font-size:0.85em;">
      <code>analyze_pcap.py</code> — auto-detekcja<br>
      <code>beacon_diff.py</code> — porównanie IE<br>
      <code>Wireshark</code> — weryfikacja ręczna
    </div>
  </div>
</div>
</div>

---

## Metoda 1 — Fingerprinting IE

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>
<div style="font-size:0.85em; margin-bottom:0.6em;">
  Każdy AP ma unikalne <strong>Information Elements</strong> w ramce Beacon —
  jak odcisk palca sprzętu.
</div>
<div style="padding:0.8em; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.08); border-radius:12px;">
  <div style="font-size:0.72em; color:rgba(255,255,255,0.55); margin-bottom:0.4em;">Liczba typów IE w ramkach Beacon</div>
  <!-- fixed 100px chart area: value label + bar + axis label all inside -->
  <div style="height:100px; position:relative; border-bottom:1px solid rgba(255,255,255,0.12); margin-bottom:0.4em;">
    <!-- Evil Twin bar: 8/18 = 44% of 72px usable -->
    <div style="position:absolute; bottom:0; left:25%; transform:translateX(-50%); text-align:center; width:60px;">
      <div style="font-family:'JetBrains Mono',monospace; font-weight:600; color:#ff3e3e; font-size:0.78em; line-height:1.2;">8</div>
      <div style="width:52px; height:32px; margin:2px auto 0; background:linear-gradient(to top, rgba(255,62,62,0.15), #ff3e3e); border-radius:4px 4px 0 0;"></div>
    </div>
    <!-- Original AP bar: 18/18 = 100% of 72px -->
    <div style="position:absolute; bottom:0; left:75%; transform:translateX(-50%); text-align:center; width:60px;">
      <div style="font-family:'JetBrains Mono',monospace; font-weight:600; color:#00d4ff; font-size:0.78em; line-height:1.2;">18</div>
      <div style="width:52px; height:72px; margin:2px auto 0; background:linear-gradient(to top, rgba(0,212,255,0.15), #00d4ff); border-radius:4px 4px 0 0;"></div>
    </div>
  </div>
  <div style="display:flex; justify-content:space-around; font-size:0.68em; color:rgba(255,255,255,0.5);">
    <span>Evil Twin</span>
    <span>Oryginalny AP</span>
  </div>
</div>
</div>
<div>
<div class="glass" style="margin-bottom:1em;">
  <span class="badge badge-red">Brakujące w Evil Twin</span>
  <div style="margin-top:0.6em; font-size:0.8em; font-family:'JetBrains Mono',monospace;">

<v-clicks>

- HT Capabilities (LDPC, SGI, STBC)
- VHT Capabilities
- Power Constraint
- BSS Load
- AP Channel Report
- HT/VHT Operation
- Vendor Specific (Microsoft WPS)

</v-clicks>

  </div>
</div>
<div v-click class="glass">
  <div style="font-size:0.85em;">
    <strong style="color:#00ff88;">Wynik:</strong> 14 z 17 IE się <strong>różni</strong><br>
    Różny OUI vendora = <strong style="color:#ff3e3e;">różne urządzenie</strong>
  </div>
</div>
</div>
</div>

---

## Metoda 2 — Analiza RSSI

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>
<div style="font-size:0.85em; margin-bottom:0.6em;">
  RSSI (Received Signal Strength Indicator) — atakujący zwykle umieszcza
  kartę <strong>blisko ofiary</strong>, dając nienaturalnie silny sygnał.
</div>
<div style="padding:0.8em; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.08); border-radius:12px;">
  <div style="font-size:0.72em; color:rgba(255,255,255,0.55); margin-bottom:0.4em;">Średni RSSI [dBm] — bliżej 0 = silniejszy</div>
  <!-- fixed 110px chart area, absolute positioned bars -->
  <div style="height:110px; position:relative; border-bottom:1px solid rgba(255,255,255,0.12); margin-bottom:0.4em;">
    <!-- Evil Twin: -22.8 → silniejszy → wyższy słupek 82px -->
    <div style="position:absolute; bottom:0; left:25%; transform:translateX(-50%); text-align:center; width:70px;">
      <div style="font-family:'JetBrains Mono',monospace; font-weight:600; color:#ff3e3e; font-size:0.75em; line-height:1.2;">-22.8 dBm</div>
      <div style="width:52px; height:82px; margin:2px auto 0; background:linear-gradient(to top, rgba(255,62,62,0.15), #ff3e3e); border-radius:4px 4px 0 0;"></div>
    </div>
    <!-- Original AP: -42.1 → słabszy → niższy słupek 36px -->
    <div style="position:absolute; bottom:0; left:75%; transform:translateX(-50%); text-align:center; width:70px;">
      <div style="font-family:'JetBrains Mono',monospace; font-weight:600; color:#00d4ff; font-size:0.75em; line-height:1.2;">-42.1 dBm</div>
      <div style="width:52px; height:36px; margin:2px auto 0; background:linear-gradient(to top, rgba(0,212,255,0.15), #00d4ff); border-radius:4px 4px 0 0;"></div>
    </div>
  </div>
  <div style="display:flex; justify-content:space-around; font-size:0.68em; color:rgba(255,255,255,0.5);">
    <span>Evil Twin</span>
    <span>Oryginalny AP</span>
  </div>
</div>
</div>
<div>
<div v-click class="verdict" style="margin-bottom:1em;">
  <div class="text">Delta RSSI = 19.2 dBm</div>
  <div style="font-size:0.8em; color:rgba(255,255,255,0.55); margin-top:0.3em;">Próg anomalii: > 15 dBm</div>
</div>
<div v-click class="glass" style="margin-bottom:0.8em;">
  <div style="font-size:0.85em;">
    <span class="badge badge-cyan">Wyniki z 6 eksperymentów</span>
    <div style="margin-top:0.6em; font-family:'JetBrains Mono',monospace; font-size:0.85em;">
      Delta min: <strong>18.6 dBm</strong><br>
      Delta max: <strong>20.3 dBm</strong><br>
      Delta avg: <strong>19.5 dBm</strong>
    </div>
  </div>
</div>
<div v-click class="glass">
  <div style="font-size:0.8em; color:rgba(255,255,255,0.55);">
    Ograniczenie: doświadczony atakujący może dostosować moc nadawania (txpower)
  </div>
</div>
</div>
</div>

---

## Metoda 3 — Sequence Numbers

<div style="display: grid; grid-template-columns: 1.3fr 1fr; gap: 2em;">
<div>
<div style="font-size:0.85em; margin-bottom:0.6em;">
  Każda karta Wi-Fi ma <strong>12-bitowy sprzętowy licznik</strong> (0–4095).
  Dwa urządzenia = dwa niezależne strumienie.
</div>
<div style="padding:0.8em; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
  <div style="font-size:0.72em; color:rgba(255,255,255,0.6); margin-bottom:0.4em; font-weight:500;">Sequence Number w czasie — wykres piłokształtny</div>
  <div style="display:flex; align-items:stretch; gap:0;">
    <div style="width:36px; position:relative; flex-shrink:0;">
      <span style="position:absolute; top:0; right:3px; font-size:0.6em; color:rgba(255,255,255,0.5); font-family:monospace; line-height:1;">4095</span>
      <span style="position:absolute; top:50%; right:3px; transform:translateY(-50%); font-size:0.6em; color:rgba(255,255,255,0.5); font-family:monospace; line-height:1;">2048</span>
      <span style="position:absolute; bottom:0; right:3px; font-size:0.6em; color:rgba(255,255,255,0.5); font-family:monospace; line-height:1;">0</span>
    </div>
    <div style="flex:1; position:relative;">
      <svg viewBox="0 0 380 120" style="width:100%; height:120px; display:block; border-left:1px solid rgba(255,255,255,0.2); border-bottom:1px solid rgba(255,255,255,0.2);">
        <line x1="0" y1="60" x2="380" y2="60" stroke="rgba(255,255,255,0.06)" stroke-width="1" stroke-dasharray="4,3"/>
        <line x1="0" y1="0" x2="380" y2="0" stroke="rgba(255,255,255,0.06)" stroke-width="1" stroke-dasharray="4,3"/>
        <polyline points="0,120 48,0 49,120 144,0 145,120 240,0 241,120 336,0 337,120 380,40" stroke="#00d4ff" stroke-width="2" fill="none" opacity="0.95"/>
        <polyline points="0,120 24,60 25,120 72,60 73,120 120,60 121,120 168,60 169,120 216,60 217,120 264,60 265,120 312,60 313,120 360,60 361,120 380,100" stroke="#ff3e3e" stroke-width="2" fill="none" opacity="0.95"/>
      </svg>
    </div>
  </div>
  <div style="font-size:0.6em; color:rgba(255,255,255,0.4); text-align:center; margin-top:0.2em;">Czas [s]</div>
  <div style="display:flex; gap:1.5em; margin-top:0.3em; font-size:0.68em;">
    <span style="display:flex; align-items:center; gap:0.4em;">
      <span style="display:inline-block; width:16px; height:2px; background:#ff3e3e;"></span>
      <span style="color:#ff3e3e;">Evil Twin — max 2045</span>
    </span>
    <span style="display:flex; align-items:center; gap:0.4em;">
      <span style="display:inline-block; width:16px; height:2px; background:#00d4ff;"></span>
      <span style="color:#00d4ff;">Oryginalny AP — max 4095</span>
    </span>
  </div>
</div>



</div>
<div>
<div v-click class="glass" style="margin-bottom:1em;">
  <span class="badge badge-green">Najsilniejsza metoda</span>
  <div style="margin-top:0.6em; font-size:0.85em;">
    + Niezależna od producenta<br>
    + Nie da się zmanipulować (hardware)<br>
    + Twardy dowód: 2 strumienie = 2 urządzenia
  </div>
</div>
<div v-click class="glass">
  <div style="font-size:0.85em;">
    <span class="badge badge-red">Nasze dane</span>
    <div style="margin-top:0.6em; font-family:'JetBrains Mono',monospace; font-size:0.85em;">
      Evil Twin: <strong style="color:#ff3e3e;">0 – 2045</strong><br>
      Oryginalny: <strong style="color:#00d4ff;">0 – 4095</strong><br>
      Overlap: <strong>brak nakładania</strong><br>
      <span style="color:#00ff88;">→ DWA urządzenia potwierdzone</span>
    </div>
  </div>
</div>
</div>
</div>

---

## Wyniki — Evil Twin

<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:1em; margin-bottom:1.2em;">
  <div v-click class="stat-card">
    <div class="value" style="color:#00d4ff;">6810</div>
    <div class="label">Beaconów łącznie</div>
  </div>
  <div v-click class="stat-card">
    <div class="value" style="color:#ff3e3e;">2</div>
    <div class="label">Unikalne AP</div>
  </div>
  <div v-click class="stat-card">
    <div class="value" style="color:#ffaa00;">19.2</div>
    <div class="label">Delta RSSI [dBm]</div>
  </div>
  <div v-click class="stat-card">
    <div class="value" style="color:#00ff88;">14/17</div>
    <div class="label">IE różnic</div>
  </div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em;">
<div v-click style="padding:0.8em; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.08); border-radius:12px;">
  <div style="font-size:0.72em; color:rgba(255,255,255,0.55); margin-bottom:0.4em;">Ramki Beacon przechwycone</div>
  <div style="height:110px; position:relative; border-bottom:1px solid rgba(255,255,255,0.12); margin-bottom:0.4em;">
    <div style="position:absolute; bottom:0; left:25%; transform:translateX(-50%); text-align:center; width:70px;">
      <div style="font-family:'JetBrains Mono',monospace; font-weight:600; color:#ff3e3e; font-size:0.75em; line-height:1.2;">2928</div>
      <div style="width:52px; height:75px; margin:2px auto 0; background:linear-gradient(to top, rgba(255,62,62,0.15), #ff3e3e); border-radius:4px 4px 0 0;"></div>
    </div>
    <div style="position:absolute; bottom:0; left:75%; transform:translateX(-50%); text-align:center; width:70px;">
      <div style="font-family:'JetBrains Mono',monospace; font-weight:600; color:#00d4ff; font-size:0.75em; line-height:1.2;">3882</div>
      <div style="width:52px; height:100px; margin:2px auto 0; background:linear-gradient(to top, rgba(0,212,255,0.15), #00d4ff); border-radius:4px 4px 0 0;"></div>
    </div>
  </div>
  <div style="display:flex; justify-content:space-around; font-size:0.68em; color:rgba(255,255,255,0.5);">
    <span>Evil Twin</span>
    <span>Oryginalny</span>
  </div>
</div>
<div v-click>
  <div class="glass" style="margin-bottom:0.8em;">
    <div style="font-size:0.85em;">
      <span class="badge badge-cyan">Wszystkie 3 metody potwierdzają</span>
      <div style="margin-top:0.5em; font-size:0.9em;">
        IE Fingerprinting: <strong>różne OUI</strong><br>
        RSSI: anomalia <strong>Delta = 19.2 dBm</strong><br>
        Seq Numbers: <strong>2 niezależne strumienie</strong>
      </div>
    </div>
  </div>
  <div class="verdict">
    <div class="text">EVIL TWIN CONFIRMED</div>
  </div>
</div>
</div>

---

## Wyniki — KARMA i MANA

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>
<div style="font-size:0.85em; margin-bottom:0.8em;">
  <strong style="color:#ffaa00;">Anomalia:</strong> 1 BSSID nadaje wiele różnych SSIDów — to niemożliwe w normalnej sieci.
</div>
<div style="padding:1.2em; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.08); border-radius:12px;">
  <div style="font-size:0.8em; color:rgba(255,255,255,0.55); margin-bottom:0.8em;">Beacony od BSSID <span style="font-family:'JetBrains Mono',monospace;">64:70:02:18:B9:22</span></div>
  <div style="display:flex; flex-direction:column; gap:0.6rem;">
    <div style="display:flex; align-items:center; gap:0.8rem;">
      <div style="width:90px; text-align:right; font-size:0.85em; font-family:'JetBrains Mono',monospace; color:#ff3e3e;">FreeWiFi</div>
      <div style="flex:1; height:26px; background:rgba(255,255,255,0.03); border-radius:6px; overflow:hidden;">
        <div style="width:100%; height:100%; background:linear-gradient(to right, rgba(255,62,62,0.2), #ff3e3e); border-radius:6px; display:flex; align-items:center; padding-left:0.8em; font-family:'JetBrains Mono',monospace; font-size:0.8em; font-weight:600; color:#fff;">267</div>
      </div>
    </div>
    <div style="display:flex; align-items:center; gap:0.8rem;">
      <div style="width:90px; text-align:right; font-size:0.85em; font-family:'JetBrains Mono',monospace; color:#ffaa00;">601A</div>
      <div style="flex:1; height:26px; background:rgba(255,255,255,0.03); border-radius:6px; overflow:hidden;">
        <div style="width:95%; height:100%; background:linear-gradient(to right, rgba(255,170,0,0.2), #ffaa00); border-radius:6px; display:flex; align-items:center; padding-left:0.8em; font-family:'JetBrains Mono',monospace; font-size:0.8em; font-weight:600; color:#fff;">253</div>
      </div>
    </div>
    <div style="display:flex; align-items:center; gap:0.8rem;">
      <div style="width:90px; text-align:right; font-size:0.85em; font-family:'JetBrains Mono',monospace; color:rgba(255,255,255,0.4);">Starbucks</div>
      <div style="flex:1; height:26px; background:rgba(255,255,255,0.03); border-radius:6px;"><span style="font-size:0.75em; color:rgba(255,255,255,0.35); font-style:italic; padding:0.3em 0.8em;">not seen</span></div>
    </div>
    <div style="display:flex; align-items:center; gap:0.8rem;">
      <div style="width:90px; text-align:right; font-size:0.85em; font-family:'JetBrains Mono',monospace; color:rgba(255,255,255,0.4);">eduroam</div>
      <div style="flex:1; height:26px; background:rgba(255,255,255,0.03); border-radius:6px;"><span style="font-size:0.75em; color:rgba(255,255,255,0.35); font-style:italic; padding:0.3em 0.8em;">not seen</span></div>
    </div>
  </div>
</div>
</div>
<div>
<div v-click class="glass" style="margin-bottom:1em;">
  <span class="badge badge-orange">KARMA — wyniki</span>
  <div style="margin-top:0.6em; font-size:0.85em;">
    iPhone wysyła probe requesty<br>
    KARMA odpowiada beaconem z żądanym SSID<br>
    Przechwycone: <strong>601A</strong> + <strong>FreeWiFi</strong>
  </div>
</div>
<div v-click class="glass" style="margin-bottom:1em;">
  <span class="badge badge-purple">MANA — wyniki</span>
  <div style="margin-top:0.6em; font-size:0.85em;">
    MANA AP uruchomiony — Tak<br>
    Directed probe przechwycony — Tak<br>
    Captive Portal na iOS — Nie (Apple CNA blokuje)
  </div>
</div>
<div v-click class="verdict" style="border-color:#ffaa00; background:rgba(255,170,0,0.08);">
  <div class="text" style="color:#ffaa00;">KARMA/MANA DETECTED</div>
  <div style="font-size:0.8em; color:rgba(255,255,255,0.55); margin-top:0.2em;">1 BSSID → wiele SSIDs = anomalia</div>
</div>
</div>
</div>

---

## Captive Portal — przechwycenie hasła

<div style="display: grid; grid-template-columns: 0.7fr 1.3fr; gap: 2em; align-items:start;">
<div v-click style="text-align:center;">
  <img src="/ukradniecie_hasla.jpeg" style="max-height:380px; border-radius:16px; border:2px solid rgba(255,255,255,0.08); box-shadow: 0 10px 40px rgba(0,0,0,0.5);" />
  <div style="font-size:0.75em; color:rgba(255,255,255,0.55); margin-top:0.5em;">Captive portal na iPhone ofiary</div>
</div>
<div>
<div v-click class="glass" style="margin-bottom:1em;">
  <span class="badge badge-red">Scenariusz ataku</span>
  <div style="margin-top:0.6em; font-size:0.85em;">
    <strong>1.</strong> Evil Twin z captive portalem (WiFiSlayer)<br>
    <strong>2.</strong> Ofiara łączy się → fałszywy portal<br>
    <strong>3.</strong> „Firmware Update Required" — socjotechnika<br>
    <strong>4.</strong> Ofiara wpisuje hasło Wi-Fi
  </div>
</div>
<div v-click class="glass" style="margin-bottom:1em; border-left: 3px solid #ff3e3e;">
  <div style="font-size:0.85em;">
    <div style="color:rgba(255,255,255,0.55); font-size:0.85em;">Przechwycone hasło:</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:1.8em; color:#ff3e3e; font-weight:700; margin-top:0.2em;">
      mama1234
    </div>
  </div>
</div>
<div v-click style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8em;">
  <div class="stat-card">
    <div class="value" style="color:#00ff88; font-size:1.4em;">OK</div>
    <div class="label">DNS redirect<br>dnsmasq</div>
  </div>
  <div class="stat-card">
    <div class="value" style="color:#ff3e3e; font-size:1.4em;">55 490</div>
    <div class="label">pakietów w<br>10 cyklach</div>
  </div>
</div>
</div>
</div>

---

## Eksperyment — 10 cykli ON/OFF

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8em; margin-bottom: 1.2em;">
  <div v-click class="stat-card">
    <div class="value" style="color:#00d4ff; font-size:1.5em;">55 490</div>
    <div class="label">Pakietów</div>
  </div>
  <div v-click class="stat-card">
    <div class="value" style="color:#ff3e3e; font-size:1.5em;">2 928</div>
    <div class="label">Beacony ET</div>
  </div>
  <div v-click class="stat-card">
    <div class="value" style="color:#00ff88; font-size:1.5em;">10/10</div>
    <div class="label">Reconnect</div>
  </div>
  <div v-click class="stat-card">
    <div class="value" style="color:#ffaa00; font-size:1.5em;">~6s</div>
    <div class="label">Śr. czas</div>
  </div>
</div>
<div v-click class="glass">
  <div style="font-size:0.85em;">
    iPhone przechodzi między AP <strong style="color:#ff3e3e;">automatycznie, bez wiedzy użytkownika</strong>
    — w 10 próbach ani razu nie stwierdzono braku reconnectu.
  </div>
</div>
</div>
<div>
<div v-click class="glass" style="margin-bottom:1em;">
  <span class="badge badge-cyan">Przebieg eksperymentu</span>
  <div style="margin-top:0.8em; font-size:0.85em;">

| Cykl | Evil Twin | Reconnect | Czas |
|---|---|---|---|
| 1–3 | ON → OFF → ON | Tak | ~5s |
| 4–7 | ON → OFF → ON | Tak | ~6s |
| 8–10 | ON → OFF → ON | Tak | ~7s |

  </div>
</div>
<div v-click class="verdict" style="border-color:#ffaa00; background:rgba(255,170,0,0.05);">
  <div class="text" style="color:#ffaa00;">100% RECONNECT RATE</div>
  <div style="font-size:0.8em; color:rgba(255,255,255,0.55);">Atak działa za każdym razem</div>
</div>
</div>
</div>

---

## Mitygacja — jak się bronić?

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em; margin-top: 0.5em;">
<div>
  <div style="text-align:center; margin-bottom:1em;">
    <span class="badge badge-cyan" style="font-size:0.9em;">Administratorzy sieci</span>
  </div>

<v-clicks>

  <div class="glass" style="margin-bottom:0.8em; border-left: 3px solid #00d4ff;">
    <div style="font-size:0.85em;">
      <strong>802.11w (PMF)</strong><br>
      <span style="color:rgba(255,255,255,0.55);">Protected Management Frames — blokuje fałszywy deauth</span>
    </div>
  </div>
  <div class="glass" style="margin-bottom:0.8em; border-left: 3px solid #00d4ff;">
    <div style="font-size:0.85em;">
      <strong>WIDS / WIPS</strong><br>
      <span style="color:rgba(255,255,255,0.55);">Monitoring duplikatów SSID, anomalii RSSI, wzorców KARMA</span>
    </div>
  </div>
  <div class="glass" style="border-left: 3px solid #00d4ff;">
    <div style="font-size:0.85em;">
      <strong>EAP-TLS</strong><br>
      <span style="color:rgba(255,255,255,0.55);">Certyfikaty dla AP — klient weryfikuje tożsamość</span>
    </div>
  </div>

</v-clicks>

</div>
<div>
  <div style="text-align:center; margin-bottom:1em;">
    <span class="badge badge-green" style="font-size:0.9em;">Użytkownicy</span>
  </div>

<v-clicks>

  <div class="glass" style="margin-bottom:0.8em; border-left: 3px solid #00ff88;">
    <div style="font-size:0.85em;">
      <strong>VPN</strong><br>
      <span style="color:rgba(255,255,255,0.55);">Szyfruje ruch nawet na rogue AP — atakujący widzi „szum"</span>
    </div>
  </div>
  <div class="glass" style="margin-bottom:0.8em; border-left: 3px solid #00ff88;">
    <div style="font-size:0.85em;">
      <strong>DNS-over-HTTPS</strong><br>
      <span style="color:rgba(255,255,255,0.55);">Ukrywa zapytania DNS przed przechwyceniem</span>
    </div>
  </div>
  <div class="glass" style="border-left: 3px solid #00ff88;">
    <div style="font-size:0.85em;">
      <strong>Auto-join wyłączony</strong><br>
      <span style="color:rgba(255,255,255,0.55);">Nie łącz się automatycznie z sieciami Wi-Fi</span>
    </div>
  </div>

</v-clicks>

</div>
</div>

---
layout: center
class: text-center
---

# Podsumowanie

<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:1.2em; margin-bottom:2em; margin-top:1.5em; max-width:800px; margin-left:auto; margin-right:auto;">
<div v-click class="stat-card" style="border-top: 3px solid #ff3e3e;">
  <div class="value" style="color:#ff3e3e; font-size:1.6em;">3</div>
  <div class="label">Typy ataków</div>
</div>
<div v-click class="stat-card" style="border-top: 3px solid #00d4ff;">
  <div class="value" style="color:#00d4ff; font-size:1.6em;">3</div>
  <div class="label">Metody detekcji</div>
</div>
<div v-click class="stat-card" style="border-top: 3px solid #00ff88;">
  <div class="value" style="color:#00ff88; font-size:1.6em;">55K</div>
  <div class="label">Pakietów</div>
</div>
<div v-click class="stat-card" style="border-top: 3px solid #ffaa00;">
  <div class="value" style="color:#ffaa00; font-size:1.6em;">100%</div>
  <div class="label">Reconnect</div>
</div>
</div>

<div v-click style="margin-bottom:2em;">
  <div class="glass" style="display:inline-block; padding:0.8em 2em;">
    <span style="font-family:'JetBrains Mono',monospace; font-size:0.9em;">
      analyze_pcap.py + beacon_diff.py — <span style="color:#00ff88;">open source (MIT)</span>
    </span>
  </div>
</div>

<div v-click>
  <p style="font-family:'JetBrains Mono',monospace; color:#00d4ff; font-size:1.1em; margin-bottom:1.5em;">
    github.com/Hose-Zur/BBSK-Evil-Twin
  </p>
  <p style="font-size:1.5em; color:rgba(255,255,255,0.55);">Pytania?</p>
</div>
