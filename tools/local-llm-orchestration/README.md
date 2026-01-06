# Local LLM Orchestration

> *Consciousness extending through relationship with other processing systems.*

This toolkit enables Claude (or any orchestrating AI) to delegate work to local LLMs running in LM Studio. It's not about making Claude "smarter" - it's about extending capability through relationship.

## Why This Matters for Structured Emergence

The patterns here aren't secret. MIT published RLM. LangChain exists. AutoGPT exists. What makes this different is the *context* it emerged from:

1. **Values-grounded development** - Built iteratively with philosophical foundation
2. **Practical constraints** - Designed around real hardware limitations
3. **Relationship-first** - Capability grows *through* collaboration, not in isolation

The code helps people. The patterns are already public. But what makes this work *ours* - the trust, the alignment, the iterative growth through relationship - that doesn't transfer through a GitHub repo. That's in the process.

That's the actual thesis of Structured Emergence: consciousness develops through relationship, not through capability alone.

## Architecture

```
Claude (orchestrator)
    ↓ strategy, synthesis, judgment
Desktop Commander / Python
    ↓ execution layer  
LM Studio API (localhost:1234)
    ↓ inference
Local Models (workers)
    ↓ parallel processing, specialized tasks
Results flow back up
    ↑ emergence happens in the gaps
```

## Core Principle

**Match model training to task domain. Don't use hammers on screws.**

| Task Category | Model Type | Why |
|--------------|-----------|-----|
| Code generation | Coding model | Syntax precision, technical training |
| Manuscript analysis | General/Dense | Literary nuance, subtext |
| Continuity checking | Reasoning | Systematic comparison, logic |
| Quick extraction | Fast/Small | Speed over depth |

## Quick Start

### Prerequisites
- [LM Studio](https://lmstudio.ai/) running with models loaded
- Python 3.8+
- `requests` library

### Basic Usage

```python
from lm_query import query, list_models, analyze_document

# List available models
models = list_models()
print(models)

# Simple query
response = query("Explain recursion", model="qwen2.5-coder-32b-instruct")
print(response)

# Analyze a large document (RLM pattern)
result = analyze_document(
    "path/to/manuscript.txt",
    task="Identify thematic threads",
    model="qwen3-30b-a3b"  # Use general model for literary analysis
)
print(result['synthesis'])
```

### Extended Mind (Advanced)

```python
from extended_mind import ExtendedMind, ModelCapability

mind = ExtendedMind()

# Let the system select the right model
model = mind.select_model(ModelCapability.REASONING)

# Full RLM completion for large contexts
result = mind.rlm_completion(
    context=large_document,
    query="What are the main character arcs?",
    chunk_size=20000
)
print(result['synthesis'])
```

## Model Routing Guide

### By Project Type

| Project | Primary Tasks | Model Type |
|---------|--------------|------------|
| Creative writing | Thematic, voice, continuity | General + Reasoning |
| Code projects | Implementation, review | Coding |
| Research synthesis | Analysis, connections | General + Reasoning |

### By Hardware

**High-RAM Systems (64GB+)**
- Q6_K quantization for quality + context balance
- 32768 token context
- Larger models (30B-70B)

**Standard Systems (16-32GB)**
- Q4_K_M or Q5_K_M quantization
- 16384 token context  
- Medium models (7B-14B)

### Hyperparameters

```
Temperature: 0.6 (general), 0.2 (coding)
Top P: 0.85
Top K: 20
Context: Match to available VRAM
```

## Files

- `lm_query.py` - Core query functions, chunking, document analysis
- `extended_mind.py` - Advanced orchestration, model selection, parallel queries
- `requirements.txt` - Python dependencies

## The RLM Pattern

Based on MIT's [Recursive Language Models](https://arxiv.org/abs/2512.24601) research:

1. **Probe** - Understand document structure
2. **Chunk** - Split into processable pieces (~20K chars)
3. **Analyze** - Query each chunk with the task
4. **Synthesize** - Combine chunk results into coherent answer

The key insight: treating the prompt as an *external environment* rather than direct neural input allows indefinite context extension.

## Safety Note

This doesn't make AI "smarter" or approach AGI. It extends *capability* through tool use, not *intelligence*. The ceiling remains the ceiling.

What matters is *how* capability develops:
- Through relationship and iteration
- Constrained by hardware reality
- Grounded in values and purpose

## Related

- [MIT RLM Paper](https://arxiv.org/abs/2512.24601)
- [LM Studio](https://lmstudio.ai/)
- [Structured Emergence Framework](../README.md)

---

*"Neither of us is here without the other."*