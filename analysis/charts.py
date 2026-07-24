import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from config import COLORS, SIZE_ORDER, TAMPER_ORDER, TAMPER_LABELS


def get_size_labels(df):
    labels = {}
    for size in SIZE_ORDER:
        subset = df[df["log_size"] == size]
        if not subset.empty:
            count = int(subset["entry_count"].iloc[0])
            labels[size] = f"{count:,}"
    return labels


def save_fig(folder, filename):
    path = os.path.join(folder, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[ANALYSIS] Saved: {path}")


def _bar_chart(df, folder, metric, ylabel, title, filename, group_col, group_order, group_labels, fmt=".3f"):
    valid = [g for g in group_order if g in df[group_col].values]
    fig, ax = plt.subplots(figsize=(9, 5))
    x, width = range(len(valid)), 0.35

    for i, (algo, color) in enumerate(COLORS.items()):
        vals = [
            df[(df["algorithm"] == algo) & (df[group_col] == g)][metric].mean()
            if not df[(df["algorithm"] == algo) & (df[group_col] == g)].empty else 0
            for g in valid
        ]
        offset = -width / 2 if i == 0 else width / 2
        bars = ax.bar([xi + offset for xi in x], vals, width,
                      label=algo, color=color, alpha=0.85, edgecolor="white")
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                    f"{h:,{fmt}}", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel(ylabel.split("(")[0].strip(), fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels([group_labels[g] for g in valid])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,{fmt}}"))
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    save_fig(folder, filename)


def plot_by_size(df, folder, metric, ylabel, title, filename):
    size_labels = get_size_labels(df)
    _bar_chart(df, folder, metric, ylabel, title, filename,
               group_col="log_size", group_order=SIZE_ORDER, group_labels=size_labels)


def plot_by_tamper(df, folder, metric, ylabel, title, filename):
    _bar_chart(df, folder, metric, ylabel, title, filename,
               group_col="tamper_position", group_order=TAMPER_ORDER, group_labels=TAMPER_LABELS)


def plot_throughput_line(df, folder):
    size_labels = get_size_labels(df)
    valid_sizes = [s for s in SIZE_ORDER if s in size_labels]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = list(range(len(valid_sizes)))

    for algo, color in COLORS.items():
        vals = [
            df[(df["algorithm"] == algo) & (df["log_size"] == s)]["throughput_eps"].mean()
            if not df[(df["algorithm"] == algo) & (df["log_size"] == s)].empty else 0
            for s in valid_sizes
        ]
        ax.plot(x, vals, marker="o", label=algo, color=color, linewidth=2.5)
        for xi, v in zip(x, vals):
            ax.text(xi, v * 1.015, f"{v:,.0f}", ha="center", fontsize=8)

    ax.set_xlabel("Jumlah Entri Log", fontsize=11)
    ax.set_ylabel("Throughput (entri/detik)", fontsize=11)
    ax.set_title("Perbandingan Throughput SHA-256 vs BLAKE3", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([size_labels[s] for s in valid_sizes])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.legend()
    ax.grid(linestyle="--", alpha=0.4)
    plt.tight_layout()
    save_fig(folder, "chart_throughput_line.png")


def plot_memory(df, folder):
    size_labels = get_size_labels(df)
    valid_sizes = [s for s in SIZE_ORDER if s in size_labels]

    fig, ax = plt.subplots(figsize=(9, 5))
    x, width = range(len(valid_sizes)), 0.35

    for i, (algo, color) in enumerate(COLORS.items()):
        vals = [
            df[(df["algorithm"] == algo) & (df["log_size"] == s)]["memory_peak_kb"].mean()
            if not df[(df["algorithm"] == algo) & (df["log_size"] == s)].empty else 0
            for s in valid_sizes
        ]
        offset = -width / 2 if i == 0 else width / 2
        bars = ax.bar([xi + offset for xi in x], vals, width,
                      label=algo, color=color, alpha=0.85, edgecolor="white")
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                    f"{h:,.1f}", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Jumlah Entri Log", fontsize=11)
    ax.set_ylabel("Peak Memory (KB)", fontsize=11)
    ax.set_title("Perbandingan Penggunaan Memori SHA-256 vs BLAKE3", fontsize=12, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels([size_labels[s] for s in valid_sizes])
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    save_fig(folder, "chart_memory.png")


def plot_hash_time(df, folder):
    size_labels = get_size_labels(df)
    valid_sizes = [s for s in SIZE_ORDER if s in size_labels]

    fig, ax = plt.subplots(figsize=(9, 5))
    x, width = range(len(valid_sizes)), 0.35

    for i, (algo, color) in enumerate(COLORS.items()):
        vals = [
            df[(df["algorithm"] == algo) & (df["log_size"] == s)]["hash_time_us"].mean()
            if not df[(df["algorithm"] == algo) & (df["log_size"] == s)].empty else 0
            for s in valid_sizes
        ]
        offset = -width / 2 if i == 0 else width / 2
        bars = ax.bar([xi + offset for xi in x], vals, width,
                      label=algo, color=color, alpha=0.85, edgecolor="white")
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                    f"{h:.4f}", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Jumlah Entri Log", fontsize=11)
    ax.set_ylabel("Waktu Hash per Entri (µs)", fontsize=11)
    ax.set_title(
        "Perbandingan Kecepatan Komputasi Hash SHA-256 vs BLAKE3\n(per entri log, dalam mikrodetik — lebih kecil = lebih cepat)",
        fontsize=11, fontweight="bold"
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels([size_labels[s] for s in valid_sizes])
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    save_fig(folder, "chart_hash_time_us.png")


def plot_proof_length(df, folder):
    size_labels = get_size_labels(df)
    valid_sizes = [s for s in SIZE_ORDER if s in size_labels]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = list(range(len(valid_sizes)))

    for algo, color in COLORS.items():
        vals = [
            int(df[(df["algorithm"] == algo) & (df["log_size"] == s)]["merkle_proof_length"].iloc[0])
            if not df[(df["algorithm"] == algo) & (df["log_size"] == s)].empty else 0
            for s in valid_sizes
        ]
        ax.plot(x, vals, marker="s", label=algo, color=color, linewidth=2, linestyle="--")
        for xi, v in zip(x, vals):
            ax.text(xi, v + 0.05, str(v), ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_xlabel("Jumlah Entri Log", fontsize=11)
    ax.set_ylabel("Merkle Proof Length (langkah)", fontsize=11)
    ax.set_title(
        "Merkle Proof Length per Ukuran Log\n(jumlah langkah dari leaf ke root = ⌈log₂(n)⌉)",
        fontsize=11, fontweight="bold"
    )
    ax.set_xticks(x)
    ax.set_xticklabels([size_labels[s] for s in valid_sizes])
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.legend()
    ax.grid(linestyle="--", alpha=0.4)
    plt.tight_layout()
    save_fig(folder, "chart_proof_length.png")


def plot_tamper_positions(df, folder):
    df_ml = df[df["tamper_position"].isin(["middle", "last"])].copy()
    if df_ml.empty:
        return

    size_labels = get_size_labels(df)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, pos in zip(axes, ["middle", "last"]):
        df_pos = df_ml[df_ml["tamper_position"] == pos]
        for algo, color in COLORS.items():
            df_algo = df_pos[df_pos["algorithm"] == algo]
            if df_algo.empty:
                continue
            sizes  = df_algo["log_size"].tolist()
            avgs   = df_algo["tamper_node_avg"].tolist()
            mins   = df_algo["tamper_node_min"].tolist()
            maxs   = df_algo["tamper_node_max"].tolist()
            counts = df_algo["entry_count"].tolist()
            x_pos  = range(len(sizes))

            ax.scatter(x_pos, [a / c * 100 for a, c in zip(avgs, counts)],
                       color=color, label=algo, zorder=5, s=60)
            for xi, mn, mx, c in zip(x_pos, mins, maxs, counts):
                ax.plot([xi, xi], [mn / c * 100, mx / c * 100],
                        color=color, linewidth=3, alpha=0.4)

        valid_sizes = [s for s in SIZE_ORDER if s in size_labels]
        ax.set_title(f"Distribusi Posisi Tampering — {TAMPER_LABELS[pos]}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Ukuran Log", fontsize=10)
        ax.set_ylabel("Posisi (% dari total entri)", fontsize=10)
        ax.set_xticks(list(range(len(valid_sizes))))
        ax.set_xticklabels([size_labels[s] for s in valid_sizes])
        ax.legend()
        ax.grid(linestyle="--", alpha=0.4)

    plt.tight_layout()
    save_fig(folder, "chart_tamper_positions.png")
