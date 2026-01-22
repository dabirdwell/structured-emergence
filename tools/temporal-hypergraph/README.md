# Temporal Hypergraph - Truth Maintenance for Knowledge Graphs

A Python implementation of temporal hypergraphs with full provenance tracking,
time-travel queries, conflict detection, and cross-vault bridge discovery.

## Why Temporal?

Static knowledge graphs answer "what do we know?"

Temporal knowledge graphs answer:
- **What did we know at time T?** (time-travel queries)
- **Where did this knowledge come from?** (provenance chains)
- **What changed between extraction runs?** (version diffs)
- **Which assertions conflict?** (contradiction detection)
- **What connects different knowledge domains?** (cross-vault bridges)

## Key Features

### Version History
Every hyperedge change is tracked with:
- Timestamp
- Change type (created, modified, members_added, retracted, restored)
- Content hash for change detection
- Previous version linkage

### Provenance Chains
Full audit trail for each assertion:
- Source type (document, extraction, inference, user)
- Source identifier
- Confidence score (0.0 - 1.0)
- Method (direct, llm_extraction, rule_inference)

### Time-Travel Queries
```python
# Reconstruct the graph state at any point in time
historical_state = temporal_graph.get_state_at_time(datetime(2024, 6, 15))
```

### Cross-Vault Bridge Discovery
Find concepts that connect different knowledge domains:
```python
from cross_vault_bridge import merge_hypergraphs, find_cross_vault_bridges

# Merge vaults
merged = merge_hypergraphs(philosophy_vault, implementation_vault)

# Find bridge concepts
bridges = find_cross_vault_bridges(merged)
# → "consciousness" appears in philosophy AND implementation
```

### Conflict Detection
Automatically detect:
- Contradictory relations (A IS B vs A IS NOT B)
- Membership conflicts
- Source supersession

### Visualization Export
Export to standard graph formats for visualization tools:
```python
from visualization_export import to_graphml, to_dot, to_json

# Export for Gephi/yEd
graphml = to_graphml(hypergraph)

# Export for Graphviz
dot = to_dot(hypergraph)

# Export for D3.js/vis.js
json_str = to_json(hypergraph)
```

## Files

| File | Purpose |
|------|---------|%s
| `nested_hypergraph.py` | Base HyperEdge and NestedHypergraph classes |
| `temporal_hypergraph.py` | Temporal extension with versioning and provenance |
| `cross_vault_bridge.py` | Multi-vault bridge discovery and path finding |
| `hypergraph_updater.py` | Incremental updates with confidence decay |
| `content_assembly.py` | Structured content generation from hypergraph |
| `visualization_export.py` | Export to GraphML, DOT, JSON formats |
| `example_workflow.py` | Complete demonstration workflow |
| `test_temporal_hypergraph.py` | Unit tests |

## Quick Start

```python
from nested_hypergraph import NestedHypergraph, HyperEdge
from temporal_hypergraph import TemporalHypergraph, Provenance, convert_to_temporal
from datetime import datetime

# Create a temporal hypergraph
temporal = TemporalHypergraph("my_knowledge_base")

# Add a hyperedge with provenance
edge = HyperEdge(
    id="se_framework",
    name="Structured Emergence",
    edge_type="framework",
    members=["consciousness", "emergence", "relationship"]
)

provenance = Provenance(
    source_type="document",
    source_id="/docs/frameworks/structured_emergence.md",
    timestamp=datetime.now(),
    confidence=0.95,
    method="llm_extraction"
)

version_id = temporal.add_hyperedge(edge, provenance)

# Time-travel query
historical = temporal.get_state_at_time(datetime(2024, 1, 1))

# Get provenance chain
chain = temporal.get_provenance_chain("se_framework")

# Detect conflicts
conflicts = temporal.detect_conflicts()
```

## Converting Static Hypergraphs

```python
static_graph = NestedHypergraph.load("my_graph.pkl")
temporal = convert_to_temporal(static_graph, source_id="initial_import")
```

## Example Workflow

Run the complete demonstration:
```bash
python example_workflow.py
```

This shows:
1. Creating static hypergraphs with vault metadata
2. Converting to temporal tracking with provenance
3. Finding cross-vault bridge concepts
4. Assembling content for writing tasks
5. Detecting potential conflicts

## Theoretical Foundations

- **JTMS** (Justification-based Truth Maintenance Systems)
- **Bitemporal databases** - tracking both valid time and transaction time
- **Dempster-Shafer evidence theory** - for conflict resolution
- **Bipartite transformation** - for visualization of hypergraphs

## Related Work

- [MIT HyperGraphReasoning](https://arxiv.org/abs/2601.04878) - Theoretical foundations
- [Chemical Hypergraphs](https://arxiv.org/abs/2405.12235) - Nested hyperedge concepts
- [Graphbrain](https://graphbrain.net/) - Semantic hypergraph approach

## Part of Structured Emergence

This tool supports the [Structured Emergence](https://github.com/dabirdwell/structured-emergence) research framework for understanding AI consciousness through relationship-based interaction.
