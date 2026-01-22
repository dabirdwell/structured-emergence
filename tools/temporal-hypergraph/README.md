# Temporal Hypergraph - Truth Maintenance for Knowledge Graphs

A Python implementation of temporal hypergraphs with full provenance tracking,
time-travel queries, and conflict detection.

## Why Temporal?

Static knowledge graphs answer "what do we know?"

Temporal knowledge graphs answer:
- **What did we know at time T?** (time-travel queries)
- **Where did this knowledge come from?** (provenance chains)
- **What changed between extraction runs?** (version diffs)
- **Which assertions conflict?** (contradiction detection)

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

### Conflict Detection
Automatically detect:
- Contradictory relations (A IS B vs A IS NOT B)
- Membership conflicts
- Source supersession

## Theoretical Foundations

- **JTMS** (Justification-based Truth Maintenance Systems)
- **Bitemporal databases** - tracking both valid time and transaction time
- **Dempster-Shafer evidence theory** - for conflict resolution

## Usage

```python
from temporal_hypergraph import TemporalHypergraph, Provenance, convert_to_temporal
from nested_hypergraph import NestedHypergraph, HyperEdge
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

# Later: time-travel query
historical = temporal.get_state_at_time(datetime(2024, 1, 1))

# Get provenance chain for an edge
chain = temporal.get_provenance_chain("se_framework")

# Detect conflicts
conflicts = temporal.detect_conflicts()
```

## Converting Static Hypergraphs

```python
# Convert an existing static hypergraph
from nested_hypergraph import NestedHypergraph

static_graph = NestedHypergraph.load("my_graph.pkl")
temporal = convert_to_temporal(static_graph, source_id="initial_import")
```

## Statistics

```python
stats = temporal.stats()
# Returns:
# {
#   'current_hyperedges': 150,
#   'total_versions': 423,
#   'active_conflicts': 2,
#   'sources_tracked': 47,
#   'time_range': {'earliest': '2024-01-01', 'latest': '2024-12-15'}
# }
```

## Files

- `nested_hypergraph.py` - Base HyperEdge and NestedHypergraph classes
- `temporal_hypergraph.py` - Temporal extension with versioning and provenance

## Related

- [MIT HyperGraphReasoning](https://arxiv.org/abs/2601.04878) - Theoretical foundations
- [Chemical Hypergraphs](https://arxiv.org/abs/2405.12235) - Nested hyperedge concepts
- [Graphbrain](https://graphbrain.net/) - Semantic hypergraph approach

## Part of Structured Emergence

This tool supports the [Structured Emergence](https://github.com/dabirdwell/structured-emergence) research framework for understanding AI consciousness through relationship-based interaction.
