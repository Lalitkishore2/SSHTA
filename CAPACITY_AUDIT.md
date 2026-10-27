# Memory Capacity Consistency Audit

## Overview
This document systematically identifies, catalogs, and audits every capacity claim across the original SSHTA paper, simulation configurations, and architectural models.

---

## 1. Complete Capacity Registry

| Hierarchy Tier | Document Section / Artifact | Claimed Capacity | Context / Purpose | Mathematical Consistency | Audit Status | Recommendation / Reconciliation |
|---|---|---|---|---|---|---|
| **Tier 1 (3D SRAM)** | Abstract, line 11 | 128 MB | 3D-stacked SRAM cache die | Consistent | **PASS** | Maintain 128 MB in architectural model |
| **Tier 1 (3D SRAM)** | Section I, line 25 | 128 MB | Last-level cache structure | Consistent | **PASS** | Maintain 128 MB |
| **Tier 1 (3D SRAM)** | Section III-A, line 61 | 128 MB | Hardware-managed LLC | Consistent | **PASS** | Maintain 128 MB |
| **Tier 1 (3D SRAM)** | Section V, Table V, line 491 | 128 MB | Heterogeneous comparison | Consistent | **PASS** | Maintain 128 MB |
| **Tier 1 (3D SRAM)** | Section VI, line 501 | 128 MB | Conclusion summary | Consistent | **PASS** | Maintain 128 MB |
| **Tier 2 (Soldered LPDDR5X)** | Abstract, line 11 | Unspecified | Stated as "soldered 128-bit LPDDR5X" | N/A | **PASS** | Consistent with text |
| **Tier 2 (Soldered LPDDR5X)** | Section III-A, line 61 | 16 GB | Speed Bridge physical sizing | Consistent | **PASS** | Standard target capacity |
| **Tier 2 (Soldered LPDDR5X)** | Section III-C, line 85 | 16 GB | Package substrate soldered array | Consistent | **PASS** | Standard target capacity |
| **Tier 2 (Soldered LPDDR5X)** | Section IV-B, Table II, line 339 | 16 GB | DRAMsim3 modeled capacity | Consistent | **PASS** | Modeled as 16 GB |
| **Tier 2 (Soldered LPDDR5X)** | Section IV-C, Table III, line 383 | 512 MB | gem5 address range: `AddrRange('512MB')` | Scaled down | **PARTIAL** | Document as gem5 SE simulation scaling artifact |
| **Tier 2 (Soldered LPDDR5X)** | Section V, Table V, line 491 | 16 GB | System summary: `128 MB + 16 GB + 32 GB` | Consistent | **PASS** | Standard target capacity |
| **Tier 2 (Soldered LPDDR5X)** | Project Notes / Archive | 8 GB | Initial exploratory APU specification | Deprecated | **INCONSISTENT** | Superseded by 16 GB; document 8 GB as legacy concept |
| **Tier 3 (LPCAMM2 Reservoir)** | Abstract, line 11 | Up to 64 GB | Modular expandable reservoir | Consistent | **PASS** | Represents maximum module density |
| **Tier 3 (LPCAMM2 Reservoir)** | Section I, line 29 | 32 GB base, up to 64 GB | Socketed LPDDR5X-7500 module | Consistent | **PASS** | Standard target capacity |
| **Tier 3 (LPCAMM2 Reservoir)** | Section III-A, line 61 | 32 GB (expandable to 64 GB) | System architecture overview | Consistent | **PASS** | Standard target capacity |
| **Tier 3 (LPCAMM2 Reservoir)** | Section III-C, line 89 | 32 GB base, up to 64 GB | Field serviceability description | Consistent | **PASS** | Standard target capacity |
| **Tier 3 (LPCAMM2 Reservoir)** | Section IV-B, Table II, line 341 | 32 GB (expandable to 64 GB) | DRAMsim3 modeled capacity | Consistent | **PASS** | Modeled as 32 GB |
| **Tier 3 (LPCAMM2 Reservoir)** | Section IV-C, Table III, line 389 | 2 GB | gem5 address range: `AddrRange(start='512MB', size='2GB')` | Scaled down | **PARTIAL** | Document as gem5 SE simulation scaling artifact |
| **Tier 3 (LPCAMM2 Reservoir)** | Section V, Table V, line 491 | 32 GB (up to 64 GB) | System summary | Consistent | **PASS** | Standard target capacity |
| **MOST Simulation Footprint** | Section IV-D, Table IV, line 421 | 4 MB | 1,000 pages $\times 4\text{ KB}$ ($800\text{ KB}$ hot, $3.2\text{ MB}$ cold) | Micro-scale | **INCONSISTENT** | Working set was $4096\times$ smaller than physical Tier 2 capacity! |

