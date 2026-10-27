# Simulation Configuration & Toolchain Audit

## Overview
This document presents the comprehensive simulation configuration audit across LTspice, DRAMSim3, gem5, and MOST models in the original SSHTA research pipeline across four distinct simulation environments:
1. **LTspice 26.0.2** (Circuit-Level SRAM Bitcell Simulation)
2. **DRAMsim3** (Cycle-Accurate DRAM Timing & Power Modeling)
3. **gem5 v25.1** (System Bus Architecture & Address Space Isolation)
4. **Python Trace Simulator** (OS-Level MOST Page Tiering Policy)

---

## 1. LTspice Circuit Simulation Audit

### 1.1 Model Library & Setup
- **Device Model Deck:** Berkeley 45 nm Predictive Technology Model (`45nm_HP.pm`)
- **Supply Voltage ($V_{DD}$):** $1.00\text{ V}$ nominal
- **Simulation Commands:**
  - Transient Analysis: `.tran 1p 20n` (1 picosecond time-step resolution over a 20 ns window)
  - DC Operating Point: `.op` (Standby leakage current extraction)
  - Model Inclusions: `.include C:\SSHTA_Sim\models\45nm_HP.pm`, `.options allow_ambiguous_models`
- **Initial Conditions:** `.ic V(Q)=1 V(QB)=0 V(RBL)=1`

### 1.2 Transistor Sizing Audit
| Transistor Class | Instances | Width ($W$) | Length ($L$) | Aspect Ratio ($W/L$) | Evaluation |
|---|---|---|---|---|---|
| Pull-Up PMOS | `MP1`, `MP2` | 360 nm | 45 nm | 8.0 | Standard high-beta ratio for robust write recovery |
| Stacked Pull-Down NMOS | `MN1_Top`, `MN1_Bot`, `MN2_Top`, `MN2_Bot` | 90 nm | 45 nm | 2.0 | Half-width stacking design per sleepy-stack methodology |
| Sleep NMOS | `MN_Sleep1`, `MN_Sleep2` | 90 nm | 45 nm | 2.0 | High-efficiency leakage suppression in parallel |
| Sleep PMOS | `MP_sleep1`, `MP_sleep2` | 90 nm | 45 nm | 2.0 | High-efficiency leakage suppression in parallel |
| Write Pass-Gates | `MN3`, `MN4` | 180 nm | 45 nm | 4.0 | Symmetric write capability |
| Read Decoupled Buffer | `MN5`, `MN6` | 180 nm | 45 nm | 4.0 | Fast discharge of bitline capacitance (10 fF) |

### 1.3 Measurement Methodology Audit
- **Read Propagation Delay:**
  `.meas TRAN Read_Delay TRIG V(RWL) VAL=0.5 RISE=1 TARG V(RBL) VAL=0.5 FALL=1`
  *Assessment:* Standard 50% voltage threshold definition. Correct and physically meaningful.
- **Write Transition Metric:**
  Measured relative offset between $V(Q) = 0.5\text{ V}$ and $V(WL) = 0.5\text{ V}$.
  *Assessment:* The reported negative offset ($-17.99\text{ ps}$) indicates that node Q crossed 0.5 V before the rising WL pulse reached 0.5 V due to high pass-gate conductivity. True settling time is ~150 ps.
- **Static Noise Margin (SNM):**
  Extracted via butterfly curves by sweeping internal noise sources $V_n$ from $-0.5\text{ V}$ to $+0.5\text{ V}$.
  *Assessment:* Standard Seevinck diagonal square method. Verified.
- **Temperature Sweep Limitations:**
  The original repository only simulated at room temperature ($25^\circ\text{C}$). The claimed "99% suppression at 110°C" was an analytical extrapolation cited from Park & Mooney (2005), not a local SPICE measurement.
  *Action:* A full automated 25°C–110°C sweep will be executed in Phase 1.

---

## 2. DRAMsim3 Timing & Power Audit

### 2.1 Configuration Comparison
| Parameter | Tier 2 Configuration (`LPDDR5X_tier2_SSHTA.ini`) | Tier 3 Configuration (`LPCAMM2_tier3_SSHTA.ini`) |
|---|---|---|
| **Memory Standard** | LPDDR5X (Soldered) | LPDDR5X / LPCAMM2 (Socketed) |
| **Data Rate** | 9600 MT/s | 7500 MT/s |
| **Clock Frequency ($f_{CK}$)** | ~4800 MHz | ~3750 MHz |
| **Supply Voltage ($V_{DD}$)** | 1.05 V | 1.05 V |
| **Channels / Width** | Effective 256-bit (simulated) vs 128-bit (claimed) | Effective 256-bit (simulated) vs 128-bit (claimed) |
| **Simulated Requests** | 100,000 (Stream read benchmark) | 100,000 (Stream read benchmark) |
| **Reads Completed** | 99,967 | 99,967 |
| **Total Energy** | $2.0453 \times 10^8\text{ pJ}$ ($204.53\text{ mJ}$) | $3.1703 \times 10^8\text{ pJ}$ ($317.03\text{ mJ}$) |
| **Average Power Output** | **2,045.3 mW (2.05 W)** | **3,170.3 mW (3.17 W)** |
| **Average Read Latency** | **38.67 cycles** | **39.60 cycles** |
| **Average Bandwidth Output** | **308.332 GB/s** | **308.332 GB/s** |

