import os
import json
import pandas as pd
from scipy import stats

from config import RESULTS_DIR, METRICS, SIZE_ORDER
from charts import (
    plot_by_size, plot_by_tamper,
    plot_throughput_line, plot_memory,
    plot_hash_time, plot_proof_length,
    plot_tamper_positions,
)


def get_latest_experiment():
    folders = [
        d for d in os.listdir(RESULTS_DIR)
        if d.startswith("experiment") and os.path.isdir(os.path.join(RESULTS_DIR, d))
    ]
    if not folders:
        raise FileNotFoundError("[ANALYSIS] No experiment folder found.")
    folders.sort(key=lambda x: int(x.replace("experiment", "")))
    latest = os.path.join(RESULTS_DIR, folders[-1])
    print(f"[ANALYSIS] Using: {latest}")
    return latest


def load_results(folder):
    path = os.path.join(folder, "results_raw.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ANALYSIS] results_raw.csv not found in {folder}")
    df = pd.read_csv(path)

    meta = {}
    meta_path = os.path.join(folder, "experiment_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)

    print(f"[ANALYSIS] Loaded {len(df)} rows.")
    return df, meta


def generate_summaries(df, folder):
    s1 = df.groupby(["algorithm", "log_size"]).agg(
        entry_count           =("entry_count",             "first"),
        avg_build_ms          =("build_time_ms",           "mean"),
        avg_verify_ms         =("verify_time_ms",          "mean"),
        avg_throughput_eps    =("throughput_eps",          "mean"),
        avg_accuracy_pct      =("detection_accuracy_pct",  "mean"),
        avg_memory_peak_kb    =("memory_peak_kb",          "mean"),
        avg_hash_time_us      =("hash_time_us",            "mean"),
        merkle_proof_length   =("merkle_proof_length",     "first"),
    ).round(4).reset_index()

    p1 = os.path.join(folder, "summary_by_size.csv")
    s1.to_csv(p1, index=False)
    print(f"[ANALYSIS] Saved: {p1}")

    s2 = df.groupby(["algorithm", "log_size", "tamper_position"]).agg(
        avg_verify_ms         =("verify_time_ms",          "mean"),
        avg_accuracy_pct      =("detection_accuracy_pct",  "mean"),
        tamper_node_avg       =("tamper_node_avg",         "mean"),
        tamper_node_min       =("tamper_node_min",         "min"),
        tamper_node_max       =("tamper_node_max",         "max"),
        tamper_range_min      =("tamper_range_defined_min","first"),
        tamper_range_max      =("tamper_range_defined_max","first"),
        entry_count           =("entry_count",             "first"),
    ).round(2).reset_index()

    p2 = os.path.join(folder, "summary_by_tamper.csv")
    s2.to_csv(p2, index=False)
    print(f"[ANALYSIS] Saved: {p2}")

    return s1, s2


def statistical_test(df, folder):
    sha_df   = df[df["algorithm"] == "SHA256"]
    blake_df = df[df["algorithm"] == "BLAKE3"]
    rows     = []

    for col, label in METRICS.items():
        if col not in df.columns:
            continue
        t_stat, p_value = stats.ttest_ind(
            sha_df[col].dropna(),
            blake_df[col].dropna(),
        )
        rows.append({
            "metric":      label,
            "sha256_mean": round(sha_df[col].mean(), 6),
            "blake3_mean": round(blake_df[col].mean(), 6),
            "t_statistic": round(t_stat, 4),
            "p_value":     round(p_value, 6),
            "significant": "Ya" if p_value < 0.05 else "Tidak",
        })

    result_df = pd.DataFrame(rows)
    path = os.path.join(folder, "statistical_test.csv")
    result_df.to_csv(path, index=False)
    print(f"[ANALYSIS] Saved: {path}")
    print("\n[ANALYSIS] Statistical Test Results:")
    print(result_df.to_string(index=False))


def export_excel(df, folder):
    path = os.path.join(folder, "hasil_penelitian.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Raw Data", index=False)

        df.groupby(["algorithm", "log_size"]).mean(numeric_only=True).reset_index()\
          .to_excel(writer, sheet_name="Summary by Size", index=False)

        df.groupby(["algorithm", "tamper_position"]).mean(numeric_only=True).reset_index()\
          .to_excel(writer, sheet_name="Summary by Tamper", index=False)

        df[[
            "algorithm", "log_size", "entry_count", "tamper_position",
            "tamper_node_avg", "tamper_node_min", "tamper_node_max",
            "tamper_range_defined_min", "tamper_range_defined_max",
        ]].to_excel(writer, sheet_name="Tamper Positions", index=False)

    print(f"[ANALYSIS] Saved: {path}")


def main():
    folder = get_latest_experiment()
    df, meta = load_results(folder)

    print("\n[ANALYSIS] Generating summaries...")
    generate_summaries(df, folder)

    print("\n[ANALYSIS] Generating charts...")
    plot_by_size(df, folder, "build_time_ms", "Waktu (ms)",
                 "Perbandingan Waktu Build SHA-256 vs BLAKE3", "chart_build_time.png")
    plot_by_size(df, folder, "verify_time_ms", "Waktu (ms)",
                 "Perbandingan Waktu Verifikasi SHA-256 vs BLAKE3", "chart_verify_time.png")
    plot_by_size(df, folder, "detection_accuracy_pct", "Akurasi (%)",
                 "Perbandingan Akurasi Deteksi SHA-256 vs BLAKE3", "chart_accuracy_by_size.png")
    plot_throughput_line(df, folder)
    plot_memory(df, folder)
    plot_by_tamper(df, folder, "verify_time_ms", "Waktu (ms)",
                   "Waktu Verifikasi per Posisi Tampering", "chart_verify_by_tamper.png")
    plot_by_tamper(df, folder, "detection_accuracy_pct", "Akurasi (%)",
                   "Akurasi Deteksi per Posisi Tampering", "chart_accuracy_by_tamper.png")
    plot_hash_time(df, folder)
    plot_proof_length(df, folder)
    plot_tamper_positions(df, folder)

    print("\n[ANALYSIS] Running statistical tests...")
    statistical_test(df, folder)

    print("\n[ANALYSIS] Exporting to Excel...")
    export_excel(df, folder)

    print("\n" + "=" * 65)
    print("[ANALYSIS] All outputs generated successfully.")
    print(f"[ANALYSIS] Results at: {folder}")


if __name__ == "__main__":
    main()
