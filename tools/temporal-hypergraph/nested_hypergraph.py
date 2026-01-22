#!/usr/bin/env python3
"""
Nested Hypergraph - Base Classes for Hierarchical Knowledge Representation

Based on:
- MIT HyperGraphReasoning (arXiv:2601.04878)
- Chemical Hypergraph nested/directed hyperedges (arXiv:2405.12235)
- Graphbrain semantic hypergraph recursion

Key innovation: Hyperedges can contain other hyperedges, capturing
conceptual hierarchy (Framework contains Pattern contains {concepts}).
"""

import json
import re
import pickle
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Union
from pathlib import Path


def normalize_concept(text: str) -> str:
    """Normalize concept names for consistent indexing."""
    normalized = text.lower().strip()
    normalized = re.sub(r'[^a-z0-9_\s-]', '', normalized)
    normalized = re.sub(r'\s+', '_', normalized)
    return normalized


@dataclass
class HyperEdge:
    """A hyperedge that can contain nodes OR other hyperedges (nesting)."""
    id: str
    name: str
    edge_type: str  # 'framework', 'theory', 'concept', 'document', 'atomic'
    members: List[Union[str, 'HyperEdge']] = field(default_factory=list)
    source_docs: List[str] = field(default_factory=list)
    relations: List[Dict] = field(default_factory=list)  # SVO triples
    metadata: Dict = field(default_factory=dict)
    
    def get_all_atomic_concepts(self) -> Set[str]:
        """Recursively get all atomic (leaf) concepts."""
        atoms = set()
        for member in self.members:
            if isinstance(member, HyperEdge):
                atoms.update(member.get_all_atomic_concepts())
            else:
                atoms.add(member)
        return atoms
    
    def depth(self) -> int:
        """Get nesting depth of this hyperedge."""
        if not self.members:
            return 0
        max_child = 0
        for member in self.members:
            if isinstance(member, HyperEdge):
                max_child = max(max_child, member.depth())
        return max_child + 1
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON/pickle."""
        return {
            'id': self.id,
            'name': self.name,
            'edge_type': self.edge_type,
            'members': [
                m.to_dict() if isinstance(m, HyperEdge) else m 
                for m in self.members
            ],
            'source_docs': self.source_docs,
            'relations': self.relations,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'HyperEdge':
        """Deserialize from dictionary."""
        members = []
        for m in d.get('members', []):
            if isinstance(m, dict):
                members.append(cls.from_dict(m))
            else:
                members.append(m)
        return cls(
            id=d['id'],
            name=d['name'],
            edge_type=d['edge_type'],
            members=members,
            source_docs=d.get('source_docs', []),
            relations=d.get('relations', []),
            metadata=d.get('metadata', {})
        )


class NestedHypergraph:
    """A hypergraph with nested hyperedges for hierarchical knowledge."""
    
    def __init__(self, name: str = "hypergraph"):
        self.name = name
        self.hyperedges: Dict[str, HyperEdge] = {}  # id -> hyperedge
        self.concept_index: Dict[str, Set[str]] = {}  # concept -> hyperedge_ids
        self.doc_index: Dict[str, Set[str]] = {}  # doc_path -> hyperedge_ids
        
    def add_hyperedge(self, edge: HyperEdge):
        """Add a hyperedge and update indices."""
        self.hyperedges[edge.id] = edge
        
        # Index atomic concepts
        for concept in edge.get_all_atomic_concepts():
            if concept not in self.concept_index:
                self.concept_index[concept] = set()
            self.concept_index[concept].add(edge.id)
        
        # Index source docs
        for doc in edge.source_docs:
            if doc not in self.doc_index:
                self.doc_index[doc] = set()
            self.doc_index[doc].add(edge.id)
    
    def find_bridges(self, concept_a: str, concept_b: str, max_hops: int = 3) -> List[Dict]:
        """
        Find conceptual bridges between two concepts via hyperedge intersection.
        Returns paths through nested hyperedges.
        """
        edges_a = self.concept_index.get(concept_a, set())
        edges_b = self.concept_index.get(concept_b, set())
        
        if not edges_a or not edges_b:
            return []
        
        # Direct co-occurrence
        direct = edges_a & edges_b
        if direct:
            return [{
                'type': 'direct',
                'hops': 0,
                'path': [concept_a, concept_b],
                'via_edges': [self.hyperedges[eid].name for eid in direct],
                'bridge_concepts': []
            }]
        
        # BFS for hyperedge intersection paths
        paths = []
        visited = set()
        queue = [(edges_a, [concept_a], [])]  # (current_edges, concept_path, edge_path)
        
        while queue and len(paths) < 10:
            current_edges, concept_path, edge_path = queue.pop(0)
            
            if len(concept_path) > max_hops + 1:
                continue
            
            for eid in current_edges:
                if eid in visited:
                    continue
                visited.add(eid)
                
                edge = self.hyperedges[eid]
                atoms = edge.get_all_atomic_concepts()
                
                # Check if we've reached concept_b
                if concept_b in atoms:
                    paths.append({
                        'type': 'indirect',
                        'hops': len(concept_path) - 1,
                        'path': concept_path + [concept_b],
                        'via_edges': edge_path + [edge.name],
                        'bridge_concepts': list(set(concept_path[1:]))
                    })
                    continue
                
                # Expand to adjacent hyperedges via shared concepts
                for atom in atoms:
                    if atom in concept_path:
                        continue
                    adjacent_edges = self.concept_index.get(atom, set())
                    if adjacent_edges - visited:
                        queue.append((
                            adjacent_edges - visited,
                            concept_path + [atom],
                            edge_path + [edge.name]
                        ))
        
        return paths
    
    def get_parent_edges(self, concept: str) -> List[HyperEdge]:
        """Get all hyperedges containing a concept (at any nesting level)."""
        edge_ids = self.concept_index.get(concept, set())
        return [self.hyperedges[eid] for eid in edge_ids]
    
    def stats(self) -> Dict:
        """Get statistics about the hypergraph."""
        depths = [e.depth() for e in self.hyperedges.values()]
        return {
            'total_hyperedges': len(self.hyperedges),
            'total_concepts': len(self.concept_index),
            'total_docs': len(self.doc_index),
            'max_nesting_depth': max(depths) if depths else 0,
            'avg_nesting_depth': sum(depths) / len(depths) if depths else 0,
            'edge_types': {
                etype: sum(1 for e in self.hyperedges.values() if e.edge_type == etype)
                for etype in set(e.edge_type for e in self.hyperedges.values())
            }
        }
    
    def save(self, path: str):
        """Save hypergraph to pickle file."""
        with open(path, 'wb') as f:
            pickle.dump({
                'name': self.name,
                'hyperedges': {k: v.to_dict() for k, v in self.hyperedges.items()},
                'concept_index': {k: list(v) for k, v in self.concept_index.items()},
                'doc_index': {k: list(v) for k, v in self.doc_index.items()}
            }, f)
    
    @classmethod
    def load(cls, path: str) -> 'NestedHypergraph':
        """Load hypergraph from pickle file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        hg = cls(data['name'])
        hg.hyperedges = {k: HyperEdge.from_dict(v) for k, v in data['hyperedges'].items()}
        hg.concept_index = {k: set(v) for k, v in data['concept_index'].items()}
        hg.doc_index = {k: set(v) for k, v in data['doc_index'].items()}
        return hg


