# Research Methodology & Simulation Physics: SSHTA to SSHTA-X

## 1. Scope & Guiding Principles
This document formalizes the complete mathematical, physical, and simulation methodology employed throughout the **SSHTA Validation-First Audit and SSHTA-X Framework**.

### Non-Negotiable Methodological Rules
1. **Mathematical Rigor:** Every claimed metric must have an explicit formula, verifiable units, and parameter sources.
2. **Physical Feasibility:** Theoretical limits (e.g. bus bandwidth, speed-of-light signaling, thermal resistance) must govern all simulated hardware.
3. **Reproducibility:** All simulations must run deterministically across fixed random seeds (42, 43, 44, 45, 46) and output machine-readable artifacts.
4. **Host Safety:** All workloads and simulators must execute sequentially within the constraints of the development host (16 GB RAM, 8C/16T CPU).

---

## 2. Circuit-Level SRAM Methodology (LTspice & 45nm PTM)

### 2.1 Model & Technology Parameters
- **Process Technology:** Arizona State University Predictive Technology Model (PTM) 45nm High Performance bulk CMOS (`45nm_HP.pm`).
- **Nominal Supply Voltage ($V_{DD}$):** $1.0\text{ V}$ (swept from $0.4\text{ V}$ to $1.1\text{ V}$).
- **Nominal Operating Temperature:** $25^\circ\text{C}$ (swept across $25^\circ\text{C}$, $50^\circ\text{C}$, $75^\circ\text{C}$, $90^\circ\text{C}$, $110^\circ\text{C}$).
- **Transistor Sizing:**
  * Pull-Up PMOS ($P_1, P_2$): $W/L = 90\text{ nm} / 45\text{ nm}$ ($2\lambda$)
  * Pull-Down NMOS ($N_1, N_2$): $W/L = 135\text{ nm} / 45\text{ nm}$ ($3\lambda$)
  * Write Pass Gates ($N_3, N_4$): $W/L = 90\text{ nm} / 45\text{ nm}$ ($2\lambda$)
  * Read Decoupled Driver ($N_5$): $W/L = 135\text{ nm} / 45\text{ nm}$ ($3\lambda$)
  * Read Pass Gate ($N_6$): $W/L = 90\text{ nm} / 45\text{ nm}$ ($2\lambda$)
  * Sleepy-Stack Transistors ($S_{P1}, S_{P2}, S_{N1}, S_{N2}, S_{RN1}, S_{RN2}$): $W/L = 180\text{ nm} / 45\text{ nm}$ ($4\lambda$, low on-resistance)

### 2.2 Propagation Delay Measurement
Read propagation delay ($t_{pd,read}$) is measured from the 50% transition of the Read Wordline (RWL) to the 50% voltage drop on the Read Bitline (RBL):

$$t_{pd,read} = t(V_{RBL} = 0.5 \cdot V_{DD}) - t(V_{RWL} = 0.5 \cdot V_{DD})$$

Extracted via LTspice SPICE measurement directive:
```spice
.meas tran t_read_delay trig v(rwl) val=0.5 rise=1 targ v(rbl) val=0.5 fall=1
```

### 2.3 Standby Leakage Measurement
Measured via DC operating point (`.op`) under standby conditions ($WL = 0\text{ V}, RWL = 0\text{ V}, BL = V_{DD}, \overline{BL} = V_{DD}, RBL = V_{DD}, Q = 1, \overline{Q} = 0$):

$$I_{leak} = I(V_{DD}) = \sum I_{subthreshold} + \sum I_{gate\_tunneling}$$

Total standby power for a 128 MB array ($N_{cells} = 1.074 \times 10^9$):

$$P_{standby} = N_{cells} \times I_{leak} \times V_{DD}$$

### 2.4 Static Noise Margin (SNM) Extraction
Extracted using Seevinck's butterfly curve method via static DC sweep of cross-coupled inverters. Hold SNM ($SNM_{hold}$) and Read SNM ($SNM_{read}$) correspond to the side length of the maximum square that can fit within the lobes of the voltage transfer characteristics (VTC):

$$SNM = \max \{ S \mid \square_S \subset \text{VTC Loop} \}$$

---

## 3. DRAM Channel & Bandwidth Methodology

### 3.1 First-Principles Theoretical Peak Bandwidth
Theoretical peak bandwidth ($BW_{peak}$) is strictly defined by data transfer rate and physical data bus width:

$$BW_{peak} (\text{GB/s}) = \frac{\text{Transfer Rate (MT/s)} \times \text{Bus Width (bits)}}{8 \text{ bits/byte} \times 1000}$$

#### Physical Proof for 128-bit LPDDR5X-9600:
$$BW_{peak} = \frac{9600 \times 128}{8 \times 1000} = \mathbf{153.60 \text{ GB/s}}$$

*Root Cause of Paper Discrepancy:* The $308.33\text{ GB/s}$ in legacy `dramsim3.txt` was produced by an uncalibrated 256-bit configuration (`channel_width = 64`, `burst_length = 16` at $4.819\text{ GHz}$), representing an impossible $2\times$ bus width.

#### Physical Proof for 2048-bit HBM4 at 8.0 Gbps:
$$BW_{peak} = \frac{8000 \text{ MT/s} \times 2048 \text{ bits}}{8 \times 1000} = \mathbf{2048.0 \text{ GB/s}} = \mathbf{2.048 \text{ TB/s}}$$