### 2.2 Root-Cause of the Identical 308.332 GB/s Output
Both simulation runs executed an identical synthetic read-streaming trace (100,000 requests, 1 request per cycle) over 100,000 cycles, completing 99,967 requests of 64 bytes each in $20.75\ \mu\text{s}$.
$$\text{Simulated Bandwidth} = \frac{99,967 \times 64 \text{ bytes}}{2.07499 \times 10^{-5} \text{ s}} = \mathbf{308.332 \text{ GB/s}}$$
Because the channel burst configuration simulated 64 bytes per DRAM cycle (512 bits / 2 beats = 256-bit interface), both output files recorded 308.332 GB/s. The authors took the power and latency values from DRAMSim3, but correctly overrode the bandwidth with physical calculations (153.60 GB/s and 120.00 GB/s).

---

## 3. gem5 Architectural Routing Audit

### 3.1 Setup & Configuration
- **Script Location:** `simulations/multi_scale_pipeline/phase3/ssha_super_apu.py_code.txt`
- **gem5 Version:** v25.1
- **CPU Model:** `TimingSimpleCPU` operating at 3.0 GHz
- **Interconnect:** `SystemXBar`
- **Memory Controllers:**
  - `system.mem_ctrl_tier2.dram = DDR4_2400_8x8()` with `range = AddrRange('512MB')`
  - `system.mem_ctrl_tier3.dram = DDR4_2400_8x8()` with `range = AddrRange(start='512MB', size='2GB')`
- **Workload Binary:** Statically linked Linux `hello` executable (`tests/test-progs/hello/bin/x86/linux/hello`)

### 3.2 Audit Assessment & Limitations
1. **Functional vs. Timing Scope:** The experiment was purely a **functional crossbar address decode validation**. It proved that requests mapped to addresses below 512 MB routed exclusively to controller 0 (65,455 bytes read, 7,160 bytes written) and 0 bytes reached controller 1.
2. **DRAM Model Substitution:** The script utilized gem5's built-in `DDR4_2400_8x8` SimObject as a placeholder rather than a custom LPDDR5X PHY model.
3. **Instruction Set:** The simulation executed x86, not RISC-V.
4. **Verdict:** Valid as a proof-of-concept for dual-range crossbar routing, but does NOT constitute performance simulation of LPDDR5X or RISC-V.

---

## 4. Python Trace Simulator (MOST Policy) Audit

### 4.1 Script Analysis: `simulations/multi_scale_pipeline/phase4/nano most_sim.py`
```python
# Latency parameters
TIER1_LATENCY_NS = 3.86
TIER2_LATENCY_NS = 40.0
TIER3_LATENCY_NS = 80.0
PROMOTION_THRESHOLD = 3

# Memory state
tier2_bridge = set() # Infinite capacity
tier3_reservoir = set(range(1000)) # 1000 pages
```

### 4.2 Identified Fatal Flaws
1. **Zero Migration Cost:**
   When a page was promoted from Tier 3 to Tier 2 (lines 57–60), the script added `migrations += 1` but **added zero latency to `total_latency_ns`**. The paper claimed a 5.0 µs page migration penalty, but this penalty was never executed in the simulation loop.
2. **Infinite Tier 2 Capacity:**
   `tier2_bridge` was implemented as an unbounded Python `set()`. Demotion (`Evict_LRU`) was completely absent from the script, meaning pages were never evicted back to Tier 3.
3. **Missing Seed:**
   `random.random()` was executed without `random.seed(42)`, leading to minor run-to-run variations (7,701 hits in the paper vs 7,732 hits upon re-execution).
4. **Unused Tier 1:**
   `TIER1_LATENCY_NS` was defined but never referenced in the request loop.

---

## 5. Summary of Actions for Baseline Reproduction (Phase 1)
1. **SRAM:** Re-simulate 6T, 8T, and 14T bitcells with clean, isolated netlists across 25°C–110°C in batch mode.
2. **DRAMSim3:** Calibrate configuration files to strictly enforce 128-bit bus widths and report both theoretical peak (153.60 GB/s) and realistic sustained bandwidth.
3. **gem5:** Document SE routing limitations explicitly; replace with authenticated RISC-V traffic generator.
4. **MOST:** Re-implement MOST independently with bounded Tier 2 capacity, actual LRU eviction, deterministic seeding, and explicit 5.0 µs migration penalty accounting.
