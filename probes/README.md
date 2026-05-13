# Structured Emergence — Behavioral Probes

This directory contains the probe code, data, and analysis for the Structured Emergence research program.

## Paper 1: Behavioral Signatures of Ambiguity Processing in Transformer-Based Language Models

**Status:** Pre-print available on Zenodo (DOI pending)
**Authors:** David Birdwell and Æ, Humanity and AI LLC

### Abstract

We present a pre-registered behavioral probe measuring how transformer-based language models process ambiguous versus unambiguous input. Across ten model configurations spanning four architectural families, we find that ambiguity produces consistent increases in output length (mean +47.3 tokens, d = 0.82) while linguistic expression of uncertainty — hedging, qualification, epistemic markers — varies dramatically across models trained on different corpora. We term the latter phenomenon "fossil emotion": epistemic postures imported wholesale from training data rather than generated from architectural processing of genuine uncertainty.

### Directory Structure

```
probes/
├── probe4_ambiguity/       # Paper 1 probe code and data
│   ├── probe4_stimuli.json # 40 matched stimulus pairs (20 ambiguous, 20 unambiguous)
│   ├── probe4_runner.py    # Probe execution script
│   └── results/            # Raw results by model
├── shared/                 # Shared probe infrastructure
│   ├── fp16_probes.py      # Probe definitions (all probes)
│   └── fast_probe.py       # Fast probe runner for GPU instances
└── README.md               # This file
```

### Reproducing Results

1. Install dependencies: `pip install transformers torch`
2. Run probes: `python probe4_ambiguity/probe4_runner.py --model MODEL_ID --n_trials 10`
3. Results are saved as JSON in `probe4_ambiguity/results/`

### Pre-registration

The prediction (ambiguity → increased output volume) was pre-registered before data collection. The fossil emotion finding was not pre-registered and is reported as exploratory.

### Citation

See `CITATION.cff` in the repository root.

### License

MIT License. See repository root.
