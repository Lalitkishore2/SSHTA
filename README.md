# SSHTA: Architectural Paradigms for the Super-APU

[![Publication](https://img.shields.io/badge/IEEE-Camera--Ready-blue.svg)](SSHTA_IEEE_Paper.pdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Audit Status](https://img.shields.io/badge/Turnitin%20Plagiarism-0.0%25-brightgreen.svg)](AUDIT_TABLE.md)
[![Verification](https://img.shields.io/badge/SPICE%20%26%20DRAM-Verified-success.svg)](validation/)

This repository contains the camera-ready publication manuscript, circuit-level SPICE netlists, cycle-accurate memory simulation models, and full reproducibility suite for:

> **"Architectural Paradigms for the Super-APU: The SSHTA Framework"**  
> *D. Manoj Kumar, S V Lalitkishore, and Surisetti Yagnesh*  
> Dept. of Electronics and Communication Engineering, SRM Institute of Science and Technology

---

## 📄 Publication Deliverables
- **Camera-Ready DOCX:** [`SSHTA_IEEE_Paper.docx`](SSHTA_IEEE_Paper.docx)
- **Vector PDF (8 Pages):** [`SSHTA_IEEE_Paper.pdf`](SSHTA_IEEE_Paper.pdf)
- **Markdown Edition:** [`SSHTA_Paper.md`](SSHTA_Paper.md)

---

## 🔬 Key Scientific & Audit Findings
1. **14T-RDSS SRAM Bitcell:** Standardized 14-transistor topology achieving **82.67% standby leakage suppression at 110°C** and 0.30V data retention stability under 45nm PTM.
2. **Tier 2 Memory Calibration:** Calibrated 128-bit LPDDR5X-9600 physical peak bandwidth to **153.60 GB/s** (120.0 GB/s sustained at 2.05 W).
3. **Realistic DMA Migration Analysis:** Evaluated realistic 5.0 µs DMA copy costs, demonstrating the need for access thresholding ($\\theta = 3$) and exponential decay aging ($\\alpha = 0.85$) to prevent bus thrashing.

---

## 🛠️ Verification & Building
```powershell
# Run the complete Turnitin & AI similarity audit:
python tools_and_scripts/audit_turnitin.py

# Recompile the manuscript:
python tools_and_scripts/build_sshta_manuscript.py
```

## 📜 License
MIT License. Copyright (c) 2026 D. Manoj Kumar, S V Lalitkishore, Surisetti Yagnesh.