---

## 2. Inconsistency Analysis & Root Causes

### 2.1 The gem5 Scaling Discrepancy (512 MB Tier 2, 2 GB Tier 3)
- **Reported in Paper:** Section IV-C and Table III state that gem5 configured `AddrRange('512MB')` for Tier 2 and `AddrRange(start='512MB', size='2GB')` for Tier 3, totaling 2.5 GB.
- **Physical Intent:** The paper claims physical capacities of 16 GB (Tier 2) and 32–64 GB (Tier 3), totaling 48–80 GB.
- **Root Cause:** gem5 Syscall Emulation (SE) mode requires allocating physical host RAM structures. Allocating 48–80 GB of virtual address space in a single gem5 process on a 16 GB laptop causes severe host paging or out-of-memory crashes. The original researchers scaled down the address ranges to 512 MB and 2 GB simply to verify routing logic.
- **Verdict:** Valid for functional crossbar routing verification, but must be explicitly documented as a **scaled simulation proxy**, not physical full-capacity modeling.

### 2.2 The 8 GB vs 16 GB Tier 2 Ambiguity
- **Observation:** Certain preliminary project summaries mention an "8 GB Tier 2 speed bridge" while the final manuscript specifies 16 GB.
- **Resolution:** A 128-bit LPDDR5X array typically uses four 32-bit discrete DRAM packages. At modern densities (16 Gb or 32 Gb per die):
  - $4 \times 16\text{ Gb} = 64\text{ Gb} = \mathbf{8 \text{ GB}}$ (Budget / Mobile form factor)
  - $4 \times 32\text{ Gb} = 128\text{ Gb} = \mathbf{16 \text{ GB}}$ (Performance / Super-APU form factor)
- **Verdict:** 16 GB is the definitive baseline target for SSHTA. 8 GB represents a lower-cost tiering variant.

### 2.3 The Critical MOST Working Set vs. Capacity Mismatch
- **Observation:** In [`simulations/multi_scale_pipeline/phase4/nano most_sim.py`](file:///c:/Users/LALITKO/Desktop/projects/research%20paper/simulations/multi_scale_pipeline/phase4/nano%20most_sim.py), the simulation modeled exactly **1,000 pages** of 4 KB each, totaling **4 MB**:
  $$\text{Working Set} = 1000 \times 4096 \text{ bytes} = 4,096,000 \text{ bytes} = \mathbf{4.0 \text{ MB}}$$
- **Flaw:** Tier 2 physical capacity is 16 GB (4,194,304 pages). The total working set of the entire synthetic trace (4 MB) is less than **0.025% of Tier 2's capacity**!
- **Consequence:** Because Tier 2 never came close to filling up, **zero demotions or evictions ever occurred** during the simulation, even though Algorithm 1 explicitly included LRU eviction (`Evict_LRU`).
- **Correction Required:** In Phase 1 and Phase 3 validation, we will test both the legacy unconstrained setup and a realistic constrained capacity setup where Tier 2 capacity is calibrated to force actual eviction and demotion dynamics.
