# Transistor-Level SRAM Topology & Counting Audit

## Overview
This document provides an exhaustive, node-by-node accounting of every transistor in the SPICE netlists located in `simulations/ltspice_bitcells/`, resolves the nomenclature confusion between "8T", "12T", and "14T Sleepy Stack", and establishes the rigorous scientific classification for the proposed Tier 1 bitcell.

---

## 1. Executive Findings

1. **The Claimed Nomenclature in Paper:**
   - Abstract & Section I: Referred to as **"8-transistor (8T) Sleepy Stack SRAM topology"**.
   - Section III-B & Section VI: Referred to as **"14-transistor (14T) 8T Sleepy Stack bitcell"** and **"14T Sleepy Stack"**.
   - Reviewer Critique: Reviewers flagged this naming as contradictory, asking whether the cell has 8 transistors or 14 transistors.

2. **The Actual Netlist Evidence:**
   - **`6T/6T_test1_ckt.net`**: Exactly **6 transistors** (standard single-port 6T cell).
   - **`8T/8T_test1_ckt.net`**: Exactly **8 transistors** (6T core + 2T decoupled read buffer).
   - **`8T_SleepStack/8T_SS_read_ckt.net`**: Exactly **12 transistors** (8T base with sleepy stack applied only to the pull-down NMOS network).
   - **`8T_SleepStack_14T/test1/8T_SS_read_ckt-14T type.net`**: Exactly **14 transistors** (8T base with sleepy stack applied to both pull-down NMOS and pull-up PMOS networks).

3. **Scientific Naming Verdict:**
   The proposed bitcell is an **8T read-decoupled base cell modified with 6 sleepy-stack transistors**, resulting in a physical count of **14 transistors**.
   The correct and unambiguous scientific naming is:
   $$\mathbf{14T\ Read\text{-}Decoupled\ Sleepy\text{-}Stack\ SRAM\ (14T\text{-}RDSS)}$$

---

## 2. Transistor-by-Transistor Breakdown

### 2.1 Standard 6T SRAM Bitcell (`simulations/ltspice_bitcells/6T/`)
- **Total Transistor Count:** **6** (2 PMOS, 4 NMOS)
- **Netlist File:** `simulations/ltspice_bitcells/6T/6T_test1_ckt.net`

| Instance | Type | Drain | Gate | Source | Bulk | Width ($W$) | Length ($L$) | Functional Role |
|---|---|---|---|---|---|---|---|---|
| `MP1` | PMOS | `VDD` | `Q` | `QB` | `VDD` | 360 nm | 45 nm | Left Inverter Pull-Up |
| `MP2` | PMOS | `VDD` | `QB` | `Q` | `VDD` | 360 nm | 45 nm | Right Inverter Pull-Up |
| `MN1` | NMOS | `QB` | `Q` | `0` (GND) | `0` | 180 nm | 45 nm | Left Inverter Pull-Down |
| `MN2` | NMOS | `Q` | `QB` | `0` (GND) | `0` | 180 nm | 45 nm | Right Inverter Pull-Down |
| `MN3` | NMOS | `Q` | `WL` | `BL` | `0` | 180 nm | 45 nm | Left Pass-Gate Access Transistor |
| `MN4` | NMOS | `QB` | `WL` | `BLB` | `0` | 180 nm | 45 nm | Right Pass-Gate Access Transistor |

---

### 2.2 Standard 8T Read-Decoupled SRAM Bitcell (`simulations/ltspice_bitcells/8T/`)
- **Total Transistor Count:** **8** (2 PMOS, 6 NMOS)
- **Netlist File:** `simulations/ltspice_bitcells/8T/8T_test1_ckt.net`

| Instance | Type | Drain | Gate | Source | Bulk | Width ($W$) | Length ($L$) | Functional Role |
|---|---|---|---|---|---|---|---|---|
| `MP1` | PMOS | `VDD` | `Q` | `QB` | `VDD` | 360 nm | 45 nm | Left Inverter Pull-Up |
| `MP2` | PMOS | `VDD` | `QB` | `Q` | `VDD` | 360 nm | 45 nm | Right Inverter Pull-Up |
| `MN1` | NMOS | `QB` | `Q` | `0` | `0` | 180 nm | 45 nm | Left Inverter Pull-Down |
| `MN2` | NMOS | `Q` | `QB` | `0` | `0` | 180 nm | 45 nm | Right Inverter Pull-Down |
| `MN3` | NMOS | `Q` | `WL` | `BL` | `0` | 180 nm | 45 nm | Write Pass-Gate Access 1 |
| `MN4` | NMOS | `QB` | `WL` | `BLB` | `0` | 180 nm | 45 nm | Write Pass-Gate Access 2 |
| `MN5` | NMOS | `RBL` | `RWL` | `N004` | `0` | 180 nm | 45 nm | Read Buffer Wordline Pass-Gate |
| `MN6` | NMOS | `N004`| `Q` | `0` | `0` | 180 nm | 45 nm | Read Buffer Sensor Pull-Down |

