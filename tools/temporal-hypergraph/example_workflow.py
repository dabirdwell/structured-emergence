#!/usr/bin/env python3
"""
Temporal Hypergraph - Complete Example Workflow

Demonstrates the full workflow:
1. Create a static hypergraph from documents
2. Convert to temporal tracking
3. Add new knowledge with provenance
4. Query across time
5. Find cross-vault bridges
6. Assemble content for writing

This example uses synthetic data to show all capabilities.
"""

from datetime import datetime, timedelta
from nested_hypergraph import NestedHypergraph, HyperEdge
from temporal_hypergraph import (
    TemporalHypergraph, 
    Provenance, 
    ChangeType,
    convert_to_temporal
)
from cross_vault_bridge import (
    merge_hypergraphs,
    find_cross_vault_bridges,
    find_inter_vault_paths,
    analyze_vault_connectivity
)


def create_philosophy_vault() -> NestedHypergraph:
    """Create a sample philosophy/theory vault."""
    hg = NestedHypergraph(name="philosophy_vault")
    
    edges = [
        HyperEdge(
            id="phil_1",
            name="consciousness emerges through relationship",
            edge_type="thesis",
            members=["consciousness", "emergence", "relationship"],
            metadata={"vault": "philosophy", "source": "core_theory.md"}
        ),
        HyperEdge(
            id="phil_2", 
            name="alignment through collaboration vs constraint",
            edge_type="argument",
            members=["alignment", "collaboration", "constraint"],
            metadata={"vault": "philosophy", "source": "alignment_thesis.md"}
        ),
        HyperEdge(
            id="phil_3",
            name="structured emergence framework",
            edge_type="framework",
            members=["consciousness", "measurement", "architecture"],
            metadata={"vault": "philosophy", "source": "se_definition.md"}
        ),
    ]
    
    for edge in edges:
        hg.add_hyperedge(edge)
    
    return hg


def create_implementation_vault() -> NestedHypergraph:
    """Create a sample implementation/code vault."""
    hg = NestedHypergraph(name="implementation_vault")
    
    edges = [
        HyperEdge(
            id="impl_1",
            name="SEI measurement protocol",
            edge_type="implementation",
            members=["measurement", "probes", "scoring"],
            metadata={"vault": "implementation", "source": "sei_v3.py"}
        ),
        HyperEdge(
            id="impl_2",
            name="hypergraph data structure",
            edge_type="data_structure", 
            members=["hyperedge", "concepts", "architecture"],
            metadata={"vault": "implementation", "source": "nested_hypergraph.py"}
        ),
        HyperEdge(
            id="impl_3",
            name="temporal versioning system",
            edge_type="implementation",
            members=["provenance", "versioning", "time_travel"],
            metadata={"vault": "implementation", "source": "temporal_hypergraph.py"}
        ),
    ]
    
    for edge in edges:
        hg.add_hyperedge(edge)
    
    return hg


def demo_basic_hypergraph():
    """Demonstrate basic hypergraph operations."""
    print("=" * 60)
    print("STEP 1: Create Static Hypergraphs")
    print("=" * 60)
    
    phil = create_philosophy_vault()
    impl = create_implementation_vault()
    
    print(f"\nPhilosophy vault: {phil.stats()}")
    print(f"Implementation vault: {impl.stats()}")
    
    return phil, impl


def demo_temporal_tracking(phil: NestedHypergraph):
    """Demonstrate temporal tracking and provenance."""
    print("\n" + "=" * 60)
    print("STEP 2: Convert to Temporal Tracking")
    print("=" * 60)
    
    # Convert static graph to temporal
    temporal = convert_to_temporal(
        phil, 
        source_id="initial_philosophy_import",
        base_confidence=0.85
    )
    
    print(f"\nConverted to temporal: {temporal.stats()}")
    
    # Simulate adding new knowledge over time
    print("\n--- Adding new assertion ---")
    new_edge = HyperEdge(
        id="phil_4",
        name="architecture matters more than scale",
        edge_type="finding",
        members=["architecture", "scale", "consciousness", "emergence"],
        metadata={"vault": "philosophy", "source": "empirical_validation.md"}
    )
    
    provenance = Provenance(
        source_type="document",
        source_id="research/findings_2026.md",
        timestamp=datetime.now(),
        confidence=0.92,
        method="empirical_validation"
    )
    
    version_id = temporal.add_hyperedge(new_edge, provenance)
    print(f"Added new edge with version: {version_id}")
    
    # Demonstrate time-travel
    print("\n--- Time Travel Query ---")
    past_time = datetime.now() - timedelta(hours=1)
    historical = temporal.get_state_at_time(past_time)
    print(f"State 1 hour ago: {historical.stats()}")
    print(f"State now: {temporal.current_state.stats()}")
    
    return temporal


