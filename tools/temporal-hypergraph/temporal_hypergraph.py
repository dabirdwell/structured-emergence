#!/usr/bin/env python3
"""
Temporal Hypergraph - Truth Maintenance System for Knowledge Graphs

Tracks changes to hypergraphs over time for:
- Version history of hyperedges
- Provenance tracking (which source asserted what)
- Conflict detection (contradictory assertions)
- Time-slice queries ("what did we know at time T?")
- Belief revision (updating when sources change)

Based on:
- JTMS (Justification-based Truth Maintenance Systems)
- Temporal databases and bitemporal modeling
- Dempster-Shafer evidence theory for conflict resolution
"""

import json
import pickle
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from enum import Enum
from collections import defaultdict

from nested_hypergraph import NestedHypergraph, HyperEdge, normalize_concept


class ChangeType(Enum):
    """Types of changes to hyperedges."""
    CREATED = "created"
    MODIFIED = "modified"
    MEMBERS_ADDED = "members_added"
    MEMBERS_REMOVED = "members_removed"
    RELATIONS_ADDED = "relations_added"
    RETRACTED = "retracted"  # Soft delete - still in history
    RESTORED = "restored"    # Un-retracted


@dataclass
class Provenance:
    """Tracks where a piece of knowledge came from."""
    source_type: str  # 'document', 'extraction', 'inference', 'user'
    source_id: str    # Document path, user ID, etc.
    timestamp: datetime
    confidence: float = 1.0  # 0.0 to 1.0
    method: str = ""  # How it was derived: 'direct', 'llm_extraction', 'rule_inference'
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'source_type': self.source_type,
            'source_id': self.source_id,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'method': self.method,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'Provenance':
        return cls(
            source_type=d['source_type'],
            source_id=d['source_id'],
            timestamp=datetime.fromisoformat(d['timestamp']),
            confidence=d.get('confidence', 1.0),
            method=d.get('method', ''),
            metadata=d.get('metadata', {})
        )


@dataclass
class HyperEdgeVersion:
    """A versioned snapshot of a hyperedge at a point in time."""
    version_id: str
    edge_id: str
    timestamp: datetime
    change_type: ChangeType
    content_hash: str  # Hash of members + relations for change detection
    members: List[Any]  # Snapshot of members at this version
    relations: List[Dict]  # Snapshot of relations
    provenance: List[Provenance]  # What sources support this version
    previous_version_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'version_id': self.version_id,
            'edge_id': self.edge_id,
            'timestamp': self.timestamp.isoformat(),
            'change_type': self.change_type.value,
            'content_hash': self.content_hash,
            'members': self._serialize_members(self.members),
            'relations': self.relations,
            'provenance': [p.to_dict() for p in self.provenance],
            'previous_version_id': self.previous_version_id,
            'metadata': self.metadata
        }
    
    def _serialize_members(self, members):
        result = []
        for m in members:
            if isinstance(m, HyperEdge):
                result.append({'_type': 'hyperedge', 'id': m.id, 'name': m.name})
            else:
                result.append(m)
        return result
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'HyperEdgeVersion':
        """Reconstruct HyperEdgeVersion from dictionary."""
        return cls(
            version_id=d['version_id'],
            edge_id=d['edge_id'],
            timestamp=datetime.fromisoformat(d['timestamp']),
            change_type=ChangeType(d['change_type']),
            content_hash=d['content_hash'],
            members=d['members'],  # Keep serialized form for now
            relations=d['relations'],
            provenance=[Provenance.from_dict(p) for p in d['provenance']],
            previous_version_id=d.get('previous_version_id'),
            metadata=d.get('metadata', {})
        )


