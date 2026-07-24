import json
import os
import csv
from datetime import datetime

from hash_engines import ENGINES
from merkle_core import (
    get_merkle_root, get_merkle_proof_length,
    measure_build, measure_verify, measure_hash_computation,
    calc_throughput, tamper_log,
)

DATA_DIR            = "/app/data"
RESULTS_DIR         = "/app/results"
REPEAT              = 5
TAMPERING_POSITIONS = ["first", "middle", "last"]
RANDOM_RANGE_PCT    = 0.02


# ── I/O ──────────────────────────────────────────────────────

def get_experiment_folder() -> str:
    i = 1
    while True:
        folder = os.path.join(RESULTS_DIR, f"experiment{i}")
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"[MERKLE-ENGINE] Output folder: {folder}")
            return folder
        i += 1


def get_log_sizes() -> list[str]:
    config_path = os.path.join(DATA_DIR, "log_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return list(json.load(f).keys())
    return ["small", "medium", "large"]


def save_results(results: list, output_folder: str) -> None:
    fieldnames = [
        "algorithm", "log_size", "entry_count", "tamper_position",
        "build_time_ms", "verify_time_ms", "throughput_eps",
        "detection_accuracy_pct", "memory_peak_kb",
        "hash_time_us", "merkle_proof_length",
        "tamper_node_avg", "tamper_node_min", "tamper_node_max",
        "tamper_range_defined_min", "tamper_range_defined_max",
        "repeat",
    ]

    csv_path = os.path.join(output_folder, "results_raw.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"[MERKLE-ENGINE] Saved: {csv_path}")

    config_path = os.path.join(DATA_DIR, "log_config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)

    meta = {
        "experiment_folder":       os.path.basename(output_folder),
        "run_timestamp":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "log_sizes":               config,
        "algorithms":              list(ENGINES.keys()),
        "tamper_positions":        TAMPERING_POSITIONS,
        "tamper_random_range_pct": RANDOM_RANGE_PCT * 100,
        "repeat_per_scenario":     REPEAT,
        "total_scenarios":         len(results),
    }
    meta_path = os.path.join(output_folder, "experiment_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[MERKLE-ENGINE] Saved: {meta_path}")


# ── Runner ────────────────────────────────────────────────────

def run_scenario(logs: list, algo_name: str, hash_fn, size_label: str, tamper_pos: str) -> dict:
    build_times  = []
    verify_times = []
    throughputs  = []
    memory_kbs   = []
    detect_count = 0

    tamper_indices = []
    tamper_min     = None
    tamper_max     = None

    proof_length = get_merkle_proof_length(len(logs))
    hash_time_us = measure_hash_computation(logs, hash_fn)

    for _ in range(REPEAT):
        build_ms, mem_kb, tree = measure_build(logs, hash_fn)
        original_root          = get_merkle_root(tree)

        build_times.append(build_ms)
        throughputs.append(calc_throughput(len(logs), build_ms))
        memory_kbs.append(mem_kb)

        tampered_logs, t_idx, t_min, t_max = tamper_log(logs, tamper_pos)
        tamper_indices.append(t_idx)
        if tamper_min is None:
            tamper_min = t_min
            tamper_max = t_max

        verify_ms, is_intact = measure_verify(original_root, tampered_logs, hash_fn)
        verify_times.append(verify_ms)

        if not is_intact:
            detect_count += 1

    return {
        "algorithm":               algo_name,
        "log_size":                size_label,
        "entry_count":             len(logs),
        "tamper_position":         tamper_pos,
        "build_time_ms":           round(sum(build_times)  / REPEAT, 4),
        "verify_time_ms":          round(sum(verify_times) / REPEAT, 4),
        "throughput_eps":          round(sum(throughputs)  / REPEAT, 2),
        "detection_accuracy_pct":  round((detect_count / REPEAT) * 100, 2),
        "memory_peak_kb":          round(sum(memory_kbs)   / REPEAT, 4),
        "hash_time_us":            round(hash_time_us, 6),
        "merkle_proof_length":     proof_length,
        "tamper_node_avg":         round(sum(tamper_indices) / len(tamper_indices)),
        "tamper_node_min":         min(tamper_indices),
        "tamper_node_max":         max(tamper_indices),
        "tamper_range_defined_min": tamper_min,
        "tamper_range_defined_max": tamper_max,
        "repeat":                  REPEAT,
    }


# ── Main ──────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output_folder = get_experiment_folder()
    log_sizes     = get_log_sizes()
    all_results   = []

    print("[MERKLE-ENGINE] Starting Merkle Tree evaluation...")
    print(f"[MERKLE-ENGINE] Tamper randomization: ±{RANDOM_RANGE_PCT * 100:.0f}% of position")
    print("=" * 75)

    for size_label in log_sizes:
        log_path = os.path.join(DATA_DIR, f"logs_{size_label}.json")
        if not os.path.exists(log_path):
            print(f"[MERKLE-ENGINE] WARNING: {log_path} not found, skipping.")
            continue

        with open(log_path, "r") as f:
            logs = json.load(f)

        proof_len = get_merkle_proof_length(len(logs))
        print(f"\n[MERKLE-ENGINE] Size: {size_label} | Entries: {len(logs):,} | Proof length: {proof_len} steps")

        for algo_name, hash_fn in ENGINES.items():
            for tamper_pos in TAMPERING_POSITIONS:
                result = run_scenario(logs, algo_name, hash_fn, size_label, tamper_pos)
                all_results.append(result)

                if tamper_pos == "first":
                    pos_info = "node 0 (fixed)"
                else:
                    pos_info = (
                        f"node {result['tamper_node_avg']} "
                        f"(range {result['tamper_range_defined_min']}–{result['tamper_range_defined_max']}, "
                        f"actual min={result['tamper_node_min']} max={result['tamper_node_max']})"
                    )

                print(
                    f"  {algo_name} | {tamper_pos:<8} | "
                    f"build={result['build_time_ms']:>9.2f}ms | "
                    f"verify={result['verify_time_ms']:>9.2f}ms | "
                    f"hash={result['hash_time_us']:>7.3f}µs | "
                    f"proof={result['merkle_proof_length']} | "
                    f"acc={result['detection_accuracy_pct']}% | "
                    f"tamper→ {pos_info}"
                )

    print("\n" + "=" * 75)
    save_results(all_results, output_folder)
    print(f"[MERKLE-ENGINE] Done. Results at: {output_folder}")


if __name__ == "__main__":
    main()
