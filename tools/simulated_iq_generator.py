#!/usr/bin/env python3
"""
simulated_iq_generator.py

Generate reproducible simulated IQ captures for a safe lab simulator.
Outputs either an interleaved float32 IQ file (*.iq) or a NumPy file (*.npy)
and a small JSON metadata sidecar.

Usage examples
- Generate a 5 second capture with two tones + noise:
  python3 simulated_iq_generator.py --duration 5 --samplerate 2e6 --tones 100e3:0.8,300e3:0.5 --noise 0.01 --out capture.iq

- Generate a short bursty capture for testing near-field hotspots:
  python3 simulated_iq_generator.py --duration 2 --samplerate 1e6 --burst 0.2:0.05:5 --out burst_capture.npy
"""
import argparse
import json
import numpy as np
from datetime import datetime
import os

def mk_tone(freq, amp, samplerate, t):
    return amp * np.exp(2j * np.pi * freq * t)

def mk_noise(sigma, size):
    return (sigma * (np.random.normal(size=size) + 1j * np.random.normal(size=size))).astype(np.complex64)

def mk_burst(t, samplerate, burst_start, burst_dur, burst_rate, tone_freq=0.0, amp=1.0):
    start_idx = int(burst_start * samplerate)
    dur_idx = int(burst_dur * samplerate)
    burst = np.zeros(len(t), dtype=np.complex64)
    if start_idx < len(t):
        end_idx = min(len(t), start_idx + dur_idx)
        tt = t[start_idx:end_idx]
        if tone_freq == 0.0:
            burst[start_idx:end_idx] = amp * (np.exp(2j * np.pi * burst_rate * tt))
        else:
            burst[start_idx:end_idx] = mk_tone(tone_freq, amp, samplerate, tt)
    return burst

def parse_tones(specs):
    out = []
    if not specs:
        return out
    for s in specs.split(','):
        if not s:
            continue
        parts = s.split(':')
        freq = float(parts[0])
        amp = float(parts[1]) if len(parts) > 1 else 1.0
        out.append((freq, amp))
    return out

def main():
    p = argparse.ArgumentParser(description="Simulated IQ generator for safe lab simulator")
    p.add_argument('--duration', type=float, default=5.0, help='seconds')
    p.add_argument('--samplerate', type=float, default=2e6, help='Hz')
    p.add_argument('--tones', type=str, default='', help='comma separated list freq:amp e.g. 100e3:0.8,300e3:0.5')
    p.add_argument('--noise', type=float, default=0.0, help='noise sigma (complex)')
    p.add_argument('--burst', type=str, default='', help='burst_start:burst_dur:burst_rate e.g. 0.2:0.05:5  (Hz)')
    p.add_argument('--out', required=True, help='output filename (.iq or .npy)')
    p.add_argument('--seed', type=int, default=42, help='random seed for reproducibility')
    args = p.parse_args()

    np.random.seed(int(args.seed))
    sr = float(args.samplerate)
    n = int(np.ceil(args.duration * sr))
    t = np.arange(n) / sr
    iq = np.zeros(n, dtype=np.complex64)

    tones = parse_tones(args.tones)
    for freq, amp in tones:
        iq += mk_tone(freq, amp, sr, t).astype(np.complex64)

    if args.noise and args.noise > 0:
        iq += mk_noise(args.noise, n)

    if args.burst:
        burst_parts = args.burst.split(':')
        if len(burst_parts) >= 3:
            burst_start = float(burst_parts[0])
            burst_dur = float(burst_parts[1])
            burst_rate = float(burst_parts[2])
            iq += mk_burst(t, sr, burst_start, burst_dur, burst_rate)
        else:
            print("Burst spec must be burst_start:burst_dur:burst_rate")

    # small amplitude limiter to avoid extreme values in float32
    max_amp = np.max(np.abs(iq)) if np.any(iq) else 1.0
    if max_amp > 1.0:
        iq = iq / max_amp

    out = args.out
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    meta = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "duration_s": args.duration,
        "samplerate_hz": sr,
        "tones": [{"freq_hz": f, "amp": a} for f, a in tones],
        "noise_sigma": args.noise,
        "burst_spec": args.burst,
        "seed": int(args.seed),
        "file": os.path.basename(out),
        "note": "Simulated IQ for safe, in-cage or offline analysis only. Do not transmit."
    }

    if out.endswith('.npy'):
        np.save(out, iq.view(np.complex64))
    else:
        # write interleaved float32 IQ I,Q,I,Q,...
        iq_i = np.real(iq).astype(np.float32)
        iq_q = np.imag(iq).astype(np.float32)
        interleaved = np.empty(iq_i.size + iq_q.size, dtype=np.float32)
        interleaved[0::2] = iq_i
        interleaved[1::2] = iq_q
        interleaved.tofile(out)

    meta_path = out + '.meta.json'
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"[+] Wrote {out} and metadata {meta_path}")
    print(f"[+] Preview: tones={meta['tones']}, noise_sigma={meta['noise_sigma']}, burst={meta['burst_spec']}")
    print("[!] Reminder: this is simulated IQ data for contained lab use only")
    
if __name__ == "__main__":
    main()