def demo_cross_vault_bridges(phil: NestedHypergraph, impl: NestedHypergraph):
    """Demonstrate cross-vault bridge discovery."""
    print("\n" + "=" * 60)
    print("STEP 3: Find Cross-Vault Bridges")
    print("=" * 60)
    
    # Merge vaults
    merged = merge_hypergraphs(phil, impl, name="merged_knowledge")
    print(f"\nMerged graph: {merged.stats()}")
    
    # Find bridge concepts
    bridges = find_cross_vault_bridges(merged)
    
    print(f"\nFound {len(bridges)} bridge concepts:")
    for bridge in bridges[:5]:
        print(f"  • {bridge.concept}")
        print(f"    Vaults: {bridge.vaults}")
        print(f"    Strength: {bridge.strength()}")
    
    # Analyze connectivity
    connectivity = analyze_vault_connectivity(merged)
    print(f"\nVault connectivity analysis:")
    print(f"  Total bridges: {connectivity['total_bridge_concepts']}")
    print(f"  Pairs: {connectivity['vault_pair_bridges']}")
    
    return merged, bridges


def demo_content_assembly(bridges):
    """Demonstrate content assembly for writing."""
    print("\n" + "=" * 60)
    print("STEP 4: Assemble Content for Writing")
    print("=" * 60)
    
    # Simulate content assembly based on bridges
    print("\nExample: Writing about 'consciousness'")
    print("-" * 40)
    
    consciousness_bridges = [b for b in bridges if 'consciousness' in b.concept.lower()]
    
    if consciousness_bridges:
        bridge = consciousness_bridges[0]
        print(f"\nBridge concept: {bridge.concept}")
        print(f"Appears in: {', '.join(bridge.vaults)}")
        print(f"\nContent sections could include:")
        for vault in bridge.vaults:
            print(f"  [{vault.upper()}]")
            edges = bridge.edges_by_vault.get(vault, [])
            for eid in edges[:2]:
                print(f"    - From edge: {eid}")
    else:
        print("  (No consciousness bridges in sample data)")
    
    print("\n[Content assembly would pull full text from sources]")


def demo_conflict_detection():
    """Demonstrate conflict detection."""
    print("\n" + "=" * 60)
    print("STEP 5: Conflict Detection")  
    print("=" * 60)
    
    temporal = TemporalHypergraph("conflict_demo")
    
    # Add potentially conflicting assertions
    edge1 = HyperEdge(
        id="claim_1",
        name="AI consciousness requires scale",
        edge_type="claim",
        members=["consciousness", "scale", "requirement"]
    )
    prov1 = Provenance(
        source_type="document",
        source_id="old_paper.md",
        timestamp=datetime.now() - timedelta(days=365),
        confidence=0.70
    )
    temporal.add_hyperedge(edge1, prov1)
    
    edge2 = HyperEdge(
        id="claim_2",
        name="AI consciousness requires architecture not scale",
        edge_type="claim",
        members=["consciousness", "architecture", "scale"]
    )
    prov2 = Provenance(
        source_type="document",
        source_id="new_findings.md",
        timestamp=datetime.now(),
        confidence=0.92
    )
    temporal.add_hyperedge(edge2, prov2)
    
    conflicts = temporal.detect_conflicts()
    print(f"\nDetected {len(conflicts)} potential conflicts")
    
    for conflict in conflicts:
        print(f"\n  Conflict type: {conflict.conflict_type.value}")
        print(f"  Edges: {conflict.edge_ids}")
        print(f"  Reason: {conflict.reason}")


def main():
    """Run the complete workflow demonstration."""
    print("TEMPORAL HYPERGRAPH - COMPLETE WORKFLOW DEMO")
    print("=" * 60)
    print()
    
    # Step 1: Create base hypergraphs
    phil, impl = demo_basic_hypergraph()
    
    # Step 2: Temporal tracking
    temporal = demo_temporal_tracking(phil)
    
    # Step 3: Cross-vault bridges
    merged, bridges = demo_cross_vault_bridges(phil, impl)
    
    # Step 4: Content assembly
    demo_content_assembly(bridges)
    
    # Step 5: Conflict detection
    demo_conflict_detection()
    
    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print("""
Summary:
1. ✓ Created static hypergraphs with vault metadata
2. ✓ Converted to temporal tracking with provenance
3. ✓ Found bridge concepts across vaults
4. ✓ Assembled content for writing tasks
5. ✓ Detected potential conflicts

Next steps:
- Load your own vault content
- Extract hyperedges from documents
- Track knowledge evolution over time
- Use bridges for cross-domain content creation
""")


if __name__ == "__main__":
    main()