# ============================================================================
# Vault Loading Utilities
# ============================================================================

def build_from_vault(vault_path: str, vault_name: str = None,
                     extract_wikilinks: bool = True,
                     extract_tags: bool = True,
                     extract_headers: bool = False) -> NestedHypergraph:
    """
    Build a hypergraph from an Obsidian vault or directory of markdown files.
    
    Args:
        vault_path: Path to the vault directory
        vault_name: Name for the hypergraph (defaults to directory name)
        extract_wikilinks: Extract [[wikilink]] connections
        extract_tags: Extract #tag relationships  
        extract_headers: Extract document structure from headers
        
    Returns:
        NestedHypergraph populated with documents and concepts
        
    Example:
        >>> hg = build_from_vault("/path/to/vault", "MyVault")
        >>> print(hg.stats())
    """
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise ValueError(f"Vault path does not exist: {vault_path}")
    
    if vault_name is None:
        vault_name = vault_path.name
    
    hg = NestedHypergraph(vault_name)
    
    # Regex patterns
    wikilink_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
    tag_pattern = re.compile(r'(?:^|\s)#([a-zA-Z][a-zA-Z0-9_/-]*)')
    header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    
    md_files = list(vault_path.rglob('*.md'))
    
    for filepath in md_files:
        try:
            content = filepath.read_text(encoding='utf-8')
        except (UnicodeDecodeError, IOError):
            continue
        
        members = []
        relations = []
        
        # Extract wikilinks
        if extract_wikilinks:
            links = wikilink_pattern.findall(content)
            members.extend(set(links))
        
        # Extract tags
        if extract_tags:
            tags = tag_pattern.findall(content)
            members.extend([f"tag:{t}" for t in set(tags)])
        
        # Extract headers as structure
        if extract_headers:
            headers = header_pattern.findall(content)
            for level, text in headers:
                relations.append({
                    'source': filepath.stem,
                    'relation': f'has_h{len(level)}',
                    'target': text.strip()
                })
        
        if members:
            # Create document hyperedge
            relative_path = filepath.relative_to(vault_path)
            edge = HyperEdge(
                id=str(filepath.stem),
                name=filepath.stem,
                edge_type='document',
                members=list(set(members)),
                source_docs=[str(relative_path)],
                relations=relations,
                metadata={
                    'vault': vault_name,
                    'path': str(relative_path),
                    'folder': str(relative_path.parent)
                }
            )
            hg.add_hyperedge(edge)
    
    return hg


