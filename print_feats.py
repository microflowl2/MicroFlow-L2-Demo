import os
import time

from client import MicroFlowClient


def main():
    print("[DEMO] Starting MicroFlow-L2 evaluation inspector...\n")

    try:
        client = MicroFlowClient()
    except Exception as e:
        print(f"[FATAL] Could not attach to engine: {e}")
        return

    symbols = client.get_symbols()
    features = client.get_active_features()
    last_seq = 0

    try:
        while True:
            if not client.is_healthy(max_lag_ms=1500.0):
                print(
                    f"[STALE] Engine offline or 15-min timeout reached (Lag: {client.heartbeat_age_ms():.1f} ms)"
                )
                time.sleep(1.0)
                continue

            try:
                seq, matrix = client.snapshot()
                if seq != last_seq:
                    last_seq = seq
                    os.system("cls" if os.name == "nt" else "clear")

                    print("==================================================")
                    print(
                        f"   MicroFlow-L2 EVALUATION DEMO  (Seq: {seq:<6})    "
                    )
                    print("==================================================")

                    for feat_idx, feat_name in enumerate(features):
                        btc_val = matrix[feat_idx, 0]
                        eth_val = matrix[feat_idx, 1]
                        print(
                            f" {feat_name:<16} : BTC [{btc_val:12.4f}] | ETH [{eth_val:12.4f}]"
                        )

                    print("--------------------------------------------------")
                    print(" Session timer: Max 15 minutes. Press Ctrl+C to exit.")
                    print("==================================================")

            except TimeoutError:
                pass

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n[DEMO] Inspector stopped.")
    finally:
        client.close()


if __name__ == "__main__":
    main()