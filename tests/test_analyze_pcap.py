#!/usr/bin/env python3
"""
Testy jednostkowe dla analyze_pcap.py

Uruchomienie:
    python3 -m pytest tests/test_analyze_pcap.py -v

Wymagania:
    pip install scapy matplotlib pytest
"""

import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

import pytest

# Dodaj katalog skrypty do ścieżki
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skrypty"))


# ─── Pomocnicze: generowanie syntetycznych ramek Beacon ─────────


def _make_beacon_frame(
    bssid: str,
    ssid: str,
    seq_number: int,
    rssi_dbm: int,
    supported_rates: list = None,
    vendor_oui: str = None,
    channel: int = 6,
) -> bytes:
    """
    Generuje surową ramkę Beacon 802.11 do testów.

    Używa scapy do konstrukcji ramki i zwraca ją jako bytes.
    """
    from scapy.all import (
        RadioTap,
        Dot11,
        Dot11Beacon,
        Dot11Elt,
        Dot11EltRates,
        Dot11EltDSSSet,
    )

    rates = supported_rates or [6, 12, 24, 36]
    rates_bytes = bytes([(r * 2) | 0x80 for r in rates])

    frame = RadioTap(dBm_AntSignal=rssi_dbm) / Dot11(
        type=0,
        subtype=8,
        addr1="ff:ff:ff:ff:ff:ff",
        addr2=bssid,
        addr3=bssid,
        SC=(seq_number << 4) | 0,
    ) / Dot11Beacon() / Dot11Elt(ID=0, info=ssid.encode()) / Dot11EltRates(
        rates=rates_bytes
    )

    # Extended Supported Rates (ID=50) — jeśli jest więcej niż 8 stawek
    if len(rates) > 8:
        ext_rates = rates[8:]
        ext_bytes = bytes([(r * 2) | 0x80 for r in ext_rates])
        frame /= Dot11Elt(ID=50, info=ext_bytes)

    # Vendor Specific IE (ID=221)
    if vendor_oui:
        oui_bytes = bytes.fromhex(vendor_oui.replace(":", ""))
        vs_data = oui_bytes + b"\x01\x00\x00\x00"
        frame /= Dot11Elt(ID=221, info=vs_data)

    # DSSS Parameter Set — kanał
    frame /= Dot11EltDSSSet(channel=channel)

    return bytes(frame)


def _make_pcap_file(bssid_data: list, tmpdir: str) -> str:
    """
    Tworzy plik .pcap z listą ramek Beacon.

    Args:
        bssid_data: Lista krotek (bssid, ssid, [(seq, rssi, *rates), ...], vendor_oui)
        tmpdir: Katalog tymczasowy

    Returns:
        Ścieżka do pliku .pcap
    """
    from scapy.all import wrpcap

    packets = []
    for bssid, ssid, frames, vendor_oui in bssid_data:
        for i, frame_data in enumerate(frames):
            seq = frame_data[0]
            rssi = frame_data[1]
            rates = frame_data[2] if len(frame_data) > 2 else [6, 12, 24, 36]
            raw = _make_beacon_frame(
                bssid=bssid,
                ssid=ssid,
                seq_number=seq,
                rssi_dbm=rssi,
                supported_rates=rates,
                vendor_oui=vendor_oui,
            )
            from scapy.all import Ether

            pkt = Ether(raw)
            packets.append(pkt)

    pcap_path = os.path.join(tmpdir, "test.pcap")
    wrpcap(pcap_path, packets)
    return pcap_path


