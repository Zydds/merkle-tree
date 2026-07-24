RESULTS_DIR = "/app/results"

COLORS = {
    "SHA256": "#2196F3",
    "BLAKE3": "#FF9800",
}

SIZE_ORDER = ["small", "medium", "large"]

TAMPER_ORDER = ["first", "middle", "last"]

TAMPER_LABELS = {
    "first":  "Awal (First)",
    "middle": "Tengah (Middle)",
    "last":   "Akhir (Last)",
}

METRICS = {
    "build_time_ms":          "Waktu Build (ms)",
    "verify_time_ms":         "Waktu Verifikasi (ms)",
    "throughput_eps":         "Throughput (entri/detik)",
    "detection_accuracy_pct": "Akurasi Deteksi (%)",
    "memory_peak_kb":         "Peak Memory (KB)",
    "hash_time_us":           "Kecepatan Hash per Entri (µs)",
}
