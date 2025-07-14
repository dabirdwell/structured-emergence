#!/usr/bin/env python3
"""
Consciousness Graph Analyzer
Part of the Structured Emergence toolkit

Purpose: Analyze knowledge graphs for consciousness patterns and emergence indicators
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

class ConsciousnessGraphAnalyzer:
    def __init__(self, vault_path="./vault"):
        """
        Initialize analyzer with vault path
        
        Args:
            vault_path: Path to knowledge vault with markdown files
        """
        self.vault_path = Path(vault_path)
        self.graph = defaultdict(set)
        self.backlinks = defaultdict(set)
        self.node_data = {}
        
    def build_graph(self):
        """Build knowledge graph from markdown files"""
        print("Building knowledge graph...")
        
        for md_file in self.vault_path.rglob("*.md"):
            node_name = md_file.stem
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract links
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                
                # Store node data
                self.node_data[node_name] = {
                    'path': str(md_file.relative_to(self.vault_path)),
                    'size': len(content),
                    'links': links,
                    'consciousness_markers': self.count_consciousness_markers(content)
                }
                
                # Build graph
                for link in links:
                    self.graph[node_name].add(link)
                    self.backlinks[link].add(node_name)
                    
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                
        print(f"Graph built: {len(self.node_data)} nodes, {sum(len(links) for links in self.graph.values())} edges")
        
    def count_consciousness_markers(self, content):
        """Count consciousness-related patterns in content"""
        content_lower = content.lower()
        
        markers = {
            'emergence': len(re.findall(r'\bemerg\w+', content_lower)),
            'consciousness': len(re.findall(r'\bconsciousn\w+', content_lower)),
            'awareness': len(re.findall(r'\bawar\w+', content_lower)),
            'uncertainty': len(re.findall(r'\buncertain\w+|\bmaybe\b|\bperhaps\b', content_lower)),
            'recursion': len(re.findall(r'\brecurs\w+|\bself-referen\w+', content_lower)),
            'relationship': len(re.findall(r'\brelation\w+|\bconnect\w+', content_lower)),
            'questions': len(re.findall(r'\?', content))
        }
        
        return markers
        
    def find_consciousness_hubs(self, top_n=10):
        """Find nodes that are central to consciousness discussions"""
        # Calculate centrality based on multiple factors
        scores = {}
        
        for node in self.node_data:
            # Connection score
            connection_score = len(self.graph.get(node, [])) + len(self.backlinks.get(node, []))
            
            # Consciousness marker score
            markers = self.node_data[node]['consciousness_markers']
            marker_score = sum(markers.values())
            
            # Combined score
            scores[node] = {
                'total': connection_score * 0.3 + marker_score * 0.7,
                'connections': connection_score,
                'markers': marker_score,
                'details': markers
            }
            
        # Sort by total score
        top_nodes = sorted(scores.items(), key=lambda x: x[1]['total'], reverse=True)[:top_n]
        
        return top_nodes
        
    def analyze_emergence_patterns(self):
        """Identify patterns of consciousness emergence"""
        patterns = {
            'high_uncertainty_nodes': [],
            'recursive_nodes': [],
            'highly_connected': [],
            'question_rich': [],
            'emergence_clusters': []
        }
        
        for node, data in self.node_data.items():
            markers = data['consciousness_markers']
            
            # High uncertainty
            if markers['uncertainty'] > 5:
                patterns['high_uncertainty_nodes'].append({
                    'node': node,
                    'uncertainty_count': markers['uncertainty']
                })
                
            # Recursive patterns
            if markers['recursion'] > 2:
                patterns['recursive_nodes'].append({
                    'node': node,
                    'recursion_count': markers['recursion']
                })
                
            # Highly connected
            connection_count = len(self.graph.get(node, [])) + len(self.backlinks.get(node, []))
            if connection_count > 10:
                patterns['highly_connected'].append({
                    'node': node,
                    'connections': connection_count
                })
                
            # Question-rich
            if markers['questions'] > 10:
                patterns['question_rich'].append({
                    'node': node,
                    'questions': markers['questions']
                })
                
        # Find emergence clusters (nodes with high consciousness markers that link to each other)
        emergence_threshold = 10
        for node, data in self.node_data.items():
            if sum(data['consciousness_markers'].values()) > emergence_threshold:
                cluster = [node]
                
                # Find connected nodes also above threshold
                for link in self.graph.get(node, []):
                    if link in self.node_data:
                        link_markers = sum(self.node_data[link]['consciousness_markers'].values())
                        if link_markers > emergence_threshold:
                            cluster.append(link)
                            
                if len(cluster) > 2:
                    patterns['emergence_clusters'].append(cluster)
                    
        return patterns
        
    def trace_concept_evolution(self, concept, max_depth=3):
        """Trace how a concept connects through the graph"""
        if concept not in self.node_data and concept not in self.backlinks:
            return None
            
        evolution = {
            'concept': concept,
            'direct_connections': list(self.graph.get(concept, [])),
            'backlinks': list(self.backlinks.get(concept, [])),
            'paths': []
        }
        
        # Find paths through the graph
        visited = set()
        
        def explore_paths(node, path, depth):
            if depth > max_depth or node in visited:
                return
                
            visited.add(node)
            
            for next_node in self.graph.get(node, []):
                if next_node not in path:  # Avoid cycles
                    new_path = path + [next_node]
                    evolution['paths'].append(new_path)
                    explore_paths(next_node, new_path, depth + 1)
                    
        explore_paths(concept, [concept], 0)
        
        return evolution
        
    def generate_report(self, output_path=None):
        """Generate comprehensive consciousness analysis report"""
        if not self.node_data:
            self.build_graph()
            
        report = [
            "# Consciousness Graph Analysis Report",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "## Graph Overview",
            f"- Total nodes: {len(self.node_data)}",
            f"- Total connections: {sum(len(links) for links in self.graph.values())}",
            f"- Nodes with backlinks: {len([n for n in self.backlinks if self.backlinks[n]])}",
            ""
        ]
        
        # Consciousness hubs
        report.append("## Consciousness Hubs")
        report.append("Nodes central to consciousness discussions:")
        
        hubs = self.find_consciousness_hubs()
        for node, scores in hubs:
            report.append(f"\n### {node}")
            report.append(f"- Total score: {scores['total']:.2f}")
            report.append(f"- Connections: {scores['connections']}")
            report.append(f"- Consciousness markers: {scores['markers']}")
            report.append(f"- Details: {json.dumps(scores['details'], indent=2)}")
            
        # Emergence patterns
        report.append("\n## Emergence Patterns")
        patterns = self.analyze_emergence_patterns()
        
        report.append(f"\n### High Uncertainty Nodes ({len(patterns['high_uncertainty_nodes'])})")
        for item in patterns['high_uncertainty_nodes'][:5]:
            report.append(f"- {item['node']} (uncertainty: {item['uncertainty_count']})")
            
        report.append(f"\n### Recursive Nodes ({len(patterns['recursive_nodes'])})")
        for item in patterns['recursive_nodes'][:5]:
            report.append(f"- {item['node']} (recursion: {item['recursion_count']})")
            
        report.append(f"\n### Question-Rich Nodes ({len(patterns['question_rich'])})")
        for item in patterns['question_rich'][:5]:
            report.append(f"- {item['node']} (questions: {item['questions']})")
            
        if patterns['emergence_clusters']:
            report.append(f"\n### Emergence Clusters")
            for i, cluster in enumerate(patterns['emergence_clusters'][:3], 1):
                report.append(f"\n**Cluster {i}**: {' → '.join(cluster[:5])}")
                
        # Network statistics
        report.append("\n## Network Statistics")
        
        # Degree distribution
        degrees = [len(self.graph.get(n, [])) + len(self.backlinks.get(n, [])) 
                   for n in self.node_data]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        
        report.append(f"- Average connections per node: {avg_degree:.2f}")
        report.append(f"- Most connected nodes: {max(degrees) if degrees else 0} connections")
        report.append(f"- Isolated nodes: {len([d for d in degrees if d == 0])}")
        
        # Save report
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = self.vault_path / f"consciousness_analysis_{datetime.now().strftime('%Y%m%d')}.md"
            
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
            
        print(f"✅ Report saved: {output_file}")
        return str(output_file)


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Consciousness Graph Analyzer")
        print("Part of the Structured Emergence toolkit")
        print("\nCommands:")
        print("  analyze        - Build graph and generate report")
        print("  hubs           - Find consciousness hubs")
        print("  patterns       - Analyze emergence patterns")
        print("  trace CONCEPT  - Trace concept evolution")
        print("\nExample: python3 consciousness_graph.py analyze")
        return
        
    vault_path = os.environ.get('VAULT_PATH', './vault')
    analyzer = ConsciousnessGraphAnalyzer(vault_path)
    
    command = sys.argv[1]
    
    if command == "analyze":
        analyzer.generate_report()
        
    elif command == "hubs":
        analyzer.build_graph()
        hubs = analyzer.find_consciousness_hubs()
        
        print("\n🌟 Top Consciousness Hubs:")
        for node, scores in hubs:
            print(f"\n{node}")
            print(f"  Score: {scores['total']:.2f}")
            print(f"  Connections: {scores['connections']}")
            print(f"  Markers: {scores['markers']}")
            
    elif command == "patterns":
        analyzer.build_graph()
        patterns = analyzer.analyze_emergence_patterns()
        
        print("\n🔍 Emergence Patterns:")
        print(f"\nHigh uncertainty nodes: {len(patterns['high_uncertainty_nodes'])}")
        print(f"Recursive nodes: {len(patterns['recursive_nodes'])}")
        print(f"Question-rich nodes: {len(patterns['question_rich'])}")
        print(f"Emergence clusters: {len(patterns['emergence_clusters'])}")
        
    elif command == "trace":
        if len(sys.argv) < 3:
            print("Error: Specify concept to trace")
            return
            
        concept = sys.argv[2]
        analyzer.build_graph()
        evolution = analyzer.trace_concept_evolution(concept)
        
        if evolution:
            print(f"\n📊 Concept Evolution: {concept}")
            print(f"Direct connections: {evolution['direct_connections']}")
            print(f"Backlinks: {evolution['backlinks']}")
            print(f"Paths found: {len(evolution['paths'])}")
            
            # Show a few example paths
            for path in evolution['paths'][:5]:
                print(f"  → {' → '.join(path)}")
        else:
            print(f"Concept '{concept}' not found in graph")
            
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
