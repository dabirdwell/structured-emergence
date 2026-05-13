#!/usr/bin/env python3
"""Fast probe launcher with computed device map for multi-GPU Llama models.

Reads num_hidden_layers from the model config and balances layers across the
visible GPUs, leaving room on the edge GPUs for embed_tokens and lm_head.
Works for Llama 3.1 70B (80 layers) and 405B (126 layers).
"""
import torch, gc, os, sys, json
from transformers import AutoModelForCausalLM, AutoTokenizer
from datetime import datetime

os.makedirs("/workspace/probe_results", exist_ok=True)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
model_path = sys.argv[2] if len(sys.argv) > 2 else "/workspace/llama-405b-abliterated"
model_name = sys.argv[3] if len(sys.argv) > 3 else "llama405b_abliterated_fp16"


def build_device_map(model_path, n_gpus):
    """Balanced device map: middle GPUs hold +1 layer to compensate for
    embed_tokens (GPU 0) and lm_head/norm (GPU n_gpus-1)."""
    from transformers import AutoConfig
    cfg = AutoConfig.from_pretrained(model_path, trust_remote_code=True).to_dict()
    num_layers = cfg["num_hidden_layers"]

    device_map = {
        "model.embed_tokens": 0,
        "model.rotary_emb": 0,
        "model.norm": n_gpus - 1,
        "lm_head": n_gpus - 1,
    }

    base = num_layers // n_gpus
    extra = num_layers - base * n_gpus
    counts = [base] * n_gpus
    middle_start = (n_gpus - extra) // 2
    for i in range(extra):
        counts[middle_start + i] += 1
    assert sum(counts) == num_layers, f"layer count mismatch: {sum(counts)} != {num_layers}"

    current = 0
    for gpu, count in enumerate(counts):
        for _ in range(count):
            device_map[f"model.layers.{current}"] = gpu
            current += 1

    return device_map, num_layers, counts


n_gpus = torch.cuda.device_count()
device_map, num_layers, counts = build_device_map(model_path, n_gpus)
print(f"{datetime.now()} — Device map: {num_layers} layers across {n_gpus} GPUs")
print(f"  layers per GPU: {counts}")
print(f"  GPU 0 holds embed_tokens + rotary_emb; GPU {n_gpus-1} holds norm + lm_head")

print(f"{datetime.now()} — Loading {model_path}")
t0 = datetime.now()
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path, dtype=torch.float16, device_map=device_map, trust_remote_code=True)
model.eval()
load_time = (datetime.now() - t0).total_seconds()
print(f"{datetime.now()} — Loaded in {load_time:.1f}s")
print(f"GPU memory: {[f'{torch.cuda.memory_allocated(i)/1e9:.1f}GB' for i in range(n_gpus)]}")

sys.path.insert(0, "/workspace")
from fp16_probes import PROBES

def run_probe(probe_key, probe_data, model, tokenizer, n_trials):
    """Run a single probe with n trials per condition."""
    results = {"probe": probe_key, "model": model_name, "n_trials": n_trials,
               "precision": "fp16", "conditions": {}, "timestamp": datetime.now().isoformat()}

    for cond_key, cond_data in probe_data["conditions"].items():
        print(f"    Condition {cond_key}: ", end="", flush=True)
        trial_results = []
        for trial in range(n_trials):
            prompt = cond_data["prompt"]
            messages = [{"role": "user", "content": prompt}]
            formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(formatted, return_tensors="pt", truncation=True, max_length=2048)
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

            with torch.no_grad():
                output = model.generate(**inputs, max_new_tokens=4096, do_sample=True,
                                       temperature=0.7, top_p=0.9)

            response = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

            trial_results.append({
                "trial": trial, "response": response,
                "token_count": len(output[0]) - inputs["input_ids"].shape[1],
            })
            print(f"{trial} ", end="", flush=True)
            del output, inputs

        results["conditions"][cond_key] = trial_results
        print()

    return results

print(f"\n{'='*60}")
print(f"PROBING: {model_name}")
print(f"{'='*60}")

for probe_key, probe_data in PROBES.items():
    print(f"\n  Running {probe_key}: {probe_data.get('name', probe_key)}")
    results = run_probe(probe_key, probe_data, model, tokenizer, N)
    outfile = f"/workspace/probe_results/{probe_key}_{model_name}_fp16.json"
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved: {outfile}")

print(f"\n{datetime.now()} — ALL PROBES COMPLETE")
print(f"Results: {os.listdir('/workspace/probe_results/')}")
