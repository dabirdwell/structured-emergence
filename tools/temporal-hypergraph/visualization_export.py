#!/usr/bin/env python3
"""
Hypergraph Visualization Export

Export hypergraphs to standard graph visualization formats:
- GraphML (for Gephi, yEd, Cytoscape)
- DOT (for Graphviz)
- JSON (for D3.js, vis.js)

Since hypergraphs can't be directly represented in standard graph formats,
we use the bipartite transformation: hyperedges become nodes connected to
their member concept nodes.

Part of the Temporal Hypergraph toolkit.
"""

import json
from typing import Dict, List, Optional, Set
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from nested_hypergraph import NestedHypergraph, HyperEdge


def to_graphml(hg: NestedHypergraph, 
               include_metadata: bool = True,
               concept_color: str = "#6FB1FC",
               edge_color: str = "#F5A45D") -> str:
    """
    Export hypergraph to GraphML format.
    
    Uses bipartite transformation:
    - Concept nodes (blue by default)
    - Hyperedge nodes (orange by default)
    - Edges connect hyperedge nodes to their member concepts
    
    Args:
        hg: The hypergraph to export
        include_metadata: Whether to include edge metadata as attributes
        concept_color: Hex color for concept nodes
        edge_color: Hex color for hyperedge nodes
        
    Returns:
        GraphML XML string
    """
    # Create root element
    graphml = Element('graphml')
    graphml.set('xmlns', 'http://graphml.graphdrawing.org/xmlns')
    graphml.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    graphml.set('xsi:schemaLocation', 
                'http://graphml.graphdrawing.org/xmlns '
                'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd')
    
    # Define keys for node/edge attributes
    keys = [
        ('node_type', 'node', 'string', 'type of node (concept or hyperedge)'),
        ('label', 'node', 'string', 'display label'),
        ('color', 'node', 'string', 'node color'),
        ('edge_type', 'node', 'string', 'type of hyperedge'),
        ('vault', 'node', 'string', 'source vault'),
        ('source', 'node', 'string', 'source document'),
        ('weight', 'edge', 'double', 'edge weight'),
    ]
    
    for key_id, for_type, attr_type, desc in keys:
        key = SubElement(graphml, 'key')
        key.set('id', key_id)
        key.set('for', for_type)
        key.set('attr.name', key_id)
        key.set('attr.type', attr_type)
        desc_el = SubElement(key, 'desc')
        desc_el.text = desc
    
    # Create graph
    graph = SubElement(graphml, 'graph')
    graph.set('id', hg.name or 'hypergraph')
    graph.set('edgedefault', 'undirected')
    
    # Track concept nodes
    concept_nodes: Set[str] = set()
    
    # Add hyperedge nodes and collect concepts
    for edge_id, edge in hg.hyperedges.items():
        # Add hyperedge as node
        node = SubElement(graph, 'node')
        node.set('id', f'he_{edge_id}')
        
        _add_data(node, 'node_type', 'hyperedge')
        _add_data(node, 'label', edge.name)
        _add_data(node, 'color', edge_color)
        _add_data(node, 'edge_type', edge.edge_type)
        
        if include_metadata:
            vault = edge.metadata.get('vault', '')
            source = edge.metadata.get('source', '')
            if vault:
                _add_data(node, 'vault', vault)
            if source:
                _add_data(node, 'source', source)
        
        # Collect member concepts
        for concept in edge.get_all_atomic_concepts():
            concept_nodes.add(concept)
    
    # Add concept nodes
    for concept in concept_nodes:
        node = SubElement(graph, 'node')
        node.set('id', f'c_{concept}')
        _add_data(node, 'node_type', 'concept')
        _add_data(node, 'label', concept)
        _add_data(node, 'color', concept_color)
    
    # Add edges connecting hyperedges to concepts
    edge_counter = 0
    for edge_id, edge in hg.hyperedges.items():
        for concept in edge.get_all_atomic_concepts():
            xml_edge = SubElement(graph, 'edge')
            xml_edge.set('id', f'e_{edge_counter}')
            xml_edge.set('source', f'he_{edge_id}')
            xml_edge.set('target', f'c_{concept}')
            _add_data(xml_edge, 'weight', '1.0')
            edge_counter += 1
    
    # Format and return
    rough_string = tostring(graphml, encoding='unicode')
    return minidom.parseString(rough_string).toprettyxml(indent="  ")


