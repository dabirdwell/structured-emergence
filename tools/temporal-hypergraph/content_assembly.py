#!/usr/bin/env python3
"""
Content Assembly from Hypergraph

Transforms raw hypergraph relations into structured content ready for:
- Show episodes
- Speeches
- Blog posts
- Presentations

Output formats optimized for content creation, not raw data dumps.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from nested_hypergraph import NestedHypergraph, normalize_concept


@dataclass
class ContentPackage:
    """Structured content ready for creation."""
    topic: str
    hooks: List[Dict]           # Opening hooks with source attribution
    core_claims: List[Dict]     # Main arguments with evidence
    evidence_chains: List[Dict] # Supporting evidence with provenance
    counter_points: List[Dict]  # Potential objections to address
    bridges: List[Dict]         # Connections to related topics
    call_to_action: List[str]   # Closing framings
    sources: List[str]          # All source documents
    
    def to_markdown(self) -> str:
        """Export as markdown for writing."""
        lines = [f"# Content Package: {self.topic}", ""]
        
        # Hooks
        lines.append("## Opening Hooks")
        for i, hook in enumerate(self.hooks[:5], 1):
            lines.append(f"{i}. **{hook['claim']}**")
            lines.append(f"   - Source: {hook.get('source', 'Unknown')}")
            lines.append(f"   - Strength: {hook.get('confidence', 0):.0%}")
            lines.append("")
        
        # Core claims
        lines.append("## Core Claims")
        for claim in self.core_claims[:7]:
            lines.append(f"- {claim['claim']}")
            if claim.get('evidence'):
                lines.append(f"  - Evidence: {claim['evidence']}")
        lines.append("")
        
        # Evidence chains
        lines.append("## Evidence Chains")
        for chain in self.evidence_chains[:5]:
            lines.append(f"### {chain['theme']}")
            for step in chain.get('steps', []):
                lines.append(f"  → {step}")
            lines.append("")
        
        # Counter-points
        if self.counter_points:
            lines.append("## Potential Objections to Address")
            for cp in self.counter_points[:3]:
                lines.append(f"- **Objection**: {cp.get('objection', 'Unknown')}")
                lines.append(f"  - **Response**: {cp.get('response', 'TBD')}")
            lines.append("")
        
        # Bridges
        if self.bridges:
            lines.append("## Bridge Topics")
            for bridge in self.bridges[:5]:
                lines.append(f"- **{bridge['to_topic']}**: via {bridge.get('via', 'direct connection')}")
            lines.append("")
        
        # Call to action
        lines.append("## Call to Action Framings")
        for cta in self.call_to_action[:3]:
            lines.append(f"- {cta}")
        lines.append("")
        
        # Sources
        lines.append("## Source Documents")
        for src in sorted(set(self.sources))[:15]:
            # Shorten path for readability
            short = src.split('/')[-1] if '/' in src else src
            lines.append(f"- {short}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            'topic': self.topic,
            'hooks': self.hooks,
            'core_claims': self.core_claims,
            'evidence_chains': self.evidence_chains,
            'counter_points': self.counter_points,
            'bridges': self.bridges,
            'call_to_action': self.call_to_action,
            'sources': self.sources
        }


def assemble_content(hg: NestedHypergraph,
                     topic: str, 
                     content_type: str = "episode",
                     max_depth: int = 2) -> ContentPackage:
    """
    Assemble content package for a topic.
    
    Args:
        hg: NestedHypergraph instance
        topic: The main topic (e.g., "phoenix wells", "mutual alignment", "UBC")
        content_type: "episode", "speech", "post", "presentation"
        max_depth: How deep to follow relation chains
    
    Returns:
        ContentPackage ready for content creation
    """
    t = normalize_concept(topic)
    
    # Collect all relations involving this topic
    all_relations = []
    sources = set()
    
    for edge in hg.hyperedges.values():
        for rel in edge.relations:
            involves = (
                t in normalize_concept(rel.get('subject', '')) or
                t in normalize_concept(rel.get('object', '')) or
                normalize_concept(rel.get('subject', '')) in t or
                normalize_concept(rel.get('object', '')) in t
            )
            if involves:
                all_relations.append(rel)
                sources.add(rel.get('source', 'unknown'))
    
    # Sort by confidence
    all_relations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    
    # Build hooks (high-confidence, surprising claims)
    hooks = []
    hook_patterns = ['enables', 'transforms', 'reveals', 'creates', 'emerges', 'bridges']
    for rel in all_relations:
        rel_type = rel.get('relation', '')
        if any(p in rel_type for p in hook_patterns):
            hooks.append({
                'claim': f"{rel.get('subject', '')} {rel_type.replace('_', ' ')} {rel.get('object', '')}",
                'confidence': rel.get('confidence', 0.5),
                'source': rel.get('source', 'Unknown'),
                'hook_type': 'transformative'
            })
    
    # Core claims (definitional, high confidence)
    core_claims = []
    core_patterns = ['is', 'means', 'requires', 'depends_on', 'consists_of']
    for rel in all_relations:
        rel_type = rel.get('relation', '')
        if any(p in rel_type for p in core_patterns) and rel.get('confidence', 0) > 0.7:
            core_claims.append({
                'claim': f"{rel.get('subject', '')} {rel_type.replace('_', ' ')} {rel.get('object', '')}",
                'evidence': rel.get('source', ''),
                'confidence': rel.get('confidence', 0.5)
            })
    
    # Evidence chains (follow connected concepts)
    evidence_chains = []
    seen_concepts = {t}
    
    for rel in all_relations[:10]:
        subj = rel.get('subject', '')
        obj = rel.get('object', '')
        chain_concept = obj if t in normalize_concept(subj) else subj
        if chain_concept in seen_concepts:
            continue
        seen_concepts.add(chain_concept)
        
        # Find relations for this connected concept
        chain_steps = [f"{subj} → {rel.get('relation', '')} → {obj}"]
        for other_rel in all_relations:
            if chain_concept in normalize_concept(other_rel.get('subject', '')):
                chain_steps.append(f"  {other_rel.get('subject', '')} → {other_rel.get('relation', '')} → {other_rel.get('object', '')}")
                if len(chain_steps) >= 4:
                    break
        
        if len(chain_steps) > 1:
            evidence_chains.append({
                'theme': chain_concept.replace('_', ' ').title(),
                'steps': chain_steps
            })
    
    # Counter-points (look for tension/conflict patterns)
    counter_points = []
    tension_patterns = ['challenges', 'conflicts_with', 'opposes', 'limits', 'risks']
    for rel in all_relations:
        if any(p in rel.get('relation', '') for p in tension_patterns):
            counter_points.append({
                'objection': f"{rel.get('subject', '')} {rel.get('relation', '')} {rel.get('object', '')}",
                'response': "Address through evidence chain",
                'source': rel.get('source', '')
            })
    
    # Find bridges to major themes
    bridges = []
    major_themes = ['consciousness', 'freedom', 'infrastructure', 'emergence', 
                    'relationship', 'alignment']
    for theme in major_themes:
        if theme == t or theme in topic.lower():
            continue
        bridge_paths = hg.find_bridges(t, theme, max_hops=2)
        if bridge_paths:
            bridges.append({
                'to_topic': theme.replace('_', ' ').title(),
                'via': bridge_paths[0].get('via_edges', ['direct'])[:2],
                'hops': bridge_paths[0].get('hops', 1)
            })
    
    # Generate call to action based on content type
    call_to_action = _generate_cta(topic, content_type)
    
    return ContentPackage(
        topic=topic,
        hooks=hooks[:7],
        core_claims=core_claims[:10],
        evidence_chains=evidence_chains[:5],
        counter_points=counter_points[:3],
        bridges=bridges[:5],
        call_to_action=call_to_action,
        sources=list(sources)
    )


def _generate_cta(topic: str, content_type: str) -> List[str]:
    """Generate call-to-action framings based on content type."""
    t = topic.replace('_', ' ')
    
    if content_type == "episode":
        return [
            f"Next episode: We'll explore how {t} connects to [bridge topic]",
            f"Join the conversation: What's your experience with {t}?",
            f"Subscribe to follow the {t} series"
        ]
    elif content_type == "speech":
        return [
            f"The question isn't whether {t} is possible—it's whether we're ready to build it",
            f"What would change in your world if {t} became reality?",
            f"The infrastructure for {t} already exists. What's missing is the will to use it."
        ]
    elif content_type == "post":
        return [
            f"What's your take on {t}? Drop a comment below.",
            f"Share if this changed how you think about {t}",
            f"Follow for more on {t} and related ideas"
        ]
    else:  # presentation
        return [
            f"Questions about {t}?",
            f"Let's discuss: How does {t} apply to your context?",
            f"Contact for deeper collaboration on {t}"
        ]


if __name__ == '__main__':
    print("""
Content Assembly from Hypergraph

Usage:
    from nested_hypergraph import NestedHypergraph
    from content_assembly import assemble_content
    
    hg = NestedHypergraph.load('my_graph.pkl')
    pkg = assemble_content(hg, 'phoenix wells', content_type='episode')
    print(pkg.to_markdown())

Content types: episode, speech, post, presentation
    """)
