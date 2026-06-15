# Beacon Frame Diff — Porównanie fingerprintów AP

**Data:** 2026-06-15 11:41 UTC

## AP #1
- **BSSID:** `64:70:02:18:B9:22`
- **SSID:** 601A
- **Ramki Beacon:** 333

## AP #2
- **BSSID:** `7C:F1:7E:C1:7B:95`
- **SSID:** 601A
- **Ramki Beacon:** 296

## Metryki

| Metryka | AP #1 | AP #2 | Różnica |
|---|---|---|---|
| Śr. RSSI | -22.6 dBm | -41.2 dBm | 18.6 dBm |
| Zakres seq | 1559–1894 | 2297–3723 | — |
| Ramki | 333 | 296 | 37 |

## Porównanie IE

### ❌ Supported Rates — RÓŻNICA

- **AP #1:** 82848b960c121824
- **AP #2:** 82848b961224486c

### ✅ DSSS Parameter Set
Wspólne: Channel 4

### ❌ TIM (Traffic Indication Map) — RÓŻNICA

- **AP #1:** 01020006, 01020000, 00020004, 00020002
- **AP #2:** 00010000

### ❌ BSS Load — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** 010000127a

### ❌ Power Constraint — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** 00

### ❌ TPC Report — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** 3f00

### ✅ ERP Information
Wspólne: Barker_Preamble

### ❌ HT Capabilities — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** LDPC, HT40, SGI20, SGI40, Tx-STBC, Rx-STBC(1), MaxAMSDU-7935

### ✅ RSN Information
Wspólne: RSN (ver 1, len 20B)

### ❌ Extended Supported Rates — RÓŻNICA

- **AP #1:** 3048606c
- **AP #2:** 0c183060

### ❌ AP Channel Report — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** 0b010203040506070809

### ❌ HT Operation — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** PrimaryCh=4, SecOffset=0, ChWidth=40MHz

### ❌ QoS Map Set — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** 0200000000

### ❌ Expedited Bandwidth Request — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** 14000a002c01c800140005001900

### ❌ Extended Capabilities — RÓŻNICA

- **AP #1:** len=8B, raw:0000000200000040
- **AP #2:** len=8B, raw:0100080000000000

### ❌ VHT Tx Power Envelope — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** b179c133faff0c03faff0c03

### ❌ MCCAOP Advertisement Overview — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** 000000faff

### ❌ Vendor Specific — RÓŻNICA

- **AP #1:** (brak unikalnych)
- **AP #2:** OUI:001D0F | raw:001d0f10016300007cf17ec17b957cf17ec17b95306100007b9500010000, Microsoft (WPS) | raw:0050f204104a000110104400010210470010000000000000100000007cf17ec17b95103c0001031049000600372a000120, Microsoft (WPS) | raw:0050f2020101800003a4000027a4000042435e0062322f00, OUI:000CE7 | raw:000ce708000000bf0cb101c0332aff92042aff9204c0050000002affc303010202, OUI:000C43 | raw:000c4309000000

## 🔴 WERDYKT: EVIL TWIN POTWIERDZONY