import json
import math
import random
import time
import tracemalloc
from copy import deepcopy
from typing import Callable

RANDOM_RANGE_PCT = 0.02


# ── Merkle Tree ───────────────────────────────────────────────

def hash_entry(entry: dict, hash_fn: Callable) -> str:
    return hash_fn(json.dumps(entry, sort_keys=True))


def build_merkle_tree(leaves: list, hash_fn: Callable) -> list:
    if not leaves:
        return []
    tree    = [leaves]
    current = leaves
    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left   = current[i]
            right  = current[i + 1] if i + 1 < len(current) else current[i]
            parent = hash_fn(left + right)
            next_level.append(parent)
        tree.append(next_level)
        current = next_level
    return tree


def get_merkle_root(tree: list) -> str | None:
    return tree[-1][0] if tree else None


def get_merkle_proof_length(total_entries: int) -> int:
    if total_entries <= 1:
        return 0
    return math.ceil(math.log2(total_entries))


def verify_integrity(original_root: str, logs: list, hash_fn: Callable) -> bool:
    leaves   = [hash_entry(e, hash_fn) for e in logs]
    tree     = build_merkle_tree(leaves, hash_fn)
    new_root = get_merkle_root(tree)
    return new_root == original_root


# ── Tampering ─────────────────────────────────────────────────

def resolve_tamper_index(logs: list, position: str) -> tuple[int, int, int]:
    total  = len(logs)
    margin = max(1, int(total * RANDOM_RANGE_PCT))

    if position == "first":
        return 0, 0, 0

    if position == "middle":
        center  = total // 2
        idx_min = max(0, center - margin)
        idx_max = min(total - 1, center + margin)
    else:
        idx_min = max(0, total - 1 - margin)
        idx_max = total - 1

    idx = random.randint(idx_min, idx_max)
    return idx, idx_min, idx_max


def tamper_log(logs: list, position: str) -> tuple[list, int, int, int]:
    tampered              = deepcopy(logs)
    idx, idx_min, idx_max = resolve_tamper_index(logs, position)

    tampered[idx]["eventName"]    = "UNAUTHORIZED_ACCESS"
    tampered[idx]["errorCode"]    = "TAMPERED"
    tampered[idx]["errorMessage"] = "** LOG ENTRY TAMPERED **"
    tampered[idx]["_tampered"]    = True

    return tampered, idx, idx_min, idx_max


# ── Pengukuran Metrik ─────────────────────────────────────────

def measure_hash_computation(logs: list, hash_fn: Callable, sample_size: int = 500) -> float:
    sample     = logs[:min(sample_size, len(logs))]
    serialized = [json.dumps(e, sort_keys=True) for e in sample]

    warmup_n = min(10, len(serialized))
    for s in serialized[:warmup_n]:
        hash_fn(s)

    start = time.perf_counter()
    for s in serialized:
        hash_fn(s)
    end = time.perf_counter()

    elapsed_us = ((end - start) / len(sample)) * 1_000_000
    return round(elapsed_us, 6)


def measure_build(logs: list, hash_fn: Callable) -> tuple[float, float, list]:
    tracemalloc.start()
    mem_before = tracemalloc.get_traced_memory()[0]

    t_start = time.perf_counter()
    leaves  = [hash_entry(e, hash_fn) for e in logs]
    tree    = build_merkle_tree(leaves, hash_fn)
    t_end   = time.perf_counter()

    _, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    build_time_ms = (t_end - t_start) * 1000
    memory_kb     = (mem_peak - mem_before) / 1024
    return build_time_ms, memory_kb, tree


def measure_verify(original_root: str, logs: list, hash_fn: Callable) -> tuple[float, bool]:
    t_start   = time.perf_counter()
    is_intact = verify_integrity(original_root, logs, hash_fn)
    t_end     = time.perf_counter()
    return (t_end - t_start) * 1000, is_intact


def calc_throughput(entry_count: int, build_time_ms: float) -> float:
    build_sec = build_time_ms / 1000
    return entry_count / build_sec if build_sec > 0 else 0
