# Phase 0 Milestone Validation Report: Research Audit & Baseline Discovery

## Executive Summary
This milestone report synthesizes Phase 0 (Project Audit & Discovery) of the Validation-First Research Framework.
In accordance with the **Validation-First Research Contract**, no source code has been altered, no premature conclusions have been adopted, and all legacy artifacts, netlists, and paper claims have been independently analyzed without assuming their validity.

This audit has discovered three critical findings that explain every numerical anomaly and reviewer objection regarding the legacy SSHTA paper:
1. **The 308.33 GB/s Bandwidth Anomaly:** The reported theoretical physical peak of **153.60 GB/s** for a 128-bit bus at 9600 MT/s is mathematically correct. The conflicting value of **308.332 GB/s** discovered in `dramsim3.txt` was caused by an uncalibrated DRAMSim3 configuration simulating an effective 256-bit bus (64 bytes/cycle at 4.819 GHz).
2. **The "8T vs 14T Sleepy Stack" Transistor Count Inconsistency:** Detailed netlist inspection proves that the proposed bitcell has **14 physical transistors** (an 8T read-decoupled core plus 6 sleepy-stack transistors). It should never be described as an 8T cell without clarifying that 14 transistors are present on silicon. The scientific naming is formally standardized as **14T Read-Decoupled Sleepy-Stack SRAM (14T-RDSS)**.
3. **Fatal Omissions in the Original MOST Simulation:** In `nano most_sim.py`, the reported 77.01% hit rate and 49.20 ns average latency were generated because the 5.0 µs page migration penalty was **completely omitted ($0\text{ ns}$ added to latency)**, Tier 2 capacity was treated as **infinite (no demotions occurred)**, and no deterministic random seed was set.

---

## Phase 0 Deliverable Index

| Phase 0 Task | Output Document / Artifact | Scope & Description | Status |
|---|---|---|---|
| **Task 0.1** | [`PROJECT_INVENTORY.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/PROJECT_INVENTORY.md) | Exhaustive registry of all 420 workspace files across 16 categories | **COMPLETED** |
| **Task 0.2** | [`AUDIT_TABLE.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/AUDIT_TABLE.md) | 53 numerical claims extracted from paper and classified across 7 evidence axes | **COMPLETED** |
| **Task 0.3** | [`BANDWIDTH_AUDIT.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/BANDWIDTH_AUDIT.md) & [`validation/bandwidth_audit.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/validation/bandwidth_audit.md) | Full mathematical proof of 128-bit bandwidths; root cause of 308.33 GB/s | **COMPLETED** |
| **Task 0.4** | [`CAPACITY_AUDIT.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/CAPACITY_AUDIT.md) | Catalog of capacity claims, gem5 SE scaling artifacts, and MOST 4 MB footprint | **COMPLETED** |
| **Task 0.5** | [`SRAM_TRANSISTOR_AUDIT.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/SRAM_TRANSISTOR_AUDIT.md) | Transistor-by-transistor count (6T, 8T, 12T, 14T); naming standardization | **COMPLETED** |
| **Task 0.6** | [`validation/audit/sim_config_audit.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/validation/audit/sim_config_audit.md) | Line-by-line audit of LTspice, DRAMSim3, gem5, and MOST Python scripts | **COMPLETED** |
| **Task 0.7** | [`PHASE_0_VALIDATION_REPORT.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/PHASE_0_VALIDATION_REPORT.md) | This synthesis document (**Checkpoint 0 Gate**) | **COMPLETED** |

---

## Detailed Audit Findings by Subsystem

### 1. Project Inventory Summary (420 Files)
- **Circuit Simulation Artifacts (`simulations/ltspice_bitcells/`):** 21 SPICE netlists, 20 schematics, 30 raw waveform decks, and 17 database files across 6T, 8T, and sleepy-stack variations.
- **DRAM Timing Artifacts (`simulations/multi_scale_pipeline/phase2/`):** Raw logs and JSON summaries for soldered LPDDR5X and socketed LPCAMM2 runs.
- **Architectural Bus Routing (`simulations/multi_scale_pipeline/phase3/`):** gem5 v25.1 execution stats (`stats_output.txt`) and Python configuration (`ssha_super_apu.py_code.txt`).
- **OS Policy Simulation (`simulations/multi_scale_pipeline/phase4/`):** Legacy trace-driven simulator script (`nano most_sim.py`) and terminal execution captures.
- **Manuscripts & References:** Original IEEE Word manuscripts (4.78 MB), PDF copies, plagiarism check documents, and reference PDFs.

---

### 2. Numerical Claim Classification Summary (53 Claims)
Out of 53 extracted numerical claims in [`AUDIT_TABLE.md`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/AUDIT_TABLE.md):
- **PASS (39 Claims / 73.6%):** Mathematically sound, physically valid, and verified in simulation logs (e.g., 6T/8T/14T delay, hold SNM, standby leakage at 25°C, 153.60 GB/s peak, 120.00 GB/s peak, 2.05 W, 3.17 W, gem5 routing stats).
- **PARTIAL (3 Claims / 5.7%):** Partially supported but dependent on unstated assumptions (e.g., 110°C leakage suppression was an analytical literature extrapolation, gem5 address ranges were scaled-down proxies).
- **INCONSISTENT (2 Claims / 3.8%):** Conflicting terms within the paper (e.g., "8T" vs "14T" bitcell naming, 4 MB synthetic working set vs 16 GB physical capacity).
- **FAIL (9 Claims / 16.9%):** Disproven by physical formulas or invalid simulation code:
  - Raw DRAMSim3 average bandwidth ($308.33\text{ GB/s}$) exceeded 128-bit physical bus limits by $2.007\times$.
  - Original MOST script omitted migration latency entirely ($0\text{ ns}$ added vs $5.0\ \mu\text{s}$ claimed).
  - Effective latency formula claimed $K_{access} = 10^4$, which was mathematically impossible in a 10,000-request trace over 1,000 pages (actual $K_{access} \approx 10$, making real migration overhead $500\text{ ns}$ per access).

