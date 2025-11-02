import json, os, sys, time

def load_settings():
    path = os.environ.get("SETTINGS_PATH", "settings.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def main():
    cfg = load_settings()
    inst = cfg.get("instance")
    print(f"ETL instance {inst}: START")
    # test
    time.sleep(1)
    print(f"ETL instance {inst}: OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