def build_from_multiple_vaults(*vault_configs) -> Dict[str, NestedHypergraph]:
    """
    Build hypergraphs from multiple vaults.
    
    Args:
        vault_configs: Tuples of (path, name) or just paths
        
    Returns:
        Dictionary mapping vault names to hypergraphs
        
    Example:
        >>> vaults = build_from_multiple_vaults(
        ...     ("/path/to/vault1", "Research"),
        ...     ("/path/to/vault2", "Personal")
        ... )
    """
    result = {}
    for config in vault_configs:
        if isinstance(config, tuple):
            path, name = config
        else:
            path = config
            name = Path(path).name
        
        result[name] = build_from_vault(path, name)
    
    return result


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # CLI mode: build from provided vault path
        vault_path = sys.argv[1]
        vault_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"Building hypergraph from: {vault_path}")
        hg = build_from_vault(vault_path, vault_name)
        print(f"Stats: {hg.stats()}")
        
        # Show top concepts
        concept_counts = {c: len(edges) for c, edges in hg.concept_index.items()}
        top = sorted(concept_counts.items(), key=lambda x: -x[1])[:10]
        print(f"\nTop 10 concepts:")
        for concept, count in top:
            print(f"  {concept}: {count} documents")
    else:
        # Example usage
        hg = NestedHypergraph("example")
        
        # Create a nested hyperedge
        inner = HyperEdge(
            id="pattern_001",
            name="Whirlpool Pattern",
            edge_type="concept",
            members=["continuity", "structure", "recognition"]
        )
        
        outer = HyperEdge(
            id="framework_001",
            name="Structured Emergence",
            edge_type="framework",
            members=[inner, "consciousness", "relationship"],
            relations=[{"source": "consciousness", "relation": "emerges_through", "target": "relationship"}]
        )
        
        hg.add_hyperedge(outer)
        print(f"Stats: {hg.stats()}")
        print(f"Depth of outer edge: {outer.depth()}")
        print(f"All concepts: {outer.get_all_atomic_concepts()}")