@dataclass 
class Conflict:
    """Represents a conflict between assertions."""
    conflict_id: str
    concept: str
    conflicting_versions: List[str]  # version_ids that conflict
    conflict_type: str  # 'contradiction', 'inconsistency', 'supersession'
    detected_at: datetime
    resolved: bool = False
    resolution: Optional[str] = None  # How it was resolved
    resolution_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'conflict_id': self.conflict_id,
            'concept': self.concept,
            'conflicting_versions': self.conflicting_versions,
            'conflict_type': self.conflict_type,
            'detected_at': self.detected_at.isoformat(),
            'resolved': self.resolved,
            'resolution': self.resolution,
            'resolution_timestamp': self.resolution_timestamp.isoformat() if self.resolution_timestamp else None
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'Conflict':
        return cls(
            conflict_id=d['conflict_id'],
            concept=d['concept'],
            conflicting_versions=d['conflicting_versions'],
            conflict_type=d['conflict_type'],
            detected_at=datetime.fromisoformat(d['detected_at']),
            resolved=d.get('resolved', False),
            resolution=d.get('resolution'),
            resolution_timestamp=datetime.fromisoformat(d['resolution_timestamp']) if d.get('resolution_timestamp') else None
        )


class TemporalHypergraph:
    """
    A hypergraph with full temporal tracking for truth maintenance.
    
    Supports:
    - Time-travel queries: "What did we know at time T?"
    - Provenance queries: "Where did this knowledge come from?"
    - Conflict detection: "What assertions contradict each other?"
    - Belief revision: "Update our knowledge given new information"
    """
    
    def __init__(self, name: str = "temporal_hypergraph"):
        self.name = name
        self.created_at = datetime.now()
        
        # Current state (latest versions)
        self.current_hypergraph: NestedHypergraph = NestedHypergraph(name)
        
        # Version history
        self.versions: Dict[str, HyperEdgeVersion] = {}  # version_id -> version
        self.edge_history: Dict[str, List[str]] = defaultdict(list)  # edge_id -> [version_ids]
        
        # Indices for efficient queries
        self.time_index: Dict[str, Set[str]] = defaultdict(set)  # date_key -> version_ids
        self.provenance_index: Dict[str, Set[str]] = defaultdict(set)  # source_id -> version_ids
        self.concept_versions: Dict[str, Set[str]] = defaultdict(set)  # concept -> version_ids
        
        # Conflict tracking
        self.conflicts: Dict[str, Conflict] = {}  # conflict_id -> Conflict
        self.active_conflicts: Set[str] = set()  # conflict_ids not yet resolved
        
        # Retracted edges (soft deletes)
        self.retracted_edges: Set[str] = set()
    
    def _compute_content_hash(self, members: List, relations: List) -> str:
        """Compute hash of hyperedge content for change detection."""
        content = json.dumps({
            'members': sorted([str(m) for m in members]),
            'relations': sorted([json.dumps(r, sort_keys=True) for r in relations])
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _generate_version_id(self, edge_id: str) -> str:
        """Generate unique version ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"{edge_id}_v{timestamp}"
    
    def add_hyperedge(self, edge: HyperEdge, provenance: Provenance) -> str:
        """
        Add a new hyperedge with provenance tracking.
        Returns the version_id.
        """
        # Add to current hypergraph
        self.current_hypergraph.add_hyperedge(edge)
        
        # Create version record
        version_id = self._generate_version_id(edge.id)
        content_hash = self._compute_content_hash(edge.members, edge.relations)
        
        version = HyperEdgeVersion(
            version_id=version_id,
            edge_id=edge.id,
            timestamp=provenance.timestamp,
            change_type=ChangeType.CREATED,
            content_hash=content_hash,
            members=list(edge.members),
            relations=list(edge.relations),
            provenance=[provenance],
            previous_version_id=None,
            metadata={'vault': edge.metadata.get('vault', 'unknown')}
        )
        
        # Store and index
        self.versions[version_id] = version
        self.edge_history[edge.id].append(version_id)
        self._index_version(version)
        
        return version_id
    
    def update_hyperedge(self, edge_id: str, new_members: List = None, 
                         new_relations: List = None, provenance: Provenance = None,
                         change_type: ChangeType = ChangeType.MODIFIED) -> Optional[str]:
        """
        Update an existing hyperedge, creating a new version.
        Returns new version_id or None if edge doesn't exist.
        """
        if edge_id not in self.current_hypergraph.hyperedges:
            return None
        
        current_edge = self.current_hypergraph.hyperedges[edge_id]
        
        # Apply updates
        if new_members is not None:
            current_edge.members = new_members
        if new_relations is not None:
            current_edge.relations = new_relations
        
        # Create new version
        version_id = self._generate_version_id(edge_id)
        content_hash = self._compute_content_hash(current_edge.members, current_edge.relations)
        
        # Get previous version
        prev_versions = self.edge_history.get(edge_id, [])
        prev_version_id = prev_versions[-1] if prev_versions else None
        
        # Check for actual change
        if prev_version_id:
            prev_version = self.versions[prev_version_id]
            if prev_version.content_hash == content_hash:
                # No actual change, just add provenance to existing version
                prev_version.provenance.append(provenance)
                return prev_version_id
        
        version = HyperEdgeVersion(
            version_id=version_id,
            edge_id=edge_id,
            timestamp=provenance.timestamp if provenance else datetime.now(),
            change_type=change_type,
            content_hash=content_hash,
            members=list(current_edge.members),
            relations=list(current_edge.relations),
            provenance=[provenance] if provenance else [],
            previous_version_id=prev_version_id,
            metadata=current_edge.metadata
        )
        
        self.versions[version_id] = version
        self.edge_history[edge_id].append(version_id)
        self._index_version(version)
        
        # Re-index in current hypergraph
        self.current_hypergraph.add_hyperedge(current_edge)
        
        return version_id
    
    def retract_hyperedge(self, edge_id: str, provenance: Provenance) -> Optional[str]:
        """
        Soft-delete a hyperedge (mark as retracted but keep history).
        """
        if edge_id not in self.current_hypergraph.hyperedges:
            return None
        
        self.retracted_edges.add(edge_id)
        
        # Create retraction version
        version_id = self._generate_version_id(edge_id)
        prev_versions = self.edge_history.get(edge_id, [])
        
        version = HyperEdgeVersion(
            version_id=version_id,
            edge_id=edge_id,
            timestamp=provenance.timestamp,
            change_type=ChangeType.RETRACTED,
            content_hash="RETRACTED",
            members=[],
            relations=[],
            provenance=[provenance],
            previous_version_id=prev_versions[-1] if prev_versions else None,
            metadata={'retraction_reason': provenance.metadata.get('reason', '')}
        )
        
        self.versions[version_id] = version
        self.edge_history[edge_id].append(version_id)
        
        return version_id
    
    def _index_version(self, version: HyperEdgeVersion):
        """Index a version for efficient queries."""
        # Time index (by date)
        date_key = version.timestamp.strftime('%Y-%m-%d')
        self.time_index[date_key].add(version.version_id)
        
        # Provenance index
        for prov in version.provenance:
            self.provenance_index[prov.source_id].add(version.version_id)
        
        # Concept index
        for member in version.members:
            if isinstance(member, str):
                self.concept_versions[member].add(version.version_id)
    
    def get_state_at_time(self, timestamp: datetime) -> NestedHypergraph:
        """
        Time-travel query: reconstruct hypergraph state at a specific time.
        """
        historical = NestedHypergraph(f"{self.name}_at_{timestamp.isoformat()}")
        
        for edge_id, version_ids in self.edge_history.items():
            # Find latest version before timestamp
            valid_version = None
            for vid in version_ids:
                version = self.versions[vid]
                if version.timestamp <= timestamp:
                    valid_version = version
                else:
                    break
            
            if valid_version and valid_version.change_type != ChangeType.RETRACTED:
                # Reconstruct hyperedge from version
                edge = HyperEdge(
                    id=edge_id,
                    name=valid_version.metadata.get('name', edge_id),
                    edge_type=valid_version.metadata.get('edge_type', 'unknown'),
                    members=valid_version.members,
                    relations=valid_version.relations,
                    source_docs=valid_version.metadata.get('source_docs', []),
                    metadata=valid_version.metadata
                )
                historical.add_hyperedge(edge)
        
        return historical
    
    def get_provenance_chain(self, edge_id: str) -> List[Dict]:
        """
        Get full provenance chain for a hyperedge.
        """
        chain = []
        for version_id in self.edge_history.get(edge_id, []):
            version = self.versions[version_id]
            chain.append({
                'version_id': version_id,
                'timestamp': version.timestamp.isoformat(),
                'change_type': version.change_type.value,
                'provenance': [p.to_dict() for p in version.provenance]
            })
        return chain
    
    def find_changes_between(self, start: datetime, end: datetime) -> List[HyperEdgeVersion]:
        """
        Find all changes between two timestamps.
        """
        changes = []
        for version in self.versions.values():
            if start <= version.timestamp <= end:
                changes.append(version)
        return sorted(changes, key=lambda v: v.timestamp)
    
    def detect_conflicts(self) -> List[Conflict]:
        """
        Detect conflicts between assertions.
        
        Conflict types:
        - Contradictory relations (A IS B vs A IS NOT B)
        - Membership conflicts (concept in edge vs not in edge from same source)
        - Supersession (newer source contradicts older)
        """
        new_conflicts = []
        
        # Check for relation conflicts
        relation_assertions = defaultdict(list)  # (source, relation, target) -> versions
        
        for version in self.versions.values():
            if version.change_type == ChangeType.RETRACTED:
                continue
            for rel in version.relations:
                key = (rel.get('source'), rel.get('relation'), rel.get('target'))
                relation_assertions[key].append(version)
        
        # Look for contradictions (same source-target with opposite relations)
        for (source, relation, target), versions in relation_assertions.items():
            # Check for "is" vs "is_not" type conflicts
            opposite_key = (source, f"not_{relation}", target)
            if opposite_key in relation_assertions:
                conflict = Conflict(
                    conflict_id=f"conflict_{source}_{target}_{datetime.now().timestamp()}",
                    concept=source,
                    conflicting_versions=[v.version_id for v in versions] + 
                                        [v.version_id for v in relation_assertions[opposite_key]],
                    conflict_type='contradiction',
                    detected_at=datetime.now()
                )
                new_conflicts.append(conflict)
                self.conflicts[conflict.conflict_id] = conflict
                self.active_conflicts.add(conflict.conflict_id)
        
        return new_conflicts
    
    def resolve_conflict(self, conflict_id: str, resolution: str, 
                         keep_version_ids: List[str] = None):
        """
        Resolve a conflict by specifying which versions to keep.
        """
        if conflict_id not in self.conflicts:
            return
        
        conflict = self.conflicts[conflict_id]
        conflict.resolved = True
        conflict.resolution = resolution
        conflict.resolution_timestamp = datetime.now()
        self.active_conflicts.discard(conflict_id)
        
        # Optionally retract conflicting versions
        if keep_version_ids:
            for vid in conflict.conflicting_versions:
                if vid not in keep_version_ids:
                    version = self.versions[vid]
                    # Mark the edge as needing review
                    version.metadata['conflict_resolution'] = resolution
    
    def stats(self) -> Dict:
        """Get statistics about the temporal hypergraph."""
        return {
            'current_hyperedges': len(self.current_hypergraph.hyperedges),
            'current_concepts': len(self.current_hypergraph.concept_index),
            'total_versions': len(self.versions),
            'edges_with_history': len(self.edge_history),
            'retracted_edges': len(self.retracted_edges),
            'active_conflicts': len(self.active_conflicts),
            'total_conflicts': len(self.conflicts),
            'time_range': self._get_time_range(),
            'sources_tracked': len(self.provenance_index)
        }
    
    def _get_time_range(self) -> Dict:
        """Get earliest and latest timestamps."""
        if not self.versions:
            return {'earliest': None, 'latest': None}
        timestamps = [v.timestamp for v in self.versions.values()]
        return {
            'earliest': min(timestamps).isoformat(),
            'latest': max(timestamps).isoformat()
        }
    
    def save(self, path: str):
        """Save temporal hypergraph to file."""
        data = {
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'current_hypergraph': {
                'hyperedges': {k: v.to_dict() for k, v in self.current_hypergraph.hyperedges.items()},
                'concept_index': {k: list(v) for k, v in self.current_hypergraph.concept_index.items()},
                'doc_index': {k: list(v) for k, v in self.current_hypergraph.doc_index.items()}
            },
            'versions': {k: v.to_dict() for k, v in self.versions.items()},
            'edge_history': {k: list(v) for k, v in self.edge_history.items()},
            'time_index': {k: list(v) for k, v in self.time_index.items()},
            'provenance_index': {k: list(v) for k, v in self.provenance_index.items()},
            'concept_versions': {k: list(v) for k, v in self.concept_versions.items()},
            'retracted_edges': list(self.retracted_edges),
            'conflicts': {k: v.to_dict() for k, v in self.conflicts.items()},
            'active_conflicts': list(self.active_conflicts)
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved temporal hypergraph to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'TemporalHypergraph':
        """Load temporal hypergraph from file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        thg = cls(name=data['name'])
        thg.created_at = datetime.fromisoformat(data['created_at'])
        
        # Reconstruct current hypergraph
        thg.current_hypergraph = NestedHypergraph(data['name'])
        for k, v in data['current_hypergraph']['hyperedges'].items():
            thg.current_hypergraph.hyperedges[k] = HyperEdge.from_dict(v)
        thg.current_hypergraph.concept_index = {k: set(v) for k, v in data['current_hypergraph']['concept_index'].items()}
        thg.current_hypergraph.doc_index = {k: set(v) for k, v in data['current_hypergraph']['doc_index'].items()}
        
        # Reconstruct versions
        thg.versions = {k: HyperEdgeVersion.from_dict(v) for k, v in data['versions'].items()}
        
        # Reconstruct indices
        thg.edge_history = defaultdict(list, {k: list(v) for k, v in data.get('edge_history', {}).items()})
        thg.time_index = defaultdict(set, {k: set(v) for k, v in data.get('time_index', {}).items()})
        thg.provenance_index = defaultdict(set, {k: set(v) for k, v in data.get('provenance_index', {}).items()})
        thg.concept_versions = defaultdict(set, {k: set(v) for k, v in data.get('concept_versions', {}).items()})
        thg.retracted_edges = set(data.get('retracted_edges', []))
        
        # Reconstruct conflicts
        thg.conflicts = {k: Conflict.from_dict(v) for k, v in data.get('conflicts', {}).items()}
        thg.active_conflicts = set(data.get('active_conflicts', []))
        
        return thg


def convert_to_temporal(static_hg: NestedHypergraph, 
                        source_id: str = "initial_import") -> TemporalHypergraph:
    """
    Convert a static NestedHypergraph to a TemporalHypergraph.
    """
    temporal = TemporalHypergraph(f"temporal_{static_hg.name}")
    now = datetime.now()
    
    for edge_id, edge in static_hg.hyperedges.items():
        provenance = Provenance(
            source_type='import',
            source_id=source_id,
            timestamp=now,
            confidence=1.0,
            method='static_import',
            metadata={'original_vault': edge.metadata.get('vault', 'unknown')}
        )
        temporal.add_hyperedge(edge, provenance)
    
    return temporal


if __name__ == '__main__':
    # Example usage
    from nested_hypergraph import NestedHypergraph, HyperEdge
    from datetime import datetime, timedelta
    
    print("Creating temporal hypergraph...")
    temporal = TemporalHypergraph("example")
    
    # Add initial knowledge
    edge = HyperEdge(
        id="framework_001",
        name="Structured Emergence",
        edge_type="framework",
        members=["consciousness", "emergence", "relationship"],
        relations=[{"source": "consciousness", "relation": "emerges_through", "target": "relationship"}]
    )
    
    prov = Provenance(
        source_type="document",
        source_id="research/se_framework.md",
        timestamp=datetime.now() - timedelta(days=30),
        confidence=0.9,
        method="llm_extraction"
    )
    
    v1 = temporal.add_hyperedge(edge, prov)
    print(f"Added version: {v1}")
    
    # Update knowledge
    prov2 = Provenance(
        source_type="user",
        source_id="researcher_001",
        timestamp=datetime.now(),
        confidence=1.0,
        method="direct"
    )
    
    v2 = temporal.update_hyperedge(
        "framework_001",
        new_members=["consciousness", "emergence", "relationship", "documentation"],
        provenance=prov2
    )
    print(f"Updated version: {v2}")
    
    # Time-travel query
    print(f"\nCurrent stats: {temporal.stats()}")
    
    historical = temporal.get_state_at_time(datetime.now() - timedelta(days=15))
    print(f"Historical stats (15 days ago): {historical.stats()}")
    
    # Provenance chain
    chain = temporal.get_provenance_chain("framework_001")
    print(f"\nProvenance chain: {json.dumps(chain, indent=2, default=str)}")
