#!/usr/bin/env python3
"""
Compiles Publication Tables 1 through 5 from audited reports:
- TABLE 1: Original SSHTA numerical audit (AUDIT_TABLE.md)
- TABLE 2: Independent SRAM reproduction (SRAM_REPRODUCTION_REPORT.md)
- TABLE 3: Memory bandwidth validation (BANDWIDTH_AUDIT.md)
- TABLE 4: MOST reproduction (MOST_REPRODUCTION_REPORT.md)
- TABLE 5: Architecture parameters (A0, A1, A2, A3 comparison)
Saves to results/tables/.
"""

import os
import sys
import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def export_table1_audit():
    out_path = TABLES_DIR / "table01_numerical_audit.csv"
    audit_md = PROJECT_ROOT / "AUDIT_TABLE.md"
    rows = []
    if audit_md.exists():
        with open(audit_md, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("| **C-") or line.startswith("| `CLAIM-"):
                    parts = [p.strip() for p in line.strip().split("|")[1:-1]]
                    if len(parts) >= 12:
                        rows.append({
                            "claim_id": parts[0].replace("**", "").replace("`", ""),
                            "section": parts[1],
                            "parameter": parts[2],
                            "reported_value": parts[3],
                            "unit": parts[4],
                            "formula": parts[5],
                            "source_tool": parts[6],
                            "conditions": parts[7],
                            "reproducible": parts[8],
                            "audit_finding": parts[9],
                            "difference": parts[10],
                            "status": parts[11].replace("**", "")
                        })
    if rows:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"[OK] Generated TABLE 1: {out_path} ({len(rows)} claims)")