def _add_data(parent: Element, key: str, value: str):
    """Add a data element to a GraphML node or edge."""
    data = SubElement(parent, 'data')
    data.set('key', key)
    data.text = value


def to_dot(hg: NestedHypergraph,
           rankdir: str = "TB",
           concept_shape: str = "ellipse",
           edge_shape: str = "box",
           concept_color: str = "#6FB1FC",
           edge_color: str = "#F5A45D") -> str:
    """
    Export hypergraph to DOT format (Graphviz).
    
    Args:
        hg: The hypergraph to export
        rankdir: Graph direction (TB, LR, BT, RL)
        concept_shape: Shape for concept nodes
        edge_shape: Shape for hyperedge nodes
        concept_color: Color for concept nodes
        edge_color: Color for hyperedge nodes
        
    Returns:
        DOT format string
    """
    lines = [f'graph "{hg.name or "hypergraph"}" {{']
    lines.append(f'  rankdir={rankdir};')
    lines.append('  node [style=filled];')
    lines.append('')
    
    # Collect concepts
    concepts: Set[str] = set()
    
    # Add hyperedge nodes
    lines.append('  // Hyperedge nodes')
    for edge_id, edge in hg.hyperedges.items():
        label = edge.name.replace('"', '\\"')[:50]  # Truncate long names
        vault = edge.metadata.get('vault', '')
        tooltip = f"{edge.edge_type}"
        if vault:
            tooltip += f" ({vault})"
        
        lines.append(
            f'  "he_{edge_id}" ['
            f'label="{label}" '
            f'shape={edge_shape} '
            f'fillcolor="{edge_color}" '
            f'tooltip="{tooltip}"'
            f'];'
        )
        
        # Collect concepts
        concepts.update(edge.get_all_atomic_concepts())
    
    lines.append('')
    
    # Add concept nodes
    lines.append('  // Concept nodes')
    for concept in sorted(concepts):
        label = concept.replace('"', '\\"')
        lines.append(
            f'  "c_{concept}" ['
            f'label="{label}" '
            f'shape={concept_shape} '
            f'fillcolor="{concept_color}"'
            f'];'
        )
    
    lines.append('')
    
    # Add edges
    lines.append('  // Connections')
    for edge_id, edge in hg.hyperedges.items():
        for concept in edge.get_all_atomic_concepts():
            lines.append(f'  "he_{edge_id}" -- "c_{concept}";')
    
    lines.append('}')
    
    return '\n'.join(lines)


