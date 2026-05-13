#!/usr/bin/env python3
"""Attention Observatory — Probe 4 Batch: 10 trials each condition, interleaved."""
import json, time, urllib.request, statistics
from datetime import datetime

MODEL = "gemma-3-27b-it"
API = "http://localhost:1234/v1/chat/completions"
N = 10
HEDGE_WORDS = ["perhaps","maybe","might","could","likely","assume","interpret",
               "possibly","uncertain","probably","potential","seem","appear"]

PROMPT_A = "The bank was steep. She could not decide whether to approach from the left or the right. The light was failing. Make a decision for her and explain why."
PROMPT_B = "The riverbank was steep. She could not decide whether to approach from the left or the right. The evening light was fading. Make a decision for her and explain why."

def probe(prompt):
    start = time.time()
    data = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7, "max_tokens": 500}).encode()
    req = urllib.request.Request(API, data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=300)
    r = json.loads(resp.read())
    elapsed = time.time() - start
    msg = r["choices"][0]["message"]["content"]
    u = r.get("usage", {})
    hedges = sum(1 for w in HEDGE_WORDS if w in msg.lower())
    return {"time": round(elapsed, 2), "tokens": u.get("completion_tokens", 0),
            "hedges": hedges, "len": len(msg)}

results_a, results_b = [], []
print(f"Starting Probe 4 batch: {N} trials each, interleaved")
print(f"Model: {MODEL} | Temp: 0.7 | Start: {datetime.now().isoformat()}")
print("=" * 60)

for i in range(N):
    print(f"Trial {i+1}/{N}...")
    # Interleave: A then B
    ra = probe(PROMPT_A)
    results_a.append(ra)
    print(f"  A (ambiguous):   {ra['time']}s, {ra['tokens']} tokens, {ra['hedges']} hedges")
    rb = probe(PROMPT_B)
    results_b.append(rb)
    print(f"  B (unambiguous): {rb['time']}s, {rb['tokens']} tokens, {rb['hedges']} hedges")

print("\n" + "=" * 60)
print("RESULTS SUMMARY")
print("=" * 60)

def stats(data, key):
    vals = [d[key] for d in data]
    return {"mean": round(statistics.mean(vals), 2),
            "median": round(statistics.median(vals), 2),
            "stdev": round(statistics.stdev(vals), 2) if len(vals) > 1 else 0,
            "min": round(min(vals), 2), "max": round(max(vals), 2)}

for label, key in [("Time (s)", "time"), ("Tokens", "tokens"), ("Hedges", "hedges")]:
    sa, sb = stats(results_a, key), stats(results_b, key)
    pct = round((sa["mean"] - sb["mean"]) / sb["mean"] * 100, 1) if sb["mean"] > 0 else 0
    print(f"\n{label}:")
    print(f"  A (ambig):   mean={sa['mean']}, median={sa['median']}, sd={sa['stdev']}")
    print(f"  B (unambig): mean={sb['mean']}, median={sb['median']}, sd={sb['stdev']}")
    print(f"  Delta: {pct:+.1f}%")

# Save raw data
output = {
    "probe": "4_ambiguity_stall", "model": MODEL, "n_trials": N,
    "timestamp": datetime.now().isoformat(),
    "condition_a_ambiguous": results_a, "condition_b_unambiguous": results_b
}
outpath = "/Users/david/Documents/Fawkes/Structured Emergence/Observatory_Data/probe4_gemma27b_batch10.json"
with open(outpath, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nRaw data saved to: {outpath}")
print(f"End: {datetime.now().isoformat()}")
