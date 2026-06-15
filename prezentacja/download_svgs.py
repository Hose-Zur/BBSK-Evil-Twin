import base64
import urllib.request
import sys
import zlib
import json

def get_mermaid_svg(mermaid_code, filename):
    # mermaid.ink accepts base64 encoded JSON
    state = {
        "code": mermaid_code,
        "mermaid": '{"theme":"dark"}',
        "autoSync": True,
        "updateDiagram": True
    }
    json_str = json.dumps(state)
    b64 = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
    url = f"https://mermaid.ink/svg/{b64}"
    
    print(f"Fetching {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            svg_data = response.read()
            with open(filename, 'wb') as f:
                f.write(svg_data)
        print(f"Saved to {filename}")
    except Exception as e:
        print(f"Failed: {e}")

diagram1 = """flowchart TB
    subgraph SIEĆ["Sieć Wi-Fi: 601A"]
        AP["Legalny AP\\nBSSID: 7C:F1:..."]
        ET["Rogue AP\\nBSSID: 64:70:..."]
    end
    AP -->|"SSID: 601A\\n-42 dBm"| V["Klient"]
    ET -->|"SSID: 601A\\n-22 dBm"| V
    style ET fill:#ff3e3e22,stroke:#ff3e3e,color:#fff
    style AP fill:#00d4ff15,stroke:#00d4ff,color:#fff
    style V fill:#ffffff10,stroke:#888,color:#fff
    style SIEĆ fill:#ffffff05,stroke:#333,color:#aaa"""

diagram2 = """sequenceDiagram
    participant AP as Legalny AP
    participant V as Ofiara
    participant E as Evil Twin

    V->>AP: Połączony z "601A"
    E->>V: Deauth frame
    Note over V: Rozłączony!
    E->>V: Beacon "601A" (-22 dBm)
    V->>E: Association Request
    Note over V,E: Ofiara na Evil Twin!"""

diagram3 = """sequenceDiagram
    participant V as Ofiara
    participant K as KARMA AP

    V->>K: Probe: "Starbucks?"
    K->>V: Beacon: "Tak, jestem Starbucks!"
    V->>K: Probe: "FreeWiFi?"
    K->>V: Beacon: "Tak, jestem FreeWiFi!"
    V->>K: Probe: "601A?"
    K->>V: Beacon: "Tak, jestem 601A!"
    V->>K: Association Request
    Note over V,K: Ofiara złapana!"""

get_mermaid_svg(diagram1, 'public/diag1.svg')
get_mermaid_svg(diagram2, 'public/diag2.svg')
get_mermaid_svg(diagram3, 'public/diag3.svg')
