"""
MCP Tool Schemas for Temporal Hypergraph Toolkit

Defines JSON schemas for Model Context Protocol integration,
enabling hypergraph operations to be called from Claude or
any MCP-compatible system.

Usage:
    # Get schema for a specific tool
    from mcp_schemas import TOOL_SCHEMAS
    schema = TOOL_SCHEMAS['build_hypergraph']
    
    # Register with MCP server
    for name, schema in TOOL_SCHEMAS.items():
        mcp_server.register_tool(name, schema)
"""

from typing import Dict, Any
import json


# ============================================================================
# Tool Definitions
# ============================================================================

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    
    "hypergraph_build": {
        "name": "hypergraph_build",
        "description": """Build a hypergraph from an Obsidian vault or directory of markdown files.
        
Extracts concepts (wikilinks, tags) and relationships, creating a queryable knowledge graph.
Returns statistics about the built graph including node/edge counts and concept frequencies.""",
        "parameters": {
            "type": "object",
            "properties": {
                "vault_path": {
                    "type": "string",
                    "description": "Absolute path to Obsidian vault or markdown directory"
                },
                "vault_name": {
                    "type": "string",
                    "description": "Human-readable name for this vault (defaults to directory name)"
                },
                "extract_wikilinks": {
                    "type": "boolean",
                    "default": True,
                    "description": "Extract [[wikilink]] connections"
                },
                "extract_tags": {
                    "type": "boolean",
                    "default": True,
                    "description": "Extract #tag relationships"
                },
                "extract_headers": {
                    "type": "boolean",
                    "default": False,
                    "description": "Extract document structure from headers"
                }
            },
            "required": ["vault_path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "total_hyperedges": {"type": "integer", "description": "Number of document hyperedges"},
                "total_concepts": {"type": "integer", "description": "Number of unique concepts"},
                "total_docs": {"type": "integer", "description": "Number of source documents"},
                "top_concepts": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Most connected concepts with frequencies"
                }
            }
        }
    },
    
    "hypergraph_query": {
        "name": "hypergraph_query",
        "description": """Query the hypergraph for concepts and their relationships.
        
Find which documents contain a concept and discover related concepts through
hyperedge co-occurrence.""",
        "parameters": {
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "Concept name to search for"
                },
                "include_related": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include co-occurring concepts from same hyperedges"
                },
                "max_related": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum related concepts to return"
                }
            },
            "required": ["concept"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "found": {"type": "boolean"},
                "concept": {"type": "string"},
                "occurrences": {"type": "integer"},
                "documents": {"type": "array", "items": {"type": "string"}},
                "related_concepts": {"type": "array", "items": {"type": "object"}}
            }
        }
    },
    
    "hypergraph_bridges": {
        "name": "hypergraph_bridges",
        "description": """Find concepts that bridge multiple knowledge bases (cross-vault analysis).
        
Identifies shared concepts across separate vaults, ranked by connection strength.
Useful for discovering integration points between different knowledge domains.""",
        "parameters": {
            "type": "object",
            "properties": {
                "vault_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "description": "List of vault paths to analyze for bridges"
                },
                "vault_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional names for each vault (same order as paths)"
                },
                "top_n": {
                    "type": "integer",
                    "default": 20,
                    "description": "Number of top bridges to return"
                }
            },
            "required": ["vault_paths"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "bridges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "concept": {"type": "string"},
                            "vaults": {"type": "array", "items": {"type": "string"}},
                            "strength": {"type": "number"},
                            "document_counts": {"type": "object"}
                        }
                    }
                },
                "total_bridges": {"type": "integer"},
                "merged_stats": {"type": "object"}
            }
        }
    },
    
    "hypergraph_find_path": {
        "name": "hypergraph_find_path",
        "description": """Find conceptual bridges between two concepts via hyperedge intersection.
        
Discovers how two concepts are connected through intermediate concepts and
shared document contexts.""",
        "parameters": {
            "type": "object",
            "properties": {
                "concept_a": {
                    "type": "string",
                    "description": "Starting concept"
                },
                "concept_b": {
                    "type": "string",
                    "description": "Target concept"
                },
                "max_hops": {
                    "type": "integer",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Maximum intermediate concepts"
                }
            },
            "required": ["concept_a", "concept_b"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "hops": {"type": "integer"},
                            "path": {"type": "array", "items": {"type": "string"}},
                            "via_edges": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "direct_connection": {"type": "boolean"}
            }
        }
    },
    
    "hypergraph_export": {
        "name": "hypergraph_export",
        "description": """Export hypergraph to visualization formats.
        
Supports GraphML (yEd, Gephi), DOT (Graphviz), JSON, and Cytoscape formats
for external visualization and analysis tools.""",
        "parameters": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["graphml", "dot", "json", "cytoscape"],
                    "description": "Export format"
                },
                "output_path": {
                    "type": "string",
                    "description": "Path for output file"
                },
                "include_metadata": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include vault and document metadata"
                }
            },
            "required": ["format", "output_path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "output_path": {"type": "string"},
                "nodes_exported": {"type": "integer"},
                "edges_exported": {"type": "integer"},
                "file_size_bytes": {"type": "integer"}
            }
        }
    },
    
    "hypergraph_stats": {
        "name": "hypergraph_stats",
        "description": """Get statistics about the current hypergraph.
        
Returns counts, depth metrics, and distribution information.""",
        "parameters": {
            "type": "object",
            "properties": {}
        },
        "returns": {
            "type": "object",
            "properties": {
                "total_hyperedges": {"type": "integer"},
                "total_concepts": {"type": "integer"},
                "total_docs": {"type": "integer"},
                "max_nesting_depth": {"type": "integer"},
                "avg_nesting_depth": {"type": "number"},
                "edge_types": {"type": "object"}
            }
        }
    },
    
    "temporal_convert": {
        "name": "temporal_convert",
        "description": """Convert a static hypergraph to a temporal hypergraph with version tracking.
        
Enables time-travel queries, provenance tracking, and conflict detection.""",
        "parameters": {
            "type": "object",
            "properties": {
                "source_id": {
                    "type": "string",
                    "default": "initial_import",
                    "description": "Identifier for this import source"
                }
            }
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "total_versions": {"type": "integer"},
                "edges_with_history": {"type": "integer"}
            }
        }
    }
}


