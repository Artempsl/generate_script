"""Quick single-claim test for new Facticity payload format."""
import sys, json, winreg, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
print(f"API key: {'SET (len=' + str(len(api_key)) + ')' if api_key else 'NOT SET'}")

headers = {"Content-Type": "application/json", "x-api-key": api_key}
payload = {
    "query": "Water boils at 90 degrees Celsius at sea level.",
    "timeout": 60,
    "mode": "sync",
}

print(f"Payload: {json.dumps(payload)}")
print("Sending request to Facticity API...")

r = requests.post("https://api.facticity.ai/fact-check", json=payload, headers=headers, timeout=90)
print(f"Status: {r.status_code}")
try:
    print(f"Response JSON:\n{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
except Exception:
    print(f"Response text: {r.text[:1000]}")
