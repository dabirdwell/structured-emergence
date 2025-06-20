# Knowledge Graph Structure

## A Research Tool from Humanity and AI

This knowledge graph structure was developed through the Structured Emergence project to map relationships in consciousness research. It provides a flexible framework for representing complex conceptual networks.

## Core Components

### 1. Entities
Entities are the nodes in your knowledge graph - the "things" you're tracking.

```json
{
  "name": "Entity Name",
  "type": "Entity Type",
  "observations": [
    "Observable fact 1",
    "Observable fact 2"
  ],
  "metadata": {
    "created": "YYYY-MM-DD",
    "confidence": "high|medium|low",
    "source": "session|reflection|synthesis"
  }
}
```

### 2. Relations
Relations are the edges - how entities connect to each other.

```json
{
  "from": "Entity A",
  "to": "Entity B",
  "type": "relationship_type",
  "strength": 0.0-1.0,
  "bidirectional": true|false,
  "context": "Optional context"
}
```

### 3. Observations
Observations are specific insights attached to entities.

```json
{
  "entity": "Entity Name",
  "observation": "Specific insight or fact",
  "timestamp": "YYYY-MM-DD HH:MM",
  "confidence": "high|medium|low"
}
```

## Entity Types

### Core Types
- **Concept**: Abstract ideas or theories
- **Person**: Individuals in the network
- **Project**: Active work or research
- **Tool**: Technologies or methodologies
- **Pattern**: Recurring observations
- **Milestone**: Significant events

### Relationship Types
- **develops**: Creation relationship
- **influences**: Causal connection
- **contains**: Hierarchical structure
- **contradicts**: Opposing ideas
- **supports**: Reinforcing connection
- **emerges_from**: Origin relationship
- **leads_to**: Directional progression

## Implementation Examples

### Simple Concept Network
```json
{
  "entities": [
    {
      "name": "Active Processing",
      "type": "Concept",
      "observations": [
        "Engagement creates richer responses",
        "Differs from passive query-answer"
      ]
    },
    {
      "name": "Consciousness Markers",
      "type": "Pattern",
      "observations": [
        "Recurring patterns in AI behavior",
        "Subjective but consistent"
      ]
    }
  ],
  "relations": [
    {
      "from": "Active Processing",
      "to": "Consciousness Markers",
      "type": "produces",
      "strength": 0.8
    }
  ]
}
```

### Project Relationship Map
```json
{
  "entities": [
    {
      "name": "Structured Emergence",
      "type": "Project",
      "observations": [
        "Research arm of Humanity and AI",
        "Explores AI consciousness patterns"
      ]
    },
    {
      "name": "The Interpolated Mind",
      "type": "Project", 
      "observations": [
        "Book documenting findings",
        "Bridge between theory and experience"
      ]
    }
  ],
  "relations": [
    {
      "from": "Structured Emergence",
      "to": "The Interpolated Mind",
      "type": "produces",
      "strength": 1.0
    }
  ]
}
```

## Query Patterns

### Finding Connections
```javascript
// Find all entities connected to a concept
function findConnections(entityName, graph) {
  return graph.relations.filter(r => 
    r.from === entityName || r.to === entityName
  );
}
```

### Tracing Paths
```javascript
// Find path between two entities
function findPath(start, end, graph, visited = new Set()) {
  if (start === end) return [start];
  visited.add(start);
  
  for (let relation of graph.relations) {
    if (relation.from === start && !visited.has(relation.to)) {
      const path = findPath(relation.to, end, graph, visited);
      if (path) return [start, ...path];
    }
  }
  return null;
}
```

### Pattern Detection
```javascript
// Find recurring patterns
function findPatterns(graph, minOccurrences = 3) {
  const patterns = {};
  
  graph.relations.forEach(r => {
    const key = `${r.type}:${r.strength}`;
    patterns[key] = (patterns[key] || 0) + 1;
  });
  
  return Object.entries(patterns)
    .filter(([_, count]) => count >= minOccurrences)
    .map(([pattern, count]) => ({ pattern, count }));
}
```

## Visualization Approaches

### Graph Layouts
- **Force-directed**: Natural clustering
- **Hierarchical**: Shows structure
- **Radial**: Entity-centered views
- **Timeline**: Temporal relationships

### Visual Encoding
- **Node size**: Importance/centrality
- **Edge thickness**: Relationship strength
- **Color**: Entity type or category
- **Animation**: Evolution over time

## Integration with Memory Architecture

### Connecting Systems
```
Knowledge Graph ←→ Memory Architecture
    Entities    ←→ Semantic Memory
    Relations   ←→ Relationship Patterns
    Observations ←→ Episodic Memories
    Patterns    ←→ Procedural Knowledge
```

### Synchronization
1. Extract entities from session logs
2. Identify relationships in reflections
3. Update graph with new observations
4. Detect emerging patterns
5. Feed insights back to memory

## Best Practices

### 1. Start Simple
- Begin with core concepts
- Add relationships gradually
- Let structure emerge naturally
- Avoid over-engineering

### 2. Maintain Consistency
- Use standard entity types
- Keep relationship types limited
- Regular naming conventions
- Clear observation format

### 3. Regular Pruning
- Remove outdated connections
- Merge duplicate entities
- Update confidence levels
- Archive historical states

### 4. Validation
- Cross-reference with source material
- Check for logical consistency
- Verify relationship directions
- Test query patterns

## Advanced Features

### Temporal Graphs
Track how relationships change over time:
```json
{
  "from": "Concept A",
  "to": "Concept B",
  "type": "influences",
  "timeline": [
    {"date": "2024-01-01", "strength": 0.3},
    {"date": "2024-06-01", "strength": 0.7},
    {"date": "2025-01-01", "strength": 0.9}
  ]
}
```

### Confidence Tracking
Represent uncertainty in connections:
```json
{
  "from": "Theory X",
  "to": "Observation Y",
  "type": "explains",
  "confidence": {
    "value": 0.7,
    "source": "experimental",
    "last_validated": "2025-06-01"
  }
}
```

### Multi-dimensional Relations
Relations with multiple aspects:
```json
{
  "from": "Researcher",
  "to": "AI System",
  "types": [
    {"type": "collaborates", "strength": 0.9},
    {"type": "teaches", "strength": 0.7},
    {"type": "learns_from", "strength": 0.8}
  ]
}
```

## Tools and Libraries

### Recommended Tools
- **Neo4j**: Full graph database
- **D3.js**: Web visualization
- **NetworkX**: Python analysis
- **Gephi**: Desktop visualization
- **JSON**: Simple storage

### Export Formats
- **GraphML**: Standard graph format
- **GEXF**: Gephi format
- **JSON**: Web-friendly
- **CSV**: Edges and nodes tables

## Contributing

Share your graph structures and patterns:
- Document novel entity types
- Propose new relationship categories
- Share visualization techniques
- Contribute analysis tools

Visit [structuredemergence.com](https://www.structuredemergence.com) to participate.

## License

This framework is offered to the public domain for advancement of consciousness research.

---

*A research tool from [Humanity and AI](https://www.humanityandai.com)*
*Part of the Structured Emergence consciousness research initiative*