---

### 3. Memory Bandwidth Validation Summary
- **Mathematical Formula:**
  $$BW_{peak}\text{ (GB/s)} = \frac{\text{Transfer Rate (MT/s)} \times \text{Bus Width (bits)}}{8000}$$
- **Tier 2 (Soldered LPDDR5X-9600, 128-bit):**
  $$BW_{peak} = \frac{9600 \times 128}{8000} = \mathbf{153.60 \text{ GB/s}}$$
  $$BW_{sustained} = 153.60 \times 0.78125 = \mathbf{120.00 \text{ GB/s}}$$
- **Tier 3 (Modular LPCAMM2 LPDDR5X-7500, 128-bit):**
  $$BW_{peak} = \frac{7500 \times 128}{8000} = \mathbf{120.00 \text{ GB/s}}$$
  $$BW_{sustained} = 120.00 \times 0.7083 = \mathbf{85.00 \text{ GB/s}}$$
- **The $308.33\text{ GB/s}$ Artifact:**
  Corresponded to 64 bytes transferred per cycle across 100,000 cycles at 4.819 GHz, which simulated a **256-bit bus**. It is rejected as an uncalibrated simulation artifact.

---

### 4. Transistor Count & SRAM Topology Summary
- **Standard 6T:** 2 PMOS pull-up, 2 NMOS pull-down, 2 NMOS access gates = **6 transistors**.
- **Standard 8T:** 6T core + 2 NMOS decoupled read buffer = **8 transistors**.
- **Proposed Bitcell:**
  - 2 PMOS pull-up
  - 4 NMOS stacked pull-down
  - 2 NMOS write access gates
  - 2 NMOS read buffer gates
  - 2 PMOS pull-up sleep transistors
  - 2 NMOS pull-down sleep transistors
  - **Total = 14 transistors**.
- **Standardized Scientific Name:** **14T Read-Decoupled Sleepy-Stack SRAM (14T-RDSS)**.

---

### 5. MOST Policy Implementation Flaws
Analysis of `nano most_sim.py` revealed:
```python
# MIGRATION LOOP IN ORIGINAL SCRIPT:
if access_tracker[page] >= PROMOTION_THRESHOLD:
    tier2_bridge.add(page)
    tier3_reservoir.discard(page)
    migrations += 1  # <--- ZERO LATENCY ADDED!
```
Because `total_latency_ns` was never incremented by `tmig` ($5.0\ \mu\text{s} = 5,000\text{ ns}$), the reported average latency was simply the weighted serviced latency ($0.7701 \times 40.0 + 0.2299 \times 80.0 = 49.20\text{ ns}$). If the 573 promotions had incurred the 5.0 µs penalty, total migration overhead would have been:
$$\Delta T_{mig} = 573 \text{ migrations} \times 5,000 \text{ ns} = 2,865,000 \text{ ns}$$
$$\Delta L_{per\_access} = \frac{2,865,000 \text{ ns}}{10,000 \text{ accesses}} = \mathbf{286.5 \text{ ns per access}}$$
Making true average access latency **$335.7\text{ ns}$**, which is **$4.2\times$ worse** than the flat baseline ($80.0\text{ ns}$)!
This mathematical breakdown proves why unthrottled page migration without cost-benefit profitability gating destroys system performance, and justifies why **MOST-X** with cost gating and dynamic throttling is required.

---

## Checkpoint 0 Review & Proposed Phase 1 Actions

With Phase 0 completed, the workspace is ready for **Phase 1: Independent Baseline Reproduction from Scratch**:

1. **Step 1.1 (SRAM Reproduction):** Re-simulate 6T, 8T, and 14T-RDSS bitcells in `validation/baseline_reproduction/sram/` with 45nm PTM across 25°C, 50°C, 75°C, 90°C, and 110°C, extracting delay, leakage, and SNM.
2. **Step 1.2 (DRAMSim3 Reproduction):** Execute calibrated 128-bit configurations for LPDDR5X-9600 and LPCAMM2-7500 in `validation/baseline_reproduction/dram/`.
3. **Step 1.3 (MOST Policy Reproduction):** Re-implement MOST from text in `validation/baseline_reproduction/most/` with deterministic seed (42), recording both the flawed legacy result (0 migration penalty) and the realistic physically constrained result.
4. **Step 1.4 (Sanity Tests):** Run the 8 synthetic edge-case tests.
5. **Step 1.5 (Milestone 1 Report):** Generate `PHASE_1_REPRODUCTION_REPORT.md` and initial dashboard.

*Note: Per the validation-first protocol, SSHTA-X development will remain paused until Phase 1 reproduction is completed.*
