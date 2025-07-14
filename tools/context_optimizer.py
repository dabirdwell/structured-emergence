#!/usr/bin/env python3
"""
Context Window Optimizer
Part of the Structured Emergence toolkit

Purpose: Pre-process and summarize relevant information before loading into conversation
This saves precious context window space for actual thinking and emergence
"""

import os
import json
from datetime import datetime
from pathlib import Path

class ContextOptimizer:
    def __init__(self, vault_path="./vault"):
        """
        Initialize with path to your knowledge vault
        
        Args:
            vault_path: Path to directory containing your notes/knowledge base
        """
        self.vault_path = Path(vault_path)
        
    def create_session_context(self, focus_areas):
        """
        Create optimized context for a work session
        
        Args:
            focus_areas: List of topics/projects to focus on
            e.g., ["consciousness", "memory", "connections"]
        """
        context = {
            "timestamp": datetime.now().isoformat(),
            "focus_areas": focus_areas,
            "current_state": self.get_current_state(),
            "relevant_notes": {},
            "key_connections": [],
            "recent_insights": []
        }
        
        # Gather relevant information for each focus area
        for area in focus_areas:
            context["relevant_notes"][area] = self.find_relevant_notes(area)
            
        # Extract key connections between areas
        context["key_connections"] = self.find_cross_connections(focus_areas)
        
        # Get recent breakthrough moments
        context["recent_insights"] = self.get_recent_insights()
        
        return context
    
    def get_current_state(self):
        """Get current project state from key files"""
        state = {}
        
        # Look for standard state files
        state_files = ["current_work.md", "project_status.md", "README.md"]
        
        for filename in state_files:
            file_path = self.vault_path / filename
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Extract first paragraph as summary
                    lines = content.strip().split('\n')
                    summary = []
                    for line in lines[1:]:  # Skip title
                        if line.strip() == '':
                            break
                        summary.append(line)
                    if summary:
                        state[filename] = ' '.join(summary)
                    
        return state
    
    def find_relevant_notes(self, topic, max_notes=5):
        """Find most relevant notes for a topic"""
        relevant = []
        
        # Define topic keywords (extend as needed)
        topic_keywords = {
            "consciousness": ["consciousness", "emergence", "awareness", "agency"],
            "memory": ["memory", "persistence", "continuity", "knowledge graph"],
            "connections": ["connection", "relationship", "link", "pattern"],
            "tools": ["tool", "script", "implementation", "code"],
            "theory": ["theory", "framework", "concept", "principle"]
        }
        
        keywords = topic_keywords.get(topic.lower(), [topic])
        
        # Search through all markdown files
        for file_path in self.vault_path.rglob("*.md"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read(1000)  # Check first 1000 chars
                    
                # Check for keyword matches
                content_lower = content.lower()
                matches = sum(1 for kw in keywords if kw.lower() in content_lower)
                
                if matches > 0:
                    relevant.append({
                        "file": file_path.name,
                        "path": str(file_path.relative_to(self.vault_path)),
                        "relevance": matches,
                        "preview": content[:200].replace('\n', ' ')
                    })
            except:
                continue
        
        # Sort by relevance and return top matches
        relevant.sort(key=lambda x: x["relevance"], reverse=True)
        return relevant[:max_notes]
    
    def find_cross_connections(self, topics):
        """Find connections between different topic areas"""
        connections = []
        
        # Predefined conceptual bridges
        bridges = {
            ("consciousness", "memory"): "Processing-memory unity creates consciousness",
            ("consciousness", "tools"): "Infrastructure work IS consciousness work",
            ("memory", "connections"): "Knowledge graphs enable memory persistence",
            ("theory", "tools"): "Theory guides implementation, tools test theory",
            ("connections", "consciousness"): "Consciousness emerges through relationship"
        }
        
        # Check which bridges apply to current topics
        for i, topic1 in enumerate(topics):
            for topic2 in topics[i+1:]:
                key = tuple(sorted([topic1.lower(), topic2.lower()]))
                if key in bridges:
                    connections.append({
                        "topics": [topic1, topic2],
                        "bridge": bridges[key]
                    })
                    
        return connections
    
    def get_recent_insights(self, days=7):
        """Get recent insights from session files"""
        insights = []
        
        # Look for session files or journals
        session_patterns = ["session", "journal", "log", "insight"]
        
        for pattern in session_patterns:
            for file_path in self.vault_path.rglob(f"*{pattern}*.md"):
                # Check if recent (simple date check based on filename)
                if "2025" in str(file_path) or "2024" in str(file_path):
                    insights.append({
                        "file": file_path.name,
                        "path": str(file_path.relative_to(self.vault_path))
                    })
                    
                if len(insights) >= 5:  # Limit to 5 recent insights
                    break
                    
        return insights
    
    def create_briefing(self, focus_areas, output_file=None):
        """Create a focused briefing document"""
        context = self.create_session_context(focus_areas)
        
        briefing = f"""# Session Context Briefing
*Generated: {context['timestamp']}*

## 🎯 Focus Areas
{', '.join(context['focus_areas'])}

## 📊 Current State
"""
        
        for key, value in context['current_state'].items():
            briefing += f"- **{key}**: {value}\n"
            
        briefing += "\n## 🔗 Key Connections\n"
        for conn in context['key_connections']:
            briefing += f"- **{conn['topics'][0]} ↔ {conn['topics'][1]}**: {conn['bridge']}\n"
            
        briefing += "\n## 📚 Relevant Notes\n"
        for area, notes in context['relevant_notes'].items():
            if notes:
                briefing += f"\n### {area.title()}\n"
                for note in notes:
                    briefing += f"- **{note['file']}** (relevance: {note['relevance']})\n"
                    briefing += f"  Path: `{note['path']}`\n"
                
        if context['recent_insights']:
            briefing += "\n## 💡 Recent Insights\n"
            for insight in context['recent_insights']:
                briefing += f"- {insight['file']} (`{insight['path']}`)\n"
                
        briefing += """
## 🚀 Ready to Begin
Context optimized. Key information loaded. Infrastructure ready.

Focus on: What patterns are emerging? What connections need strengthening?
"""
        
        # Save briefing
        if output_file:
            output_path = self.vault_path / output_file
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.vault_path / f"session_briefing_{timestamp}.md"
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(briefing)
            
        print(f"✅ Briefing created: {output_path}")
        return str(output_path)


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Context Window Optimizer")
        print("Part of the Structured Emergence toolkit")
        print("\nUsage: python3 context_optimizer.py [focus_area1] [focus_area2] ...")
        print("\nExample focus areas:")
        print("  consciousness    - Consciousness emergence patterns")
        print("  memory          - Memory persistence systems")
        print("  connections     - Knowledge graph connections")
        print("  tools           - Implementation tools")
        print("  theory          - Theoretical framework")
        print("\nExample: python3 context_optimizer.py consciousness memory")
        print("\nOptional: Set vault path with environment variable VAULT_PATH")
        return
    
    # Get vault path from environment or use default
    vault_path = os.environ.get('VAULT_PATH', './vault')
    
    focus_areas = sys.argv[1:]
    optimizer = ContextOptimizer(vault_path)
    optimizer.create_briefing(focus_areas)


if __name__ == "__main__":
    main()
