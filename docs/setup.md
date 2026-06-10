# Konfiguracja środowiska

## Wymagania wstępne

- Komputer z **8+ GB RAM** i obsługą USB passthrough do VM
- **2× karty Wi-Fi** z obsługą trybu monitor i AP mode (testowane: TP-Link TL-WDN3200 / Ralink RT5572)
- **Kali Linux VM** (zalecana: 2024.x lub nowsza)
- **2 telefony** — jeden jako hotspot, drugi jako ofiara

---

## Krok 1: Konfiguracja Kali Linux

### Pobierz i zainstaluj Kali

```bash
# Opcja A: VirtualBox
https://www.kali.org/get-kali/#kali-virtualbox

# Opcja B: VMware / Parallels (macOS)
https://www.kali.org/get-kali/#kali-vmware
```

### Skonfiguruj passthrough USB

**VirtualBox:**
1. Zainstaluj VirtualBox Extension Pack
2. Ustaw VM → Settings → USB → USB 3.0 (xHCI) Controller
3. Dodaj obie karty Wi-Fi jako filtry USB
4. Uruchom VM

**Parallels Desktop (macOS):**
1. Ustaw VM → Hardware → USB & Bluetooth
2. Wybierz "Share with Linux"
3. Podłącz karty przez USB po resecie

### Instalacja zależności systemowych

Po uruchomieniu Kali:

```bash
# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Narzędzia Wi-Fi + analiza
sudo apt install airgeddon wireshark aircrack-ng python3-pip -y

# Zależności Pythona
pip3 install scapy matplotlib
```

---

## Krok 2: Weryfikacja kart Wi-Fi

### Sprawdź widoczne interfejsy

```bash
iw dev
```

Oczekiwany wynik (przykład):
```
phy#0
	Interface wlan0
		ifindex 3
		wdev 0x1
		addr 00:11:22:33:44:55
		type managed
phy#1
	Interface wlan1
		ifindex 4
		wdev 0x2
		addr 66:77:88:99:AA:BB
		type managed
```

Musisz widzieć **dwa** interfejsy (`wlan0`, `wlan1`).

### Sprawdź obsługę trybów

```bash
iw list | grep -A 15 "Supported interface modes"
```

Szukaj:
```
* AP
* monitor
```

Jeśli obie karty obsługują oba tryby — gotowe.

### Zapisz adresy MAC

```bash
ip link show wlan0 | grep "link/ether"
ip link show wlan1 | grep "link/ether"
```

Zapisz MAC adresy — przydadzą się przy analizie w Wireshark.

---

## Krok 3: Konfiguracja telefonów

### Telefon A — hotspot (oryginalny AP)

| Ustawienie | Wartość |
|---|---|
| SSID | `AGH_Test` (lub własny) |
| Zabezpieczenia | WPA2-Personal |
| Hasło | Cokolwiek (np. `test12345`) |
| Pasmo | 2.4 GHz (NIE 5 GHz) |
| Kanał | Automatyczny (telefon wybierze, zwykle 6 lub 1) |

**Uwaga:** Ustaw kanał ręcznie jeśli telefon pozwala — ułatwi to przechwytywanie. Jeśli nie — zanotuj kanał do airodump-ng.

### Telefon B — ofiara

Po prostu połącz z hotspotem telefonu A. Jest to symulacja "zaufanego użytkownika".

---

## Krok 4: Kopiowanie skryptu na Kali

Skrypt `analyze_pcap.py` znajduje się w repozytorium. Skopiuj go na Kali VM:

```bash
# Opcja A: Shared folder (VirtualBox)
cp /media/sf_BBSK-Evil-Twin/skrypty/analyze_pcap.py ~/

# Opcja B: SCP przez sieć
scp user@host:/path/to/analyze_pcap.py ~/

# Opcja C: Git clone na Kali
git clone <repo-url>
```

---

## Weryfikacja — skrypt reference

Sprawdź, czy skrypt się uruchamia (samo pomoc):

```bash
python3 ~/analyze_pcap.py 2>&1 | head -5
```

Oczekiwane: błąd o braku pliku (`Plik nie istnieje: /tmp/demo-01.pcap`), co oznacza że importy działają.

---

## Troubleshooting

| Problem | Rozwiązanie |
|---|---|
| `iw dev` pokazuje tylko 1 interfejs | Sprawdź USB passthrough w VM. Odłącz i podłącz ponownie karty |
| `airmon-ng start wlan0` — błąd z usługami | `sudo airmon-ng check kill` przed uruchomieniem |
| Brak `* AP` w `Supported interface modes` | Karta nie obsługuje trybu AP. RT5572 powinien — sprawdź sterowniki |
| Wireshark nie ma uprawnień do przechwytywania | Dodaj użytkownika do grupy wireshark: `sudo usermod -aG wireshark $USER` |
| airgeddon nie widzi karty do evil twin | Uruchom z `sudo`, wybierz odpowiedni interfejs ręcznie |
| `pip3 install` — błąd permissions | Użyj `--user` lub środowiska wirtualnego |
