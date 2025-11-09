#!/usr/bin/env python3
"""
rf_survey.py
Benign local RF survey tool (SDR). Logs spectral snapshots and metadata.
Requires: pyrtlsdr or your preferred SDR library and numpy/scipy/matplotlib for optional plotting.
"""

import os
import time
import json
from datetime import datetime

# CONFIG: adjust per lab equipment
OUTPUT_DIR = "survey_logs"
DEVICE_ID = "device-under-test-serial"  # replace with local identifier you set
FREQ_START_HZ = 1e6   # 1 MHz
FREQ_END_HZ = 6e9     # 6 GHz (adjust for equipment)
NUM_BINS = 1024
SNAPSHOT_INTERVAL_SEC = 10
NUM_SNAPSHOTS = 6

os.makedirs(OUTPUT_DIR, exist_ok=True)

def take_snapshot(index):
    # Placeholder: Replace with actual SDR acquisition code
    # e.g., use pyrtlsdr to read IQ samples, compute PSD, and save magnitudes
    # Here we simulate a fake spectrum for template purposes
    import numpy as np
    freqs = np.linspace(FREQ_START_HZ, FREQ_END_HZ, NUM_BINS)
    magnitudes_db = -120 + 20 * np.log10(np.abs(np.sin(2 * np.pi * freqs / 1e8)) + 1)
    ts = datetime.utcnow().isoformat() + "Z"
    fname = f"{OUTPUT_DIR}/snapshot_{index}_{int(time.time())}.json"
    payload = {
        "timestamp": ts,
        "device_id": DEVICE_ID,
        "freq_start_hz": FREQ_START_HZ,
        "freq_end_hz": FREQ_END_HZ,
        "num_bins": NUM_BINS,
        "magnitudes_db": magnitudes_db.tolist(),
    }
    with open(fname, "w") as f:
        json.dump(payload, f)
    print(f"[+] Saved snapshot: {fname}")

def main():
    metadata = {
        "run_started": datetime.utcnow().isoformat() + "Z",
        "device_id": DEVICE_ID,
        "notes": "Local benign RF survey; do not use for transmission or remote activation"
    }
    with open(f"{OUTPUT_DIR}/run_metadata_{int(time.time())}.json", "w") as f:
        json.dump(metadata, f)

    for i in range(NUM_SNAPSHOTS):
        take_snapshot(i)
        time.sleep(SNAPSHOT_INTERVAL_SEC)

    print("[+] Survey complete. Remember: anonymize before publishing.")

if __name__ == "__main__":
    main()