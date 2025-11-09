Lab checklist: benign PCB emissions survey

1. Safety and approvals
- Ensure lab safety gear and electrical safety.
- Obtain any required institutional approvals for equipment use.
- Do not perform tests that could interfere with critical infrastructure or medical devices.

2. Equipment (minimum)
- SDR (e.g., RTL-SDR) or spectrum analyzer (preferably 9 kHz–6 GHz).
- Passive near-field probe (optional but recommended) or small loop probe.
- Shielded enclosure (Faraday cage) or metal box for controlled tests.
- Low-noise power supply; ferrite beads for cable filtering.
- Laptop for logging (air-gapped if required for secure tests).
- Antenna(s) for broad-band scanning.

3. Setup
- Place device on an insulating, non-reflective surface within the enclosure or at the chosen test position.
- Power device from known, filtered supply; document all connections.
- Position probe/antenna at defined distances (e.g., 10 cm, 30 cm, 1 m) and record positions.
- Keep environment consistent across runs (same room, minimal movement).

4. Measurement procedure
- Baseline: measure empty enclosure noise floor and save waterfall / spectrum snapshot.
- Device idle: measure with device powered but idle.
- Device active: measure during typical workloads (boot, CPU stress, IO bursts).
- Log timestamps, device state, software running, and measured bands.
- Near-field scans: move probe around board perimeter and record hotspots.

5. Data handling
- Store raw captures and metadata (device model, revisions, firmware version).
- Anonymize or redact any personal identifiers before public sharing.
- Publish reproducible measurement steps, hardware used, and scripts.

6. Reporting
- Produce frequency vs. power plots, heatmap of near-field hotspots, and a short mitigation recommendation section.
- Share all steps and scripts used to gather the data.