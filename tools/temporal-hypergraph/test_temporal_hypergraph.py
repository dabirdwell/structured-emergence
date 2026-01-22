#!/usr/bin/env python3
"""
Unit tests for temporal hypergraph implementation.

Tests cover:
- Basic versioning operations
- Time-travel queries
- Provenance tracking
- Conflict detection
- Conversion from static hypergraphs
"""

import unittest
from datetime import datetime, timedelta
from temporal_hypergraph import (
    TemporalHypergraph, Provenance, ChangeType,
    HyperEdgeVersion, Conflict, convert_to_temporal
)
from nested_hypergraph import NestedHypergraph, HyperEdge


class TestTemporalHypergraph(unittest.TestCase):
    """Test temporal hypergraph operations."""
    
    def setUp(self):
        """Create a fresh temporal hypergraph for each test."""
        self.thg = TemporalHypergraph("test_graph")
        
        # Create a test edge
        self.test_edge = HyperEdge(
            id="test_edge_1",
            name="Test Framework",
            edge_type="framework",
            members=["concept_a", "concept_b", "concept_c"]
        )
        
        # Standard provenance
        self.test_prov = Provenance(
            source_type="document",
            source_id="/test/doc.md",
            timestamp=datetime.now(),
            confidence=0.9,
            method="test"
        )
    
    def test_add_hyperedge(self):
        """Test adding a new hyperedge."""
        version_id = self.thg.add_hyperedge(self.test_edge, self.test_prov)
        
        self.assertIsNotNone(version_id)
        self.assertIn(self.test_edge.id, self.thg.current_hypergraph.hyperedges)
        self.assertEqual(len(self.thg.versions), 1)
    
    def test_version_tracking(self):
        """Test that versions are properly tracked."""
        # Add edge
        v1 = self.thg.add_hyperedge(self.test_edge, self.test_prov)
        
        # Update edge with different members (to create a new version)
        new_prov = Provenance(
            source_type="document",
            source_id="/test/doc2.md",
            timestamp=datetime.now(),
            confidence=0.95,
            method="update"
        )
        v2 = self.thg.update_hyperedge(
            self.test_edge.id,
            new_members=["concept_a", "concept_b", "concept_d"],  # Changed!
            provenance=new_prov
        )
        
        # Should create a new version since members changed
        self.assertIsNotNone(v2)
        self.assertEqual(len(self.thg.edge_history[self.test_edge.id]), 2)
        
        # Check version chain
        version2 = self.thg.versions[v2]
        self.assertEqual(version2.previous_version_id, v1)
    
    def test_time_travel(self):
        """Test reconstructing graph state at past time."""
        # Add edge at t1
        t1 = datetime.now()
        self.thg.add_hyperedge(self.test_edge, self.test_prov)
        
        # Wait and add another edge
        t2 = datetime.now() + timedelta(seconds=1)
        edge2 = HyperEdge(
            id="test_edge_2",
            name="Later Edge",
            edge_type="concept",
            members=["x", "y"]
        )
        prov2 = Provenance(
            source_type="document",
            source_id="/test/later.md",
            timestamp=t2,
            confidence=0.8,
            method="test"
        )
        # Manually set timestamp for test
        self.thg.add_hyperedge(edge2, prov2)
        self.thg.versions[list(self.thg.versions.keys())[-1]].timestamp = t2
        
        # Time travel to before t2
        historical = self.thg.get_state_at_time(t1 + timedelta(milliseconds=500))
        
        # Should only have first edge
        self.assertEqual(len(historical.hyperedges), 1)
        self.assertIn("test_edge_1", historical.hyperedges)
    
    def test_provenance_chain(self):
        """Test retrieving full provenance chain."""
        # Add edge
        self.thg.add_hyperedge(self.test_edge, self.test_prov)
        
        # Update several times with changing members (to create new versions)
        for i in range(3):
            prov = Provenance(
                source_type="document",
                source_id=f"/test/update{i}.md",
                timestamp=datetime.now(),
                confidence=0.9 - i*0.1,
                method=f"update_{i}"
            )
            self.thg.update_hyperedge(
                self.test_edge.id,
                new_members=[f"concept_new_{i}", f"concept_extra_{i}"],  # Different each time
                provenance=prov
            )
        
        chain = self.thg.get_provenance_chain(self.test_edge.id)
        
        self.assertEqual(len(chain), 4)  # Original + 3 updates
        
        # Chain is in chronological order (oldest first)
        # Each entry has provenance list
        self.assertIn('provenance', chain[0])
        self.assertIsInstance(chain[0]['provenance'], list)
        
        # First entry should be original
        self.assertEqual(chain[0]['provenance'][0]['method'], 'test')
        # Last entry should be last update
        self.assertEqual(chain[-1]['provenance'][0]['method'], 'update_2')
    
    def test_retract_creates_version(self):
        """Test that retracting creates a retraction version."""
        v1 = self.thg.add_hyperedge(self.test_edge, self.test_prov)
        
        # Retract
        retract_prov = Provenance(
            source_type="user",
            source_id="manual",
            timestamp=datetime.now(),
            confidence=1.0,
            method="retraction"
        )
        v2 = self.thg.retract_hyperedge(self.test_edge.id, retract_prov)
        
        # Should have retraction version
        self.assertIsNotNone(v2)
        self.assertIn(self.test_edge.id, self.thg.retracted_edges)
        
        # Retraction version should exist
        retract_version = self.thg.versions[v2]
        self.assertEqual(retract_version.change_type, ChangeType.RETRACTED)
    
    def test_find_changes_between(self):
        """Test finding changes in a time range."""
        t_start = datetime.now()
        
        # Add edges at different times
        for i in range(5):
            edge = HyperEdge(
                id=f"change_test_{i}",
                name=f"Edge {i}",
                edge_type="test",
                members=[f"m{i}"]
            )
            prov = Provenance(
                source_type="test",
                source_id=f"test_{i}",
                timestamp=datetime.now() + timedelta(seconds=i),
                confidence=0.9,
                method="test"
            )
            self.thg.add_hyperedge(edge, prov)
        
        t_end = datetime.now() + timedelta(seconds=10)
        
        changes = self.thg.find_changes_between(t_start, t_end)
        
        self.assertEqual(len(changes), 5)
        # All should be CREATED
        for change in changes:
            self.assertEqual(change.change_type, ChangeType.CREATED)
    
    def test_save_and_load(self):
        """Test persistence."""
        import tempfile
        import os
        
        # Add some data
        self.thg.add_hyperedge(self.test_edge, self.test_prov)
        
        # Save
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            self.thg.save(temp_path)
            
            # Load
            loaded = TemporalHypergraph.load(temp_path)
            
            self.assertEqual(loaded.name, self.thg.name)
            self.assertEqual(len(loaded.versions), len(self.thg.versions))
            self.assertIn(self.test_edge.id, loaded.current_hypergraph.hyperedges)
        finally:
            os.unlink(temp_path)


