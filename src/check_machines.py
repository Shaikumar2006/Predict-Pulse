import json

with open("frontend/public/machine_data.json") as f:
    data = json.load(f)

for m in data["machines"]:
    records = m["records"]
    n = len(records)
    grace = m["gracePeriodSnapshots"]
    crit = m["criticalThreshold"]
    print(f"{m['name']}: criticalThreshold={crit}")
    # Exclude the grace period, exactly like the real dashboard does
    worst_healthy = max(r["severity"] for r in records[grace:n // 2])
    crossing = next((r["index"] for r in records if r["index"] > grace and r["severity"] > crit), None)
    lead_days = (n - 1 - crossing) * m["recordingIntervalMinutes"] / 60 / 24 if crossing else None
    print(f"  Worst first-half severity (post-grace-period): {worst_healthy:.3f} (should be BELOW {crit})")
    print(f"  Crosses critical at index: {crossing}, lead time: {lead_days:.2f} days" if crossing else "  Never crosses")
    print()