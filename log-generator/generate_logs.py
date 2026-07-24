import json
import os

from log_builder import generate_log_file

CONFIG_PATH = "/app/data/log_config.json"
SIZE_LABELS = ["small", "medium", "large"]


def _load_config_from_file():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    sizes = {label: config[label] for label in SIZE_LABELS}
    print("[LOG-GENERATOR] Config loaded from file:")
    for label, count in sizes.items():
        print(f"  {label:8s} = {count:,} entries")
    return sizes


def _load_config_from_input():
    print("=" * 55)
    print("  KONFIGURASI UKURAN LOG")
    print("=" * 55)
    print("  Input jumlah entri log untuk tiap ukuran.")
    print("  ex: small=10000  medium=50000  large=250000")
    print("=" * 55)

    sizes = {}
    for label in SIZE_LABELS:
        while True:
            try:
                val   = input(f"  Jumlah entri [{label}]: ").strip()
                count = int(val.replace(".", "").replace(",", ""))
                if count < 1:
                    print("  X Harus lebih dari 0.")
                    continue
                sizes[label] = count
                break
            except ValueError:
                print("  X Input tidak valid.")

    print("=" * 55)
    print("  Konfigurasi yang akan digunakan:")
    for label, count in sizes.items():
        print(f"  {label:8s} = {count:,} entries")
    print("=" * 55)

    os.makedirs("/app/data", exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(sizes, f, indent=2)

    return sizes


def load_log_config():
    if os.path.exists(CONFIG_PATH):
        return _load_config_from_file()
    return _load_config_from_input()


def main():
    os.makedirs("/app/data", exist_ok=True)
    print("\n[LOG-GENERATOR] AWS CloudTrail Log Generator")
    print("=" * 55)

    log_sizes = load_log_config()

    print("\n[LOG-GENERATOR] Starting generation...")
    for size_label, count in log_sizes.items():
        generate_log_file(size_label, count)

    print("\n" + "=" * 55)
    print("[LOG-GENERATOR] All log files generated successfully.")
    print("=" * 55)


if __name__ == "__main__":
    main()