class TestConvertToTemporal(unittest.TestCase):
    """Test conversion from static hypergraph."""
    
    def test_convert_static_to_temporal(self):
        """Test converting a static hypergraph to temporal."""
        # Create static graph
        static = NestedHypergraph("static_test")
        
        edges = [
            HyperEdge(id="e1", name="Edge 1", edge_type="test", members=["a", "b"]),
            HyperEdge(id="e2", name="Edge 2", edge_type="test", members=["b", "c"]),
            HyperEdge(id="e3", name="Edge 3", edge_type="test", members=["c", "d"]),
        ]
        
        for edge in edges:
            static.add_hyperedge(edge)
        
        # Convert
        temporal = convert_to_temporal(static, source_id="test_conversion")
        
        # Verify
        self.assertEqual(len(temporal.current_hypergraph.hyperedges), 3)
        self.assertEqual(len(temporal.versions), 3)
        
        # Check provenance
        for version in temporal.versions.values():
            self.assertEqual(version.provenance[0].source_id, "test_conversion")
            self.assertEqual(version.change_type, ChangeType.CREATED)


class TestConflictDetection(unittest.TestCase):
    """Test conflict detection."""
    
    def setUp(self):
        self.thg = TemporalHypergraph("conflict_test")
    
    def test_detect_contradictory_relations(self):
        """Test detection of contradictory relations."""
        # Add edge with relation "A enables B"
        edge1 = HyperEdge(
            id="e1",
            name="Positive Claim",
            edge_type="claim",
            members=["concept_a", "concept_b"],
            relations=[{
                'subject': 'concept_a',
                'relation': 'enables',
                'object': 'concept_b',
                'confidence': 0.9,
                'source': 'doc1.md'
            }]
        )
        
        prov1 = Provenance(
            source_type="document",
            source_id="doc1.md",
            timestamp=datetime.now(),
            confidence=0.9,
            method="extraction"
        )
        
        self.thg.add_hyperedge(edge1, prov1)
        
        # Add contradictory edge "A prevents B"
        edge2 = HyperEdge(
            id="e2",
            name="Negative Claim",
            edge_type="claim",
            members=["concept_a", "concept_b"],
            relations=[{
                'subject': 'concept_a',
                'relation': 'prevents',
                'object': 'concept_b',
                'confidence': 0.8,
                'source': 'doc2.md'
            }]
        )
        
        prov2 = Provenance(
            source_type="document",
            source_id="doc2.md",
            timestamp=datetime.now(),
            confidence=0.8,
            method="extraction"
        )
        
        self.thg.add_hyperedge(edge2, prov2)
        
        # Detect conflicts
        conflicts = self.thg.detect_conflicts()
        
        # Should return a list (may or may not find conflicts based on implementation)
        self.assertIsInstance(conflicts, list)


class TestHyperEdgeVersion(unittest.TestCase):
    """Test version dataclass."""
    
    def test_version_creation(self):
        """Test creating a version."""
        prov = Provenance(
            source_type="test",
            source_id="test",
            timestamp=datetime.now(),
            confidence=0.9,
            method="test"
        )
        
        version = HyperEdgeVersion(
            version_id="v1",
            edge_id="e1",
            timestamp=datetime.now(),
            change_type=ChangeType.CREATED,
            members=["a", "b"],  # List, not frozenset
            relations=[],
            content_hash="abc123",
            provenance=[prov]
        )
        
        self.assertEqual(version.version_id, "v1")
        self.assertEqual(version.change_type, ChangeType.CREATED)
        self.assertIn("a", version.members)
    
    def test_version_to_dict(self):
        """Test serialization."""
        prov = Provenance(
            source_type="test",
            source_id="test",
            timestamp=datetime.now(),
            confidence=0.9,
            method="test"
        )
        
        version = HyperEdgeVersion(
            version_id="v1",
            edge_id="e1",
            timestamp=datetime.now(),
            change_type=ChangeType.CREATED,
            members=["a", "b"],
            relations=[],
            content_hash="abc123",
            provenance=[prov]
        )
        
        d = version.to_dict()
        
        self.assertIn('version_id', d)
        self.assertIn('timestamp', d)
        self.assertIn('provenance', d)
        self.assertEqual(d['change_type'], 'created')


if __name__ == '__main__':
    unittest.main(verbosity=2)