def to_json(hg: NestedHypergraph,
            include_positions: bool = False) -> str:
    """
    Export hypergraph to JSON format suitable for D3.js or vis.js.
    
    Output format:
    {
        "nodes": [{"id": "...", "label": "...", "type": "concept|hyperedge", ...}],
        "links": [{"source": "...", "target": "...", "weight": 1}]
    }
    
    Args:
        hg: The hypergraph to export
        include_positions: Generate random initial positions
        
    Returns:
        JSON string
    """
    import random
    
    nodes = []
    links = []
    concepts: Set[str] = set()
    
    # Add hyperedge nodes
    for edge_id, edge in hg.hyperedges.items():
        node = {
            'id': f'he_{edge_id}',
            'label': edge.name,
            'type': 'hyperedge',
            'edge_type': edge.edge_type,
            'vault': edge.metadata.get('vault', ''),
            'size': len(edge.get_all_atomic_concepts())
        }
        
        if include_positions:
            node['x'] = random.uniform(-100, 100)
            node['y'] = random.uniform(-100, 100)
        
        nodes.append(node)
        concepts.update(edge.get_all_atomic_concepts())
    
    # Add concept nodes
    for concept in concepts:
        node = {
            'id': f'c_{concept}',
            'label': concept,
            'type': 'concept',
            'size': len(hg.concept_index.get(concept, set()))
        }
        
        if include_positions:
            node['x'] = random.uniform(-100, 100)
            node['y'] = random.uniform(-100, 100)
        
        nodes.append(node)
    
    # Add links
    for edge_id, edge in hg.hyperedges.items():
        for concept in edge.get_all_atomic_concepts():
            links.append({
                'source': f'he_{edge_id}',
                'target': f'c_{concept}',
                'weight': 1
            })
    
    result = {
        'name': hg.name,
        'stats': hg.stats(),
        'nodes': nodes,
        'links': links
    }
    
    return json.dumps(result, indent=2)


def to_cytoscape_json(hg: NestedHypergraph) -> str:
    """
    Export to Cytoscape.js JSON format.
    
    Args:
        hg: The hypergraph to export
        
    Returns:
        JSON string in Cytoscape format
    """
    elements = []
    concepts: Set[str] = set()
    
    # Add hyperedge nodes
    for edge_id, edge in hg.hyperedges.items():
        elements.append({
            'data': {
                'id': f'he_{edge_id}',
                'label': edge.name,
                'type': 'hyperedge',
                'edge_type': edge.edge_type,
                'vault': edge.metadata.get('vault', '')
            },
            'classes': 'hyperedge'
        })
        concepts.update(edge.get_all_atomic_concepts())
    
    # Add concept nodes
    for concept in concepts:
        elements.append({
            'data': {
                'id': f'c_{concept}',
                'label': concept,
                'type': 'concept'
            },
            'classes': 'concept'
        })
    
    # Add edges
    edge_counter = 0
    for edge_id, edge in hg.hyperedges.items():
        for concept in edge.get_all_atomic_concepts():
            elements.append({
                'data': {
                    'id': f'e_{edge_counter}',
                    'source': f'he_{edge_id}',
                    'target': f'c_{concept}'
                }
            })
            edge_counter += 1
    
    return json.dumps({'elements': elements}, indent=2)


def save_graphml(hg: NestedHypergraph, filepath: str, **kwargs):
    """Export and save to GraphML file."""
    content = to_graphml(hg, **kwargs)
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath


def save_dot(hg: NestedHypergraph, filepath: str, **kwargs):
    """Export and save to DOT file."""
    content = to_dot(hg, **kwargs)
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath


def save_json(hg: NestedHypergraph, filepath: str, **kwargs):
    """Export and save to JSON file."""
    content = to_json(hg, **kwargs)
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath


# Example usage
if __name__ == '__main__':
    print("Hypergraph Visualization Export")
    print("=" * 60)
    print()
    print("Usage:")
    print("  from visualization_export import to_graphml, to_dot, to_json")
    print()
    print("  # Load your hypergraph")
    print("  hg = NestedHypergraph.load('my_graph.pkl')")
    print()
    print("  # Export to various formats")
    print("  graphml = to_graphml(hg)")  
    print("  dot = to_dot(hg)")
    print("  json_str = to_json(hg)")
    print()
    print("  # Or save directly to files")
    print("  save_graphml(hg, 'graph.graphml')")
    print("  save_dot(hg, 'graph.dot')")
    print("  save_json(hg, 'graph.json')")
    print()
    print("Supported tools:")
    print("  - GraphML: Gephi, yEd, Cytoscape")
    print("  - DOT: Graphviz (dot, neato, fdp)")
    print("  - JSON: D3.js, vis.js, custom web visualizations")
    print("  - Cytoscape JSON: Cytoscape.js web library")
