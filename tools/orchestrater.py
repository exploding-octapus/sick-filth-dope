#!/usr/bin/env python3
"""
orchestrator.py

Read an experiment manifest (YAML), run a simulated or real capture pipeline,
and save structured outputs (IQ, PSD snapshots, waterfall images, metadata).

Usage:
  python3 tools/orchestrator.py --manifest experiments/manifests/example_manifest.yaml
"""
import argparse
import os
import yaml
import json
import subprocess
from datetime import datetime
import numpy as np

# Local helper imports (kept minimal so repo can be portable)
SIM_GEN = "tools/simulated_iq_generator.py"

def load_manifest(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def run_simulated_generator(manifest, out_iq):
    # Build command from manifest stimulus parameters
    st = manifest.get("stimulus", {})
    tones = st.get("tones", [])
    tones_arg = ",".join(f"{int(t['freq_hz'])}:{t.get('amp',1.0)}" for t in tones)
    noise = st.get("noise_sigma", 0.0)
    burst = None
    b = st.get("burst", {})
    if b:
        burst = f"{b.get('start_s',0)}:{b.get('duration_s',0.05)}:{b.get('burst_rate_hz',5000)}"
    cmd = [
        "python3", SIM_GEN,
        "--duration", str(manifest["capture_parameters"]["duration_s"]),
        "--samplerate", str(manifest["capture_parameters"]["samplerate_hz"]),
        "--tones", tones_arg,
        "--noise", str(noise),
        "--out", out_iq,
        "--seed", str(manifest.get("created_at", "") .__hash__() & 0xffffffff)
    ]
    if burst:
        cmd += ["--burst", burst]
    # Simulated mode: call generator and wait
    subprocess.check_call(cmd)
    return out_iq

def save_metadata(out_dir, manifest, note):
    meta = {
        "manifest": manifest,
        "run_at": datetime.utcnow().isoformat() + "Z",
        "note": note
    }
    with open(os.path.join(out_dir, "run_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--outdir", default="runs")
    args = p.parse_args()

    manifest = load_manifest(args.manifest)
    run_id = manifest.get("experiment_id", "run") + "_" + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(args.outdir, run_id)
    ensure_dir(out_dir)

    # Safety: refuse to run non-simulated captures without explicit override env var
    mode = manifest["capture_parameters"].get("mode", "simulated")
    if mode != "simulated" and os.getenv("ALLOW_REAL_CAPTURE", "0") != "1":
        print("[!] Manifest mode is not 'simulated'. Set ALLOW_REAL_CAPTURE=1 environment variable to proceed with real hardware captures.")
        return

    # Generate or capture IQ
    iq_path = os.path.join(out_dir, manifest["stimulus"].get("simulated_iq_file", "capture.iq"))
    if manifest["capture_parameters"].get("mode") == "simulated":
        print(f"[+] Running simulated generator to produce IQ -> {iq_path}")
        run_simulated_generator(manifest, iq_path)
    else:
        # Placeholder for real capture integration (SDR libs). Not implemented by default.
        raise NotImplementedError("Real SDR capture not implemented in this orchestrator. Use simulated mode or add your capture adapter.")

    # Copy/record metadata
    # Copy generator metadata sidecar if exists
    gen_meta = iq_path + ".meta.json"
    if os.path.exists(gen_meta):
        subprocess.check_call(["cp", gen_meta, out_dir])

    save_metadata(out_dir, manifest, "Simulated run completed. No over-air transmissions performed.")

    print(f"[+] Run outputs saved in {out_dir}")
    print("[!] Reminder: this run used simulated IQ; do not transmit these files over the air outside of shielded, authorized environments.")

if __name__ == "__main__":
    main()