import mmap
import sys
import time
from typing import Tuple

import numpy as np


class MicroFlowClient:
    """Cliente de evaluación para MicroFlow-L2 Demo (BTC/ETH, 4 Features)."""

    def __init__(self) -> None:
        self._shm_file = None

        self._symbols: list[str] = ["btcusdt", "ethusdt"]
        self._active_features: list[str] = [
            "mid_price",
            "wobi",
            "fast_ofi",
            "flow_toxicity",
        ]

        self._symbol_to_idx: dict[str, int] = {
            s: i for i, s in enumerate(self._symbols)
        }
        self._feature_to_idx: dict[str, int] = {
            f: i for i, f in enumerate(self._active_features)
        }

        self._num_features = len(self._active_features)
        self._num_symbols = len(self._symbols)
        self._capacity = 64
        self._header_size = 64
        self._total_bytes = self._header_size + (
            self._num_features * self._capacity * 8
        )

        shm_name = (
            "Local\\microflow_shm"
            if sys.platform == "win32"
            else "/dev/shm/microflow_shm"
        )

        try:
            if sys.platform == "win32":
                self._mm = mmap.mmap(
                    -1, self._total_bytes, tagname=shm_name, access=mmap.ACCESS_READ
                )
            else:
                self._shm_file = open(shm_name, "r+b")
                self._mm = mmap.mmap(
                    self._shm_file.fileno(),
                    self._total_bytes,
                    access=mmap.ACCESS_READ,
                )
        except Exception as e:
            raise RuntimeError(
                f"[DEMO OFFLINE] Could not map '{shm_name}'. Ensure FuturesMicrostructureEngine_demo.exe is running.\nDetails: {e}"
            ) from e

        cpp_active_symbols = int(
            np.frombuffer(self._mm, dtype=np.uint32, count=1, offset=8)[0]
        )
        cpp_num_features = int(
            np.frombuffer(self._mm, dtype=np.uint32, count=1, offset=12)[0]
        )

        if (
            cpp_num_features != self._num_features
            or cpp_active_symbols != self._num_symbols
        ):
            raise ValueError(
                f"[MISMATCH] C++ engine exported ({cpp_active_symbols} syms, {cpp_num_features} feats). "
                f"Demo expects ({self._num_symbols} syms, {self._num_features} feats)."
            )

        layout_str = ",".join(self._symbols) + ";" + ",".join(
            self._active_features
        )
        fnv_prime = 0x100000001B3
        layout_hash = 14695981039346656037
        for b in layout_str.encode("utf-8"):
            layout_hash ^= b
            layout_hash = (layout_hash * fnv_prime) & 0xFFFFFFFFFFFFFFFF

        cpp_layout_hash = int(
            np.frombuffer(self._mm, dtype=np.uint64, count=1, offset=32)[0]
        )
        if cpp_layout_hash != layout_hash:
            raise ValueError(
                f"[LAYOUT MISMATCH] Engine hash {hex(cpp_layout_hash)} != client hash {hex(layout_hash)}."
            )

        self._matrix_view = np.ndarray(
            shape=(self._num_features, self._capacity),
            dtype=np.float64,
            buffer=self._mm,
            offset=self._header_size,
        )

        self._seq_array = np.ndarray(
            (1,), dtype=np.uint64, buffer=self._mm, offset=0
        )
        self._last_warn_time = 0.0

    def snapshot(self, retries: int = 1000) -> Tuple[int, np.ndarray]:
        for _ in range(retries):
            s1 = int(self._seq_array[0])
            if (s1 & 1) != 0:
                continue

            safe_data = self._matrix_view.copy()
            s2 = int(self._seq_array[0])

            if s1 == s2:
                return s1, safe_data

        raise TimeoutError("[RETRY] Seqlock read retry limit reached.")

    def heartbeat_age_ms(self) -> float:
        heartbeat_ms = float(
            np.frombuffer(self._mm, dtype=np.float64, count=1, offset=24)[0]
        )
        if heartbeat_ms <= 0.0:
            return float("inf")
        return (time.time() * 1000.0) - heartbeat_ms

    def is_healthy(self, max_lag_ms: float = 1500.0) -> bool:
        return self.heartbeat_age_ms() <= max_lag_ms

    def get_active_features(self) -> list[str]:
        return self._active_features

    def get_symbols(self) -> list[str]:
        return self._symbols

    def close(self) -> None:
        if hasattr(self, "_matrix_view"):
            del self._matrix_view
        if hasattr(self, "_seq_array"):
            del self._seq_array
        if hasattr(self, "_mm") and self._mm:
            self._mm.close()
        if self._shm_file:
            self._shm_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()