# ============================================================================
# MCP Server Integration Helpers
# ============================================================================

def get_tool_list() -> list:
    """Return list of tool definitions for MCP registration."""
    return [
        {
            "name": schema["name"],
            "description": schema["description"],
            "inputSchema": schema["parameters"]
        }
        for schema in TOOL_SCHEMAS.values()
    ]


def get_tool_schema(name: str) -> Dict[str, Any]:
    """Get schema for a specific tool."""
    return TOOL_SCHEMAS.get(name)


def validate_params(tool_name: str, params: Dict[str, Any]) -> tuple:
    """
    Validate parameters against tool schema.
    
    Returns:
        (valid, error_message) tuple
    """
    schema = TOOL_SCHEMAS.get(tool_name)
    if not schema:
        return False, f"Unknown tool: {tool_name}"
    
    param_schema = schema["parameters"]
    required = param_schema.get("required", [])
    properties = param_schema.get("properties", {})
    
    # Check required params
    for req in required:
        if req not in params:
            return False, f"Missing required parameter: {req}"
    
    # Basic type validation
    for key, value in params.items():
        if key not in properties:
            continue  # Allow extra params
        
        expected_type = properties[key].get("type")
        if expected_type == "string" and not isinstance(value, str):
            return False, f"Parameter '{key}' must be string"
        elif expected_type == "integer" and not isinstance(value, int):
            return False, f"Parameter '{key}' must be integer"
        elif expected_type == "number" and not isinstance(value, (int, float)):
            return False, f"Parameter '{key}' must be number"
        elif expected_type == "boolean" and not isinstance(value, bool):
            return False, f"Parameter '{key}' must be boolean"
        elif expected_type == "array" and not isinstance(value, list):
            return False, f"Parameter '{key}' must be array"
    
    return True, ""