### 3.2 Sustained Bandwidth & Efficiency
Actual sustained bandwidth ($BW_{sustained}$) incorporates protocol overheads (tRCD, tRP, tWTR, refresh pauses, and bus turnaround penalties):

$$BW_{sustained} = BW_{peak} \times \eta_{bus}$$

Where $\eta_{bus} \approx 0.78$ for LPDDR5X and $\eta_{bus} \approx 0.80$ for HBM4 under FR-FCFS scheduling.

---

## 4. Multi-Agent Memory Traffic Generation Methodology

Traces represent realistic heterogeneous compute memory demand across 10 standardized workload profiles:
- **W0 (Zipfian / Hot-Cold):** Skewed Pareto distribution ($80\%$ of accesses touch $20\%$ of address space). Models database index and cache locality.
- **W1 (Sequential Streaming):** Unit stride linear traversals ($A[i]$). Tests prefetching and bus saturation.
- **W2 (Uniform Random):** Uniformly distributed pseudo-random page accesses. Models graph traversal and pointer chasing.
- **W3 (Strided Traversal):** Regular non-unit stride ($A[i \times 8]$). Models matrix column access.
- **W4 (Shifting Working Set):** Phase-changing temporal working set every $2500$ requests. Tests LRU eviction and policy reactivity.
- **W5 (Matrix GEMM):** Tiled $32 \times 32$ block matrix multiplication. Heavy temporal reuse of matrix blocks.
- **W6 (CNN Inference):** 2D convolutional sliding window feature-map buffers. Local spatial window overlap.
- **W7 (Transformer Attention & KV-Cache):** Bimodal distribution ($50\%$ static weights, $35\%$ streaming KV-cache tokens, $15\%$ temporary buffers).
- **W8 (Mixed CPU / GPU):** Interleaved latency-sensitive CPU loads ($50\%$) and GPU streaming framebuffer writes ($50\%$).
- **W9 (Mixed CPU / GPU / NPU):** Full super-APU concurrency ($35\%$ NPU matrix streams, $35\%$ CPU demand loads, $30\%$ GPU raster bursts).

---

## 5. Dynamic Tiering & Migration Policies

### 5.1 Original MOST Algorithm
```python
def access(page, theta=3):
  if page in tier2:
    return T2_LATENCY
  else:
    pac[page] += 1
    if pac[page] >= theta:
      tier2.promote(page)
      # Flaw: Original paper omitted DMA penalty and assumed infinite capacity!
    return T3_LATENCY
```

### 5.2 MOST-X Multi-Factor Heuristic
Every access updates the multi-factor page score:

$$\text{Score}(p) = (0.35 f + 0.25 r + 0.20 s + 0.20 p) - (0.15 m + 0.10 t + 0.05 q + 0.05 o)$$

Profitability gating condition:

$$E[N_{future}] \times (\Delta L) > t_{DMA} + P_{congestion}$$

Where:
- $\Delta L = L_{slow} - L_{fast}$
- $t_{DMA} = 400\text{ ns} + \frac{4096 \text{ bytes}}{BW_{cap}}$
- $BW_{cap} = 0.10 \times BW_{link}$ (10% reservation cap)

---

## 6. Transient Lumped RC Thermal Model

The vertical thermal gradient between the compute logic die and 3D SRAM die is solved via forward Euler integration:

$$C_{th,logic} \frac{dT_{logic}}{dt} = P_{logic} - \frac{T_{logic} - T_{sram}}{R_{th,logic-sram}}$$

$$C_{th,sram} \frac{dT_{sram}}{dt} = P_{sram} + \frac{T_{logic} - T_{sram}}{R_{th,logic-sram}} - \frac{T_{sram} - T_{amb}}{R_{th,sram-amb}}$$

$$C_{th,hbm} \frac{dT_{hbm}}{dt} = P_{hbm} - \frac{T_{hbm} - T_{amb}}{R_{th,hbm-amb}}$$

Where:
- $C_{th,logic} = 0.042\text{ J/K}$, $C_{th,sram} = 0.065\text{ J/K}$, $C_{th,hbm} = 0.120\text{ J/K}$
- $R_{th,logic-sram} = 0.18\text{ K/W}$ (Direct Cu-Cu hybrid bond)
- $R_{th,sram-amb} = 0.50\text{ K/W}$, $R_{th,hbm-amb} = 0.63\text{ K/W}$

---

## 7. Energy & Power Accounting

Total full-system energy ($E_{total}$) is the sum of five component domains:

$$E_{total} = E_{dynamic} + E_{static} + E_{noc} + E_{migration} + E_{predictor}$$

1. **Dynamic Memory Access:** $E_{dynamic} = \sum_{t} (\text{Bits Transferred}_t \times E_{pj/bit, t})$
2. **Static Standby Leakage:** $E_{static} = P_{leak}(T_{die}) \times t_{elapsed}$
3. **NoC Router Switching:** $E_{noc} = \sum \text{Hops} \times 256\text{ bits} \times 0.15\text{ pJ/bit/hop}$
4. **DMA Page Migration:** $E_{migration} = \text{Migrated Bytes} \times 8 \times 7.50\text{ pJ/bit}$
5. **Predictor Inference:** $E_{predictor} = N_{inferences} \times 12.0\text{ pJ/inference}$
