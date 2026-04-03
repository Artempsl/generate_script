"""Save raw Facticity API response to JSON file for inspection."""
import sys, json, winreg, requests
from pathlib import Path

def read_win_env(name):
    for hive, subkey in [
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        (winreg.HKEY_CURRENT_USER, "Environment"),
    ]:
        try:
            with winreg.OpenKey(hive, subkey) as k:
                val, _ = winreg.QueryValueEx(k, name)
                if val:
                    return str(val)
        except Exception:
            pass
    return ""

api_key = read_win_env("FACTICITY_API")
headers = {"Content-Type": "application/json", "x-api-key": api_key}
payload = {"query": "Water boils at 90 degrees Celsius at sea level.", "timeout": 60, "mode": "sync"}

out_path = Path(__file__).parent / "facticity_raw_response.json"

print("Sending request...", flush=True)
r = requests.post("https://api.facticity.ai/fact-check", json=payload, headers=headers, timeout=90)
print(f"Status: {r.status_code}", flush=True)

try:
    data = r.json()
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Response saved to: {out_path}", flush=True)
    # Print top-level keys for quick summary
    for k, v in data.items():
        if isinstance(v, str) and len(v) > 150:
            print(f"  {k!r}: {v[:120]!r}...", flush=True)
        elif isinstance(v, (dict, list)):
            print(f"  {k!r}: ({type(v).__name__})", flush=True)
        else:
            print(f"  {k!r}: {v!r}", flush=True)
except Exception as e:
    out_path.write_text(r.text, encoding="utf-8")
    print(f"Non-JSON response saved. Error: {e}", flush=True)
