"""
Memory Bandwidth Independent Mathematical Verification Script
Audits LPDDR5X, LPCAMM2, DDR5, HBM4, and CXL memory interfaces.
Analyzes the discrepancy between 153.60 GB/s and 308.33 GB/s.
"""

def calc_bandwidth(transfer_rate_mts, bus_width_bits):
    """
    Theoretical peak bandwidth formula:
    BW (GB/s) = Transfer Rate (MT/s) * Bus Width (bits) / (8 bits/byte * 1000)
    Note: In decimal GB/s (10^9 B/s), standard in JEDEC / IEEE networking and memory bandwidth.
    In binary GiB/s (2^30 B/s), divide by 1024 * 1024 * 1024.
    """
    bytes_per_sec = (transfer_rate_mts * 1e6) * (bus_width_bits / 8.0)
    bw_gb_s = bytes_per_sec / 1e9
    bw_gib_s = bytes_per_sec / (1024.0**3)
    return bw_gb_s, bw_gib_s

def audit_configs():
    configs = [
        ("Tier 2: LPDDR5X-9600 (Paper claimed physical bus)", 9600, 128),
        ("Tier 2: LPDDR5X-9600 (Hypothetical 256-bit dual-bus)", 9600, 256),
        ("Tier 2: LPDDR5X-9635.4 (DRAMSim3 exact match for 308.33 GB/s at 256-bit)", 9635.37, 256),
        ("Tier 3: LPCAMM2 LPDDR5X-7500 (128-bit single module)", 7500, 128),
        ("Tier 3: LPCAMM2 LPDDR5X-8533 (JEDEC fast grade)", 8533, 128),
        ("Baseline: DDR5-5600 SO-DIMM (Dual-channel 2x64=128-bit)", 5600, 128),
        ("Baseline: DDR5-4800 SO-DIMM (Dual-channel 128-bit)", 4800, 128),
        ("SSHTA-X Tier 2: HBM4 (2048-bit bus at 8.0 Gbps / 8000 MT/s)", 8000, 2048),
        ("SSHTA-X Tier 4: CXL 4.0 (PCIe 6.0 x16, 64 GT/s, 16 lanes PAM4 raw)", 64000, 16),
    ]
    
    print("=========================================================================================")
    print(" MEMORY BANDWIDTH AUDIT TABLE ")
    print("=========================================================================================")
    print(f"{'Interface / Configuration':<55} | {'MT/s':<8} | {'Bits':<5} | {'Peak GB/s':<10} | {'Peak GiB/s':<10}")
    print("-" * 95)
    for name, rate, width in configs:
        gb_s, gib_s = calc_bandwidth(rate, width)
        print(f"{name:<55} | {rate:<8.1f} | {width:<5} | {gb_s:<10.2f} | {gib_s:<10.2f}")
    print("=========================================================================================\n")

if __name__ == "__main__":
    audit_configs()