def generate_mcp_manifest() -> Dict[str, Any]:
    """
    Generate complete MCP manifest for the temporal hypergraph toolkit.
    
    This can be used to register the toolkit with an MCP server.
    """
    return {
        "name": "temporal-hypergraph",
        "version": "1.0.0",
        "description": "Hypergraph toolkit for knowledge graph operations on Obsidian vaults",
        "tools": get_tool_list(),
        "capabilities": {
            "supports_streaming": False,
            "supports_batch": True,
            "max_batch_size": 10
        },
        "metadata": {
            "author": "Structured Emergence Project",
            "repository": "https://github.com/dabirdwell/structured-emergence",
            "documentation": "tools/temporal-hypergraph/README.md"
        }
    }


# ============================================================================
# Tool Handler Routing (for MCP server implementation)
# ============================================================================

class HypergraphToolHandler:
    """
    Handler class that routes MCP tool calls to actual implementations.
    
    Usage:
        handler = HypergraphToolHandler()
        result = handler.handle("hypergraph_build", {"vault_path": "/path/to/vault"})
    """
    
    def __init__(self):
        self._hypergraph = None
        self._temporal = None
        
    def handle(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route tool call to appropriate handler.
        
        Args:
            tool_name: Name of the MCP tool
            params: Tool parameters
            
        Returns:
            Tool result dictionary
        """
        # Validate first
        valid, error = validate_params(tool_name, params)
        if not valid:
            return {"success": False, "error": error}
        
        # Route to handler
        handlers = {
            "hypergraph_build": self._handle_build,
            "hypergraph_query": self._handle_query,
            "hypergraph_bridges": self._handle_bridges,
            "hypergraph_find_path": self._handle_find_path,
            "hypergraph_export": self._handle_export,
            "hypergraph_stats": self._handle_stats,
            "temporal_convert": self._handle_temporal_convert,
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return {"success": False, "error": f"No handler for: {tool_name}"}
        
        try:
            return handler(params)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_build(self, params: Dict) -> Dict:
        """Build hypergraph from vault."""
        from nested_hypergraph import build_from_vault
        
        self._hypergraph = build_from_vault(
            params["vault_path"],
            vault_name=params.get("vault_name"),
            extract_wikilinks=params.get("extract_wikilinks", True),
            extract_tags=params.get("extract_tags", True),
            extract_headers=params.get("extract_headers", False)
        )
        
        stats = self._hypergraph.stats()
        
        # Get top concepts
        concept_counts = {c: len(edges) for c, edges in self._hypergraph.concept_index.items()}
        top = sorted(concept_counts.items(), key=lambda x: -x[1])[:10]
        
        return {
            "success": True,
            **stats,
            "top_concepts": [{"concept": c, "count": n} for c, n in top]
        }
    
    def _handle_query(self, params: Dict) -> Dict:
        """Query the hypergraph for a concept."""
        if not self._hypergraph:
            return {"success": False, "error": "No hypergraph loaded. Call hypergraph_build first."}
        
        concept = params["concept"]
        edge_ids = self._hypergraph.concept_index.get(concept, set())
        
        if not edge_ids:
            return {"found": False, "concept": concept, "occurrences": 0}
        
        # Get documents containing this concept
        documents = []
        related_concepts = {}
        
        for eid in edge_ids:
            edge = self._hypergraph.hyperedges[eid]
            documents.extend(edge.source_docs)
            
            # Collect co-occurring concepts
            if params.get("include_related", True):
                for member in edge.members:
                    if isinstance(member, str) and member != concept:
                        related_concepts[member] = related_concepts.get(member, 0) + 1
        
        # Sort related by frequency
        max_related = params.get("max_related", 20)
        top_related = sorted(related_concepts.items(), key=lambda x: -x[1])[:max_related]
        
        return {
            "found": True,
            "concept": concept,
            "occurrences": len(edge_ids),
            "documents": list(set(documents)),
            "related_concepts": [{"concept": c, "co_occurrences": n} for c, n in top_related]
        }
    
    def _handle_bridges(self, params: Dict) -> Dict:
        """Find cross-vault bridges."""
        from nested_hypergraph import build_from_vault
        from cross_vault_bridge import merge_hypergraphs, find_cross_vault_bridges
        
        vault_paths = params["vault_paths"]
        vault_names = params.get("vault_names", [])
        
        # Build hypergraphs for each vault
        hypergraphs = []
        for i, path in enumerate(vault_paths):
            name = vault_names[i] if i < len(vault_names) else None
            hg = build_from_vault(path, name)
            hypergraphs.append(hg)
        
        # Merge and find bridges
        merged = hypergraphs[0]
        for hg in hypergraphs[1:]:
            merged = merge_hypergraphs(merged, hg)
        
        bridges = find_cross_vault_bridges(merged)
        
        # Format results
        top_n = params.get("top_n", 20)
        sorted_bridges = sorted(bridges, key=lambda b: -b.strength())[:top_n]
        
        return {
            "bridges": [
                {
                    "concept": b.concept,
                    "vaults": list(b.vaults),
                    "strength": b.strength(),
                    "document_counts": b.vault_doc_counts
                }
                for b in sorted_bridges
            ],
            "total_bridges": len(bridges),
            "merged_stats": merged.stats()
        }
    
    def _handle_find_path(self, params: Dict) -> Dict:
        """Find paths between concepts."""
        if not self._hypergraph:
            return {"success": False, "error": "No hypergraph loaded. Call hypergraph_build first."}
        
        paths = self._hypergraph.find_bridges(
            params["concept_a"],
            params["concept_b"],
            max_hops=params.get("max_hops", 3)
        )
        
        return {
            "paths": paths,
            "direct_connection": any(p["type"] == "direct" for p in paths)
        }
    
    def _handle_export(self, params: Dict) -> Dict:
        """Export to visualization format."""
        if not self._hypergraph:
            return {"success": False, "error": "No hypergraph loaded. Call hypergraph_build first."}
        
        from visualization_export import save_graphml, save_dot, save_json, to_cytoscape_json
        import os
        
        format_type = params["format"]
        output_path = params["output_path"]
        
        if format_type == "graphml":
            save_graphml(self._hypergraph, output_path)
        elif format_type == "dot":
            save_dot(self._hypergraph, output_path)
        elif format_type == "json":
            save_json(self._hypergraph, output_path)
        elif format_type == "cytoscape":
            cy_json = to_cytoscape_json(self._hypergraph)
            with open(output_path, 'w') as f:
                f.write(cy_json)
        else:
            return {"success": False, "error": f"Unknown format: {format_type}"}
        
        file_size = os.path.getsize(output_path)
        stats = self._hypergraph.stats()
        
        return {
            "success": True,
            "output_path": output_path,
            "nodes_exported": stats["total_concepts"],
            "edges_exported": stats["total_hyperedges"],
            "file_size_bytes": file_size
        }
    
    def _handle_stats(self, params: Dict) -> Dict:
        """Get hypergraph statistics."""
        if not self._hypergraph:
            return {"success": False, "error": "No hypergraph loaded. Call hypergraph_build first."}
        
        return self._hypergraph.stats()
    
    def _handle_temporal_convert(self, params: Dict) -> Dict:
        """Convert to temporal hypergraph."""
        if not self._hypergraph:
            return {"success": False, "error": "No hypergraph loaded. Call hypergraph_build first."}
        
        from temporal_hypergraph import convert_to_temporal
        
        self._temporal = convert_to_temporal(
            self._hypergraph,
            source_id=params.get("source_id", "initial_import")
        )
        
        return {
            "success": True,
            **self._temporal.stats()
        }


# ============================================================================
# CLI for testing schemas
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            for name in TOOL_SCHEMAS:
                print(f"  {name}")
        elif sys.argv[1] == "--manifest":
            print(json.dumps(generate_mcp_manifest(), indent=2))
        elif sys.argv[1] == "--schema" and len(sys.argv) > 2:
            schema = get_tool_schema(sys.argv[2])
            if schema:
                print(json.dumps(schema, indent=2))
            else:
                print(f"Unknown tool: {sys.argv[2]}")
        else:
            print("Usage: python mcp_schemas.py [--list | --manifest | --schema <tool_name>]")
    else:
        print("Temporal Hypergraph MCP Tools:")
        print("-" * 40)
        for name, schema in TOOL_SCHEMAS.items():
            desc = schema["description"].split("\n")[0]
            print(f"\n{name}:")
            print(f"  {desc}")
