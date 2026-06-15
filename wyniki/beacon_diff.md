# Beacon Frame Diff — Porównanie fingerprintów AP

**Data:** 2026-06-15 11:16 UTC

## AP #1
- **BSSID:** `7C:F1:7E:C1:7B:95`
- **SSID:** 601A
- **Ramki Beacon:** 1

## AP #2
- **BSSID:** `D2:49:1E:9F:39:AB`
- **SSID:** 601A
- **Ramki Beacon:** 1

## Metryki

| Metryka | AP #1 | AP #2 | Różnica |
|---|---|---|---|
| Zakres seq | 1342–1342 | 663–663 | — |
| Ramki | 1 | 1 | 0 |

## Porównanie IE

### ❌ Supported Rates — RÓŻNICA

- **AP #1:** 82848b961224486c
- **AP #2:** 82848b960c121824

### ✅ DSSS Parameter Set
Wspólne: Channel 4

### ❌ TIM (Traffic Indication Map) — RÓŻNICA

- **AP #1:** 00010002
- **AP #2:** 01020000

### ❌ BSS Load — RÓŻNICA

- **AP #1:** 040000127a
- **AP #2:** (brak unikalnych)

### ❌ Power Constraint — RÓŻNICA

- **AP #1:** 00
- **AP #2:** (brak unikalnych)

### ❌ TPC Report — RÓŻNICA

- **AP #1:** 3f00
- **AP #2:** (brak unikalnych)

### ✅ ERP Information
Wspólne: Barker_Preamble

### ❌ HT Capabilities — RÓŻNICA

- **AP #1:** LDPC, HT40, SGI20, SGI40, Tx-STBC, Rx-STBC(1), MaxAMSDU-7935
- **AP #2:** (brak unikalnych)

### ✅ RSN Information
Wspólne: RSN (ver 1, len 20B)

### ❌ Extended Supported Rates — RÓŻNICA

- **AP #1:** 0c183060
- **AP #2:** 3048606c

### ❌ AP Channel Report — RÓŻNICA

- **AP #1:** 0b010203040506070809
- **AP #2:** (brak unikalnych)

### ❌ HT Operation — RÓŻNICA

- **AP #1:** PrimaryCh=4, SecOffset=0, ChWidth=40MHz
- **AP #2:** (brak unikalnych)

### ❌ QoS Map Set — RÓŻNICA

- **AP #1:** 0200000000
- **AP #2:** (brak unikalnych)

### ❌ Expedited Bandwidth Request — RÓŻNICA

- **AP #1:** 14000a002c01c800140005001900
- **AP #2:** (brak unikalnych)

### ❌ Extended Capabilities — RÓŻNICA

- **AP #1:** len=8B, raw:0100080000000000
- **AP #2:** len=8B, raw:0000000200000040

### ❌ VHT Tx Power Envelope — RÓŻNICA

- **AP #1:** b179c133faff0c03faff0c03
- **AP #2:** (brak unikalnych)

### ❌ MCCAOP Advertisement Overview — RÓŻNICA

- **AP #1:** 000000faff
- **AP #2:** (brak unikalnych)

### ❌ Vendor Specific — RÓŻNICA

- **AP #1:** OUI:000CE7 | raw:000ce708000000bf0cb101c0332aff92042aff9204c0050000002affc303010202, OUI:001D0F | raw:001d0f10016300007cf17ec17b957cf17ec17b95306100007b9500010000, OUI:000C43 | raw:000c4309000000, Microsoft (WPS) | raw:0050f204104a000110104400010210470010000000000000100000007cf17ec17b95103c0001031049000600372a000120, Microsoft (WPS) | raw:0050f2020101800003a4000027a4000042435e0062322f00
- **AP #2:** (brak unikalnych)

## 🔴 WERDYKT: EVIL TWIN POTWIERDZONY