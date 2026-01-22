#!/usr/bin/env python3
"""
Cross-Vault Bridge Finder

Discovers conceptual bridges between separate knowledge bases (vaults).
The most valuable connections often happen at the intersection of different domains:
- Where philosophy meets application
- Where theory meets implementation
- Where research meets practice

Part of the Temporal Hypergraph toolkit.
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict
from dataclasses import dataclass

from nested_hypergraph import NestedHypergraph, HyperEdge


@dataclass
class BridgeConcept:
    """A concept that appears in multiple vaults."""
    concept: str
    vaults: List[str]
    edges_by_vault: Dict[str, List[str]]
    total_edges: int
    
    def strength(self) -> float:
        """Bridge strength based on presence across vaults."""
        return self.total_edges * len(self.vaults)


@dataclass 
class InterVaultPath:
    """A path connecting concepts across vault boundaries."""
    from_concept: str
    from_vault: str
    to_concept: str
    to_vault: str
    hops: int
    path: List[str]
    via_edges: List[str]
    vault_crossings: int


def merge_hypergraphs(*hypergraphs: NestedHypergraph, 
                      name: str = "merged") -> NestedHypergraph:
    """
    Merge multiple hypergraphs, preserving vault metadata for bridge detection.
    
    Args:
        *hypergraphs: Variable number of hypergraphs to merge
        name: Name for the merged hypergraph
        
    Returns:
        A new NestedHypergraph containing all edges from input graphs
    """
    merged = NestedHypergraph(name=name)
    
    for hg in hypergraphs:
        for edge_id, edge in hg.hyperedges.items():
            merged.add_hyperedge(edge)
    
    return merged


def find_cross_vault_bridges(merged: NestedHypergraph) -> List[BridgeConcept]:
    """
    Find concepts that bridge between vaults.
    
    A bridge concept appears in hyperedges from MULTIPLE vaults.
    These represent the intersection points between different knowledge domains.
    
    Args:
        merged: A merged hypergraph with vault metadata on edges
        
    Returns:
        List of BridgeConcept objects sorted by strength (strongest first)
    """
    # Index concepts by vault
    vault_concepts = defaultdict(lambda: defaultdict(set))
    
    for edge_id, edge in merged.hyperedges.items():
        vault = edge.metadata.get('vault', 'unknown')
        for concept in edge.get_all_atomic_concepts():
            vault_concepts[vault][concept].add(edge_id)
    
    all_vaults = list(vault_concepts.keys())
    bridges = []
    
    # Find concepts appearing in multiple vaults
    for concept in merged.concept_index.keys():
        concept_vaults = set()
        concept_edges = {}
        
        for vault in all_vaults:
            if concept in vault_concepts[vault]:
                concept_vaults.add(vault)
                concept_edges[vault] = list(vault_concepts[vault][concept])
        
        if len(concept_vaults) > 1:
            bridge = BridgeConcept(
                concept=concept,
                vaults=list(concept_vaults),
                edges_by_vault=concept_edges,
                total_edges=sum(len(v) for v in concept_edges.values())
            )
            bridges.append(bridge)
    
    # Sort by strength
    bridges.sort(key=lambda x: -x.strength())
    return bridges


def find_inter_vault_paths(merged: NestedHypergraph, 
                           concept_a: str, vault_a: str,
                           concept_b: str, vault_b: str,
                           max_hops: int = 5,
                           max_paths: int = 10) -> List[InterVaultPath]:
    """
    Find paths from a concept in one vault to a concept in another vault.
    
    These paths show how ideas flow between different knowledge domains.
    
    Args:
        merged: Merged hypergraph with vault metadata
        concept_a: Starting concept
        vault_a: Starting vault
        concept_b: Target concept  
        vault_b: Target vault
        max_hops: Maximum path length (default 5)
        max_paths: Maximum paths to return (default 10)
        
    Returns:
        List of InterVaultPath objects
    """
    # Get starting edges (only from source vault)
    edges_a = set()
    for edge_id in merged.concept_index.get(concept_a, set()):
        if merged.hyperedges[edge_id].metadata.get('vault') == vault_a:
            edges_a.add(edge_id)
    
    # Get target edges (only from target vault)
    edges_b = set()
    for edge_id in merged.concept_index.get(concept_b, set()):
        if merged.hyperedges[edge_id].metadata.get('vault') == vault_b:
            edges_b.add(edge_id)
    
    if not edges_a or not edges_b:
        return []
    
    paths = []
    visited = set()
    queue = [(edges_a, [concept_a], [], vault_a)]
    
    while queue and len(paths) < max_paths:
        current_edges, concept_path, edge_path, current_vault = queue.pop(0)
        
        if len(concept_path) > max_hops:
            continue
        
        for eid in current_edges:
            if eid in visited:
                continue
            visited.add(eid)
            
            edge = merged.hyperedges[eid]
            edge_vault = edge.metadata.get('vault', 'unknown')
            atoms = edge.get_all_atomic_concepts()
            
            # Check if we've reached the target
            if concept_b in atoms and edge_vault == vault_b:
                # Count vault crossings in edge path
                vault_crossings = 0
                for i, ename in enumerate(edge_path):
                    if i > 0:
                        # Would need edge -> vault lookup for exact count
                        pass
                
                path = InterVaultPath(
                    from_concept=concept_a,
                    from_vault=vault_a,
                    to_concept=concept_b,
                    to_vault=vault_b,
                    hops=len(concept_path) - 1,
                    path=concept_path + [concept_b],
                    via_edges=edge_path + [edge.name],
                    vault_crossings=1 if vault_a != vault_b else 0
                )
                paths.append(path)
                continue
            
            # Expand search
            for atom in atoms:
                if atom in concept_path:
                    continue
                adjacent_edges = merged.concept_index.get(atom, set())
                if adjacent_edges - visited:
                    queue.append((
                        adjacent_edges - visited,
                        concept_path + [atom],
                        edge_path + [edge.name],
                        edge_vault
                    ))
    
    return paths


def analyze_vault_connectivity(merged: NestedHypergraph) -> Dict:
    """
    Analyze how well-connected different vaults are to each other.
    
    Returns statistics about cross-vault connectivity.
    """
    vault_pairs = defaultdict(int)
    vault_edges = defaultdict(int)
    
    bridges = find_cross_vault_bridges(merged)
    
    for bridge in bridges:
        for i, v1 in enumerate(bridge.vaults):
            vault_edges[v1] += len(bridge.edges_by_vault.get(v1, []))
            for v2 in bridge.vaults[i+1:]:
                pair = tuple(sorted([v1, v2]))
                vault_pairs[pair] += 1
    
    return {
        'total_bridge_concepts': len(bridges),
        'vault_pair_bridges': dict(vault_pairs),
        'edges_per_vault': dict(vault_edges),
        'strongest_bridges': [
            {
                'concept': b.concept,
                'vaults': b.vaults,
                'strength': b.strength()
            }
            for b in bridges[:10]
        ]
    }


def find_theme_bridges(merged: NestedHypergraph, 
                       themes: List[str]) -> Dict[str, List[BridgeConcept]]:
    """
    Find bridge concepts related to specific themes.
    
    Useful for content creation: "What bridges connect consciousness to infrastructure?"
    
    Args:
        merged: Merged hypergraph
        themes: List of theme concepts to search for
        
    Returns:
        Dict mapping each theme to related bridge concepts
    """
    all_bridges = find_cross_vault_bridges(merged)
    theme_bridges = {theme: [] for theme in themes}
    
    for bridge in all_bridges:
        # Check if this bridge connects to any themes
        bridge_concepts = set()
        for vault_edges in bridge.edges_by_vault.values():
            for edge_id in vault_edges:
                edge = merged.hyperedges.get(edge_id)
                if edge:
                    bridge_concepts.update(edge.get_all_atomic_concepts())
        
        for theme in themes:
            theme_lower = theme.lower()
            if (theme_lower in bridge.concept.lower() or 
                any(theme_lower in c.lower() for c in bridge_concepts)):
                theme_bridges[theme].append(bridge)
    
    return theme_bridges


# Example usage
if __name__ == '__main__':
    print("Cross-Vault Bridge Finder")
    print("=" * 60)
    print()
    print("Usage:")
    print("  from cross_vault_bridge import merge_hypergraphs, find_cross_vault_bridges")
    print()
    print("  # Load and merge hypergraphs from different vaults")
    print("  vault1 = NestedHypergraph.load('philosophy.pkl')")
    print("  vault2 = NestedHypergraph.load('implementation.pkl')")
    print("  merged = merge_hypergraphs(vault1, vault2)")
    print()
    print("  # Find bridge concepts")
    print("  bridges = find_cross_vault_bridges(merged)")
    print("  for b in bridges[:10]:")
    print("      print(f'{b.concept}: {b.vaults} ({b.strength()} strength)')")
    print()
    print("  # Find paths between vaults")
    print("  paths = find_inter_vault_paths(merged, 'consciousness', 'philosophy',")
    print("                                  'infrastructure', 'implementation')")