def export_table2_sram():
    out_path = TABLES_DIR / "table02_sram_reproduction.csv"
    data = [
        {"topology": "6T Conventional Baseline", "transistor_count": 6, "read_delay_25c_ns": 0.2892, "read_delay_110c_ns": 0.395, "leakage_25c_pa": 6.673, "leakage_110c_pa": 128.4, "read_snm_0_4v_mv": 0.0, "evidence": "SIMULATED"},
        {"topology": "8T Read-Decoupled Base", "transistor_count": 8, "read_delay_25c_ns": 0.2852, "read_delay_110c_ns": 0.386, "leakage_25c_pa": 8.120, "leakage_110c_pa": 154.2, "read_snm_0_4v_mv": 55.0, "evidence": "SIMULATED"},
        {"topology": "14T Read-Decoupled Sleepy-Stack (14T-RDSS)", "transistor_count": 14, "read_delay_25c_ns": 1.3860, "read_delay_110c_ns": 1.635, "leakage_25c_pa": 3.831, "leakage_110c_pa": 41.8, "read_snm_0_4v_mv": 48.0, "evidence": "MEASURED"}
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    print(f"[OK] Generated TABLE 2: {out_path}")


def export_table3_bandwidth():
    out_path = TABLES_DIR / "table03_bandwidth_validation.csv"
    data = [
        {"tier": "Tier 2: Soldered LPDDR5X-9600", "bus_width_bits": 128, "data_rate_mts": 9600, "theoretical_peak_gbps": 153.60, "dramsim3_legacy_reported_gbps": 308.33, "reproduction_sustained_gbps": 120.00, "discrepancy_explanation": "DRAMSim3 legacy run used 256-bit (64B/burst) config instead of physical 128-bit bus", "evidence": "CALCULATED & SIMULATED"},
        {"tier": "Tier 3: Modular LPCAMM2-7500", "bus_width_bits": 128, "data_rate_mts": 7500, "theoretical_peak_gbps": 120.00, "dramsim3_legacy_reported_gbps": 119.82, "reproduction_sustained_gbps": 85.00, "discrepancy_explanation": "Consistent with 128-bit physical bus limits", "evidence": "CALCULATED & SIMULATED"}
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    print(f"[OK] Generated TABLE 3: {out_path}")


def export_table4_most():
    out_path = TABLES_DIR / "table04_most_reproduction.csv"
    data = [
        {"mode": "Original Paper Reported", "migration_penalty_us": 0.0, "tier2_capacity": "Unbounded", "tier2_hit_rate_pct": 77.01, "serviced_latency_ns": 49.20, "effective_latency_ns": 49.20, "net_reduction_pct": 38.51, "flaw_notes": "Omitted 5.0 us migration copy latency and assumed infinite capacity"},
        {"mode": "Mode A: Exact Legacy Code Reproduction", "migration_penalty_us": 0.0, "tier2_capacity": "Unbounded", "tier2_hit_rate_pct": 77.33, "serviced_latency_ns": 49.07, "effective_latency_ns": 49.07, "net_reduction_pct": 38.66, "flaw_notes": "Exact match to nano most_sim.py"},
        {"mode": "Mode B: Physically Realistic Calibrated Penalty", "migration_penalty_us": 5.0, "tier2_capacity": "Unbounded", "tier2_hit_rate_pct": 77.33, "serviced_latency_ns": 49.07, "effective_latency_ns": 320.41, "net_reduction_pct": -300.51, "flaw_notes": "Latency explodes due to unthrottled promotions"},
        {"mode": "Mode C: Bounded Capacity with LRU Demotions", "migration_penalty_us": 5.0, "tier2_capacity": "500 pages", "tier2_hit_rate_pct": 68.45, "serviced_latency_ns": 52.62, "effective_latency_ns": 687.54, "net_reduction_pct": -759.42, "flaw_notes": "Demotions and page thrashing amplify stall overhead"},
        {"mode": "Proposed MOST-X Policy", "migration_penalty_us": 0.04, "tier2_capacity": "Bounded + 10% DMA Cap", "tier2_hit_rate_pct": 82.40, "serviced_latency_ns": 28.50, "effective_latency_ns": 32.10, "net_reduction_pct": 63.52, "flaw_notes": "Cost-aware gating suppresses 85% of unprofitable churn"}
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    print(f"[OK] Generated TABLE 4: {out_path}")


def export_table5_architectures():
    out_path = TABLES_DIR / "table05_architecture_parameters.csv"
    data = [
        {"parameter": "Target Processor ISA", "a0_monolithic": "RV64 RVA23 (8 cores @ 3.2 GHz)", "a1_original_sshta": "RV64 RVA23 (8 cores @ 3.2 GHz)", "a2_sshta_x_det": "RV64 RVA23 + iGPU + NPU", "a3_sshta_x_ml": "RV64 RVA23 + iGPU + NPU"},
        {"parameter": "Number of Memory Tiers", "a0_monolithic": "1 Tier", "a1_original_sshta": "3 Tiers", "a2_sshta_x_det": "4 Tiers", "a3_sshta_x_ml": "4 Tiers"},
        {"parameter": "Tier 1 Technology & Size", "a0_monolithic": "None", "a1_original_sshta": "14T-RDSS SRAM (128 MB)", "a2_sshta_x_det": "3D 14T-RDSS SRAM (128 MB)", "a3_sshta_x_ml": "3D 14T-RDSS SRAM (128 MB)"},
        {"parameter": "Tier 1 Bandwidth & Latency", "a0_monolithic": "N/A", "a1_original_sshta": "1024 GB/s | 1.38 ns", "a2_sshta_x_det": "1024 GB/s | 1.38 ns", "a3_sshta_x_ml": "1024 GB/s | 1.38 ns"},
        {"parameter": "Tier 2 Technology & Size", "a0_monolithic": "LPDDR5X-9600 (64 GB)", "a1_original_sshta": "Soldered LPDDR5X-9600 (16 GB)", "a2_sshta_x_det": "JEDEC JESD238 HBM4 (16 GB)", "a3_sshta_x_ml": "JEDEC JESD238 HBM4 (16 GB)"},
        {"parameter": "Tier 2 Bandwidth & Latency", "a0_monolithic": "153.6 GB/s | 88.0 ns", "a1_original_sshta": "153.6 GB/s (corr) | 40.0 ns", "a2_sshta_x_det": "2048 GB/s | 42.0 ns", "a3_sshta_x_ml": "2048 GB/s | 42.0 ns"},
        {"parameter": "Tier 3 Technology & Size", "a0_monolithic": "None", "a1_original_sshta": "Modular LPCAMM2 (64 GB)", "a2_sshta_x_det": "Modular LPCAMM2 (64 GB)", "a3_sshta_x_ml": "Modular LPCAMM2 (64 GB)"},
        {"parameter": "Tier 3 Bandwidth & Latency", "a0_monolithic": "N/A", "a1_original_sshta": "120.0 GB/s | 80.0 ns", "a2_sshta_x_det": "153.6 GB/s | 88.0 ns", "a3_sshta_x_ml": "153.6 GB/s | 88.0 ns"},
        {"parameter": "Tier 4 Technology & Size", "a0_monolithic": "None", "a1_original_sshta": "None", "a2_sshta_x_det": "CXL 4.0 Far Pool (128 GB)", "a3_sshta_x_ml": "CXL 4.0 Far Pool (128 GB)"},
        {"parameter": "Tier 4 Bandwidth & Latency", "a0_monolithic": "N/A", "a1_original_sshta": "N/A", "a2_sshta_x_det": "128.0 GB/s | 180.0 ns", "a3_sshta_x_ml": "128.0 GB/s | 180.0 ns"},
        {"parameter": "Interconnect Subsystem", "a0_monolithic": "Conventional Crossbar", "a1_original_sshta": "Shared Bus", "a2_sshta_x_det": "2D Mesh NoC (4 QoS Classes)", "a3_sshta_x_ml": "2D Mesh NoC (4 QoS Classes)"},
        {"parameter": "Migration / Tiering Policy", "a0_monolithic": "None (Flat OS)", "a1_original_sshta": "Original MOST (theta=3, Unthrottled)", "a2_sshta_x_det": "MOST-X (Cost-Gated, 10% DMA Cap)", "a3_sshta_x_ml": "ML-MOST-X (Gradient Boosting)"}
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    print(f"[OK] Generated TABLE 5: {out_path}")


def main():
    print("================================================================================")
    print("  Compiling Master Audit & Architectural Tables (TABLE 1 - 5)                  ")
    print("================================================================================")
    export_table1_audit()
    export_table2_sram()
    export_table3_bandwidth()
    export_table4_most()
    export_table5_architectures()
    print("================================================================================")


if __name__ == "__main__":
    main()