*Key Advantage over 6T:* Read Bitline (`RBL`) is decoupled from storage node `Q`, preventing read disturb and yielding Hold SNM = Read SNM.

---

### 2.3 Proposed 14T Read-Decoupled Sleepy-Stack SRAM (`simulations/ltspice_bitcells/8T_SleepStack_14T/`)
- **Total Transistor Count:** **14** (4 PMOS, 10 NMOS)
- **Netlist File:** `simulations/ltspice_bitcells/8T_SleepStack_14T/test1/8T_SS_read_ckt-14T type.net`

| # | Instance | Type | Nodes (D, G, S, B) | Dimensions | Subsystem | Functional Operation |
|---|---|---|---|---|---|---|
| 1 | `MP1` | PMOS | `N005, Q, QB, VDD` | W=360nm, L=45nm | Latch Core | Left Inverter Pull-Up PMOS |
| 2 | `MP2` | PMOS | `N006, QB, Q, VDD` | W=360nm, L=45nm | Latch Core | Right Inverter Pull-Up PMOS |
| 3 | `MN1_Top` | NMOS | `QB, Q, N010, 0` | W=90nm, L=45nm | Latch Core | Left Stacked Pull-Down NMOS (Top) |
| 4 | `MN1_Bot` | NMOS | `N010, Q, 0, 0` | W=90nm, L=45nm | Latch Core | Left Stacked Pull-Down NMOS (Bottom) |
| 5 | `MN2_Top` | NMOS | `Q, QB, N011, 0` | W=90nm, L=45nm | Latch Core | Right Stacked Pull-Down NMOS (Top) |
| 6 | `MN2_Bot` | NMOS | `N011, QB, 0, 0` | W=90nm, L=45nm | Latch Core | Right Stacked Pull-Down NMOS (Bottom) |
| 7 | `MN3` | NMOS | `Q, WL, BL, 0` | W=180nm, L=45nm | Write Access | Differential Write Access Gate 1 |
| 8 | `MN4` | NMOS | `QB, WL, BLB, 0` | W=180nm, L=45nm | Write Access | Differential Write Access Gate 2 |
| 9 | `MN5` | NMOS | `RBL, RWL, N009, 0` | W=180nm, L=45nm | Read Buffer | Read Wordline Decoupled Access Gate |
| 10 | `MN6` | NMOS | `N009, Q, 0, 0` | W=180nm, L=45nm | Read Buffer | Read Sensor Driver (Driven by Node Q) |
| 11 | `MP_sleep1` | PMOS | `VDD, Sleep_b, N005, VDD` | W=90nm, L=45nm | Sleep Network | Pull-up sleep PMOS bridging VDD to MP1 |
| 12 | `MP_sleep2` | PMOS | `VDD, Sleep_b, N006, VDD` | W=90nm, L=45nm | Sleep Network | Pull-up sleep PMOS bridging VDD to MP2 |
| 13 | `MN_Sleep1` | NMOS | `N010, Sleep, 0, 0` | W=90nm, L=45nm | Sleep Network | Pull-down sleep NMOS bridging N010 to GND |
| 14 | `MN_Sleep2` | NMOS | `N011, Sleep, 0, 0` | W=90nm, L=45nm | Sleep Network | Pull-down sleep NMOS bridging N011 to GND |

---

## 3. Discrepancy Classification & Architectural Rationale

1. **Why did the authors write "8T Sleepy Stack"?**
   The authors designed the cell by taking the standard **8T read-decoupled architecture** and applying the **Sleepy Stack circuit technique** to the inverters. In circuit design papers, researchers often refer to such cells as "an 8T cell with sleepy stack", which was mistakenly abbreviated in the abstract and introduction as "8T Sleepy Stack".
2. **Is it 8T or 14T?**
   It has **14 physical transistors**. It should never be described as an 8T cell without clarifying that 14 transistors are present on silicon.
3. **Silicon Area Impact:**
   - A standard 6T cell has 6 transistors.
   - The 14T-RDSS cell has 14 transistors, increasing transistor count by $2.33\times$ and physical cell layout area by approximately $40\%\text{--}45\%$ (due to sharing of diffusion contacts and well taps).
   - The paper accurately reports this trade-off: a ~40% area penalty accepted in exchange for a 42.58% reduction in standby leakage and complete elimination of read disturb.
