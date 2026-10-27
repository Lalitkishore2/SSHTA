import random

print("======================================================")
print(" SSHTA OS-Level MOST Policy Simulator ")
print("======================================================\n")

# --- 1. Define Architecture Latencies (From Phase 1 & 2) ---
TIER1_LATENCY_NS = 3.86  # 8T Sleepy Stack SRAM
TIER2_LATENCY_NS = 40.0  # LPDDR5X Speed Bridge
TIER3_LATENCY_NS = 80.0  # LPCAMM2 Reservoir

# --- 2. MOST Policy Parameters ---
# If a block in Tier 3 is accessed 3 times, it is promoted to Tier 2
PROMOTION_THRESHOLD = 3

# Initialize memory tiers
tier2_bridge = set() # Starts empty
tier3_reservoir = set(range(1000)) # 1000 total memory pages start in cold storage

# Statistics tracking
t2_hits = 0
t3_hits = 0
total_latency_ns = 0
migrations = 0
access_tracker = {}

# --- 3. Generate a Synthetic Workload Trace ---
# Simulating an AI workload: 80% of accesses hit a "hot" 20% of pages
print("Generating 10,000 AI memory access requests...")
trace = []
for _ in range(10000):
    if random.random() < 0.80:
        trace.append(random.randint(0, 199)) # Hot pages
    else:
        trace.append(random.randint(200, 999)) # Cold pages

# --- 4. Run the Baseline (Standard System, No Tiering) ---
baseline_latency = len(trace) * TIER3_LATENCY_NS

# --- 5. Run the SSHTA MOST Policy Simulation ---
print("Executing MOST Policy Page Migrations...\n")
for page in trace:
    # Check if page is currently in Tier 2 (Speed Bridge)
    if page in tier2_bridge:
        t2_hits += 1
        total_latency_ns += TIER2_LATENCY_NS

    # Otherwise, it must be in Tier 3 (Reservoir)
    else:
        t3_hits += 1
        total_latency_ns += TIER3_LATENCY_NS

        # Track accesses for MOST Hot-Page Promotion
        access_tracker[page] = access_tracker.get(page, 0) + 1

        # If it crosses the threshold, promote it to Tier 2
        if access_tracker[page] >= PROMOTION_THRESHOLD:
            tier2_bridge.add(page)
            tier3_reservoir.discard(page)
            migrations += 1

# --- 6. Calculate & Output Results ---
average_latency = total_latency_ns / len(trace)
baseline_avg_latency = baseline_latency / len(trace)
latency_reduction = ((baseline_avg_latency - average_latency) / baseline_avg_latency) * 100

print(f"--- SIMULATION RESULTS ---")
print(f"Total Memory Accesses:         10,000")
print(f"Tier 2 (Speed Bridge) Hits:    {t2_hits}")
print(f"Tier 3 (Reservoir) Hits:       {t3_hits}")
print(f"Total Pages Promoted (T3->T2): {migrations}")
print(f"")
print(f"Baseline Average Latency:      {baseline_avg_latency:.2f} ns")
print(f"SSHTA MOST Average Latency:    {average_latency:.2f} ns")
print(f"Overall Latency Reduction:     {latency_reduction:.2f} %")
print("======================================================")