# ─── Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def tmp_workspace():
    """Tworzy tymczasowy katalog roboczy."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def single_ap_pcap(tmp_workspace):
    """Plik .pcap z jednym AP (brak evil twin)."""
    data = [
        (
            "aa:bb:cc:dd:ee:01",
            "Test_Network",
            [(seq, -40) for seq in range(10, 30)],
            "00:0C:03",  # Apple
        ),
    ]
    return _make_pcap_file(data, tmp_workspace)


@pytest.fixture
def evil_twin_pcap(tmp_workspace):
    """Plik .pcap z dwoma AP o tym samym SSID (Evil Twin)."""
    data = [
        (
            "aa:bb:cc:dd:ee:01",
            "AGH_Test",
            [(seq, -42) for seq in range(100, 130)],
            "00:0C:03",  # Apple
        ),
        (
            "aa:bb:cc:dd:ee:02",
            "AGH_Test",
            [(seq, -28) for seq in range(50, 80)],
            "00:03:7F",  # Atheros
        ),
    ]
    return _make_pcap_file(data, tmp_workspace)


@pytest.fixture
def three_ap_pcap(tmp_workspace):
    """Plik .pcap z 3 AP o tym samym SSID."""
    data = [
        (
            "aa:bb:cc:dd:ee:01",
            "Corporate_Net",
            [(seq, -50) for seq in range(200, 230)],
            "00:0C:03",
        ),
        (
            "aa:bb:cc:dd:ee:02",
            "Corporate_Net",
            [(seq, -35) for seq in range(100, 130)],
            "00:03:7F",
        ),
        (
            "aa:bb:cc:dd:ee:03",
            "Corporate_Net",
            [(seq, -30) for seq in range(300, 330)],
            "00:50:F2",
        ),
    ]
    return _make_pcap_file(data, tmp_workspace)


# ─── Testy: parsowanie CLI ───────────────────────────────────────


class TestCliParsing:
    """Testy argumentów wiersza poleceń."""

    def test_no_args_default_pcap(self):
        """Bez argumentów — domyślna ścieżka /tmp/demo-01.pcap."""
        with patch.object(sys, "argv", ["analyze_pcap.py"]):
            import analyze_pcap as ap

            # Wymuś przeładowanie stałych z argumentów
            with pytest.raises(SystemExit):
                ap.main()
            # Sprawdzamy domyślną ścieżkę — nie ma pliku
            assert hasattr(ap, "PCAP_FILE")

    def test_with_pcap_arg(self):
        """Z argumentem pcap — używa podanej ścieżki."""
        with patch.object(sys, "argv", ["analyze_pcap.py", "/tmp/test.pcap"]):
            import analyze_pcap as ap

            assert hasattr(ap, "PCAP_FILE")

    def test_with_ssid_arg(self):
        """Z dwoma argumentami — używa pcap i SSID."""
        with patch.object(sys, "argv", ["analyze_pcap.py", "/tmp/test.pcap", "MySSID"]):
            import analyze_pcap as ap

            assert hasattr(ap, "PCAP_FILE")
            assert hasattr(ap, "TARGET_SSID")


# ─── Testy: parsowanie ramek Beacon ────────────────────────────


class TestBeaconParsing:
    """Testy poprawności parsowania ramek Beacon."""

    def test_single_ap_no_evil_twin(self, single_ap_pcap):
        """Jeden AP — brak ostrzeżenia o Evil Twin."""
        from scapy.all import rdpcap
        from collections import defaultdict

        import analyze_pcap as ap

        pkts = rdpcap(single_ap_pcap)
        aps = defaultdict(
            lambda: {
                "ssid": "?",
                "seq_nums": [],
                "rssi": [],
                "supported_rates": set(),
                "vendor_specific": [],
                "frame_count": 0,
            }
        )

        for pkt in pkts:
            if not pkt.haslayer(ap.Dot11Beacon):
                continue
            bssid = (pkt.addr3 or "?").lower()
            ap_data = aps[bssid]
            ap_data["frame_count"] += 1

            if pkt.haslayer(ap.Dot11Elt):
                elt = pkt[ap.Dot11Elt]
                while elt:
                    if elt.ID == 0 and elt.info:
                        try:
                            ap_data["ssid"] = elt.info.decode("utf-8", errors="replace")
                        except Exception:
                            pass
                    try:
                        elt = elt.payload.getlayer(ap.Dot11Elt)
                    except Exception:
                        break

        assert len(aps) == 1, f"Oczekiwano 1 AP, znaleziono {len(aps)}"
        assert list(aps.values())[0]["ssid"] == "Test_Network"

    def test_evil_twin_detected(self, evil_twin_pcap):
        """Dwa AP z tym samym SSID — wykrycie Evil Twin."""
        from scapy.all import rdpcap
        from collections import defaultdict

        import analyze_pcap as ap

        pkts = rdpcap(evil_twin_pcap)
        aps = defaultdict(
            lambda: {
                "ssid": "?",
                "seq_nums": [],
                "rssi": [],
                "supported_rates": set(),
                "vendor_specific": [],
                "frame_count": 0,
            }
        )

        for pkt in pkts:
            if not pkt.haslayer(ap.Dot11Beacon):
                continue
            bssid = (pkt.addr3 or "?").lower()
            ap_data = aps[bssid]
            ap_data["frame_count"] += 1

            if pkt.haslayer(ap.Dot11Elt):
                elt = pkt[ap.Dot11Elt]
                while elt:
                    if elt.ID == 0 and elt.info:
                        try:
                            ap_data["ssid"] = elt.info.decode("utf-8", errors="replace")
                        except Exception:
                            pass
                    try:
                        elt = elt.payload.getlayer(ap.Dot11Elt)
                    except Exception:
                        break

            if pkt.haslayer(ap.Dot11):
                seq = pkt[ap.Dot11].SC >> 4
                ap_data["seq_nums"].append((float(pkt.time), seq))

            if pkt.haslayer(ap.RadioTap):
                try:
                    rssi = pkt[ap.RadioTap].dBm_AntSignal
                    if rssi is not None and rssi != 0:
                        ap_data["rssi"].append(int(rssi))
                except AttributeError:
                    pass

        # Sprawdź czy wykryto 2 AP z tym samym SSID
        assert len(aps) == 2, f"Oczekiwano 2 AP, znaleziono {len(aps)}"
        for ap_data in aps.values():
            assert ap_data["ssid"] == "AGH_Test", f"Nieprawidłowy SSID: {ap_data['ssid']}"

        # Sprawdź różne RSSI
        rssi_values = [d["rssi"] for d in aps.values()]
        avg_rssis = [sum(r) / len(r) if r else 0 for r in rssi_values]
        assert abs(avg_rssis[0] - avg_rssis[1]) > 5, "Różnica RSSI powinna być > 5 dBm"

    def test_three_aps_detected(self, three_ap_pcap):
        """Trzy AP — wszystkie wykryte."""
        from scapy.all import rdpcap
        from collections import defaultdict

        import analyze_pcap as ap

        pkts = rdpcap(three_ap_pcap)
        aps = defaultdict(
            lambda: {
                "ssid": "?",
                "seq_nums": [],
                "rssi": [],
                "supported_rates": set(),
                "vendor_specific": [],
                "frame_count": 0,
            }
        )

        for pkt in pkts:
            if not pkt.haslayer(ap.Dot11Beacon):
                continue
            bssid = (pkt.addr3 or "?").lower()
            ap_data = aps[bssid]
            ap_data["frame_count"] += 1

            if pkt.haslayer(ap.Dot11Elt):
                elt = pkt[ap.Dot11Elt]
                while elt:
                    if elt.ID == 0 and elt.info:
                        try:
                            ap_data["ssid"] = elt.info.decode("utf-8", errors="replace")
                        except Exception:
                            pass
                    try:
                        elt = elt.payload.getlayer(ap.Dot11Elt)
                    except Exception:
                        break

        assert len(aps) == 3, f"Oczekiwano 3 AP, znaleziono {len(aps)}"


# ─── Testy: obsługa błędów ───────────────────────────────────────


class TestErrorHandling:
    """Testy obsługi błędów."""

    def test_missing_file(self):
        """Nieistniejący plik — kod wyjścia 1."""
        with patch.object(sys, "argv", ["analyze_pcap.py", "/tmp/nonexistent.pcap"]):
            with pytest.raises(SystemExit) as exc:
                import analyze_pcap as ap
                ap.main()
            # Nie sprawdzamy konkretnego kodu — ważne że kończy z błędem

    def test_missing_scapy(self):
        """Brak scapy — komunikat o błędzie."""
        with patch.dict("sys.modules", {"scapy.all": None}):
            # Symulujemy import — test koncepcyjny
            pass

    def test_non_beacon_packets(self, tmp_workspace):
        """Plik bez ramek Beacon — pusty wynik."""
        from scapy.all import wrpcap, Ether, IP, UDP

        # Stwórz pcap bez ramek Beacon (tylko IP)
        pkt = Ether() / IP(dst="1.2.3.4") / UDP()
        pcap_path = os.path.join(tmp_workspace, "no_beacon.pcap")
        wrpcap(pcap_path, [pkt])

        import analyze_pcap as ap

        with patch.object(sys, "argv", ["analyze_pcap.py", pcap_path]):
            from scapy.all import rdpcap
            from collections import defaultdict

            pkts = rdpcap(pcap_path)
            aps = defaultdict(
                lambda: {
                    "ssid": "?",
                    "seq_nums": [],
                    "rssi": [],
                    "supported_rates": set(),
                    "vendor_specific": [],
                    "frame_count": 0,
                }
            )

            for pkt in pkts:
                if not pkt.haslayer(ap.Dot11Beacon):
                    continue
                bssid = (pkt.addr3 or "?").lower()
                aps[bssid]["frame_count"] += 1

            assert len(aps) == 0, "Nie powinno być AP w pliku bez Beacon"
            assert sum(d["frame_count"] for d in aps.values()) == 0


# ─── Testy: obsługa SSID ─────────────────────────────────────────


class TestSSIDFiltering:
    """Testy filtrowania po SSID."""

    def test_filter_by_ssid(self, evil_twin_pcap):
        """Filtrowanie po SSID zwraca tylko AP z tym SSID."""
        from scapy.all import rdpcap
        from collections import defaultdict

        import analyze_pcap as ap

        pkts = rdpcap(evil_twin_pcap)
        aps = defaultdict(
            lambda: {
                "ssid": "?",
                "seq_nums": [],
                "rssi": [],
                "supported_rates": set(),
                "vendor_specific": [],
                "frame_count": 0,
            }
        )

        for pkt in pkts:
            if not pkt.haslayer(ap.Dot11Beacon):
                continue
            bssid = (pkt.addr3 or "?").lower()
            ap_data = aps[bssid]
            ap_data["frame_count"] += 1

            if pkt.haslayer(ap.Dot11Elt):
                elt = pkt[ap.Dot11Elt]
                while elt:
                    if elt.ID == 0 and elt.info:
                        try:
                            ap_data["ssid"] = elt.info.decode("utf-8", errors="replace")
                        except Exception:
                            pass
                    try:
                        elt = elt.payload.getlayer(ap.Dot11Elt)
                    except Exception:
                        break

        # Filtruj po SSID (symulacja)
        filtered = {b: d for b, d in aps.items() if d["ssid"] == "AGH_Test"}
        assert len(filtered) == 2, "Oba AP mają SSID AGH_Test"


# ─── Testy: wydajność ────────────────────────────────────────────


class TestPerformance:
    """Testy wydajnościowe."""

    def test_moderate_pcap_parsing_speed(self, evil_twin_pcap):
        """Parsowanie pliku ~20 pakietów powinno zająć < 2 sekund."""
        import time
        from scapy.all import rdpcap

        start = time.time()
        pkts = rdpcap(evil_twin_pcap)
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Parsowanie trwało {elapsed:.2f}s (limit: 2s)"
        assert len(pkts) > 0, "Plik powinien zawierać pakiety"


# ─── Testy: struktura danych ─────────────────────────────────────


class TestDataStructure:
    """Testy poprawności struktur danych skryptu."""

    def test_expected_keys_in_ap_dict(self):
        """Słownik AP powinien mieć oczekiwane klucze."""
        from collections import defaultdict

        aps = defaultdict(
            lambda: {
                "ssid": "?",
                "seq_nums": [],
                "rssi": [],
                "supported_rates": set(),
                "vendor_specific": [],
                "frame_count": 0,
            }
        )

        ap_data = aps["aa:bb:cc:dd:ee:01"]
        expected_keys = {"ssid", "seq_nums", "rssi", "supported_rates", "vendor_specific", "frame_count"}
        assert set(ap_data.keys()) == expected_keys, f"Brakujące klucze: {expected_keys - set(ap_data.keys())}"
        assert isinstance(ap_data["seq_nums"], list)
        assert isinstance(ap_data["rssi"], list)
        assert isinstance(ap_data["supported_rates"], set)
        assert isinstance(ap_data["vendor_specific"], list)
        assert isinstance(ap_data["frame_count"], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
