import hashlib
import blake3 as blake3_lib


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def blake3(data: str) -> str:
    return blake3_lib.blake3(data.encode()).hexdigest()


ENGINES = {
    "SHA256": sha256,
    "BLAKE3": blake3,
}
