import json
from pathlib import Path

def load_settings():
    p = Path("settings.json")
    with p.open("r", encoding="utf-8-sig"):  
        return json.load(p.open("r", encoding="utf-8-sig"))

def main():
    cfg = load_settings()
    inst = cfg.get("instance")
    print(f"ETL instance {inst}: START")
 
    time.sleep(1)
    print(f"ETL instance {inst}: OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
