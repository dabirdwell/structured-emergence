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
        "description": """Build a temporal hypergraph from an Obsidian vault or directory of markdown files.
        
Extracts concepts and relationships, tracking provenance and temporal evolution.
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
                    "description": "Human-readable name for this vault (used in cross-vault analysis)"
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
                    "default": True,
                    "description": "Extract document structure from headers"
                },
                "min_confidence": {
                    "type": "number",
                    "default": 0.5,
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Minimum confidence threshold for extracted relationships"
                }
            },
            "required": ["vault_path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "nodes": {"type": "integer", "description": "Number of concept nodes"},
                "edges": {"type": "integer", "description": "Number of hyperedges"},
                "documents": {"type": "integer", "description": "Number of source documents"},
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
        "description": """Query the hypergraph for concepts, relationships, and evolution patterns.
        
Supports semantic search, temporal queries, and relationship traversal.""",
        "parameters": {
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "Concept name or search term"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["exact", "fuzzy", "semantic"],
                    "default": "fuzzy",
                    "description": "Match type: exact name, fuzzy substring, or semantic similarity"
                },
                "include_related": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include directly connected concepts"
                },
                "depth": {
                    "type": "integer",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Traversal depth for relationship discovery"
                },
                "time_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string", "format": "date-time"},
                        "end": {"type": "string", "format": "date-time"}
                    },
                    "description": "Filter by temporal range (ISO format)"
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
                "sources": {"type": "array", "items": {"type": "string"}},
                "related_concepts": {"type": "array", "items": {"type": "object"}},
                "evolution": {"type": "array", "items": {"type": "object"}}
            }
        }
    },
    
    "hypergraph_bridges": {
        "name": "hypergraph_bridges",
        "description": """Find concepts that bridge multiple knowledge bases (cross-vault analysis).
        
Identifies shared concepts, parallel developments, and potential integration points
across separate vaults or knowledge domains.""",
        "parameters": {
            "type": "object",
            "properties": {
                "vault_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "description": "List of vault paths to analyze for bridges"
                },
                "min_vaults": {
                    "type": "integer",
                    "default": 2,
                    "minimum": 2,
                    "description": "Minimum number of vaults a concept must appear in"
                },
                "similarity_threshold": {
                    "type": "number",
                    "default": 0.8,
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Threshold for fuzzy concept matching across vaults"
                },
                "include_context": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include surrounding context for each bridge"
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
                            "contexts": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "total_bridges": {"type": "integer"},
                "strongest_connection": {"type": "string"}
            }
        }
    },
    
    "hypergraph_evolution": {
        "name": "hypergraph_evolution",
        "description": """Track how a concept evolves over time across documents.
        
Shows temporal progression, context shifts, and relationship changes
to understand how ideas develop in a knowledge base.""",
        "parameters": {
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "Concept to track through time"
                },
                "granularity": {
                    "type": "string",
                    "enum": ["day", "week", "month", "year"],
                    "default": "month",
                    "description": "Time grouping for evolution analysis"
                },
                "include_context_snippets": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include text snippets showing concept usage"
                },
                "track_relationships": {
                    "type": "boolean",
                    "default": True,
                    "description": "Track how related concepts change over time"
                }
            },
            "required": ["concept"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "concept": {"type": "string"},
                "first_seen": {"type": "string", "format": "date-time"},
                "last_seen": {"type": "string", "format": "date-time"},
                "timeline": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "string"},
                            "occurrences": {"type": "integer"},
                            "new_relationships": {"type": "array"},
                            "context_shift": {"type": "number"}
                        }
                    }
                },
                "trend": {"type": "string", "enum": ["growing", "stable", "declining"]}
            }
        }
    },
    
    "hypergraph_export": {
        "name": "hypergraph_export",
        "description": """Export hypergraph to various visualization formats.
        
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
                    "description": "Path for output file (optional, returns string if omitted)"
                },
                "filter_concepts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Export only subgraph containing these concepts"
                },
                "max_nodes": {
                    "type": "integer",
                    "default": 500,
                    "description": "Maximum nodes to include (for performance)"
                },
                "include_metadata": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include temporal and provenance metadata"
                },
                "layout_hint": {
                    "type": "string",
                    "enum": ["hierarchical", "force", "circular", "temporal"],
                    "default": "force",
                    "description": "Suggested layout algorithm for visualization"
                }
            },
            "required": ["format"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "output_path": {"type": "string"},
                "nodes_exported": {"type": "integer"},
                "edges_exported": {"type": "integer"},
                "format": {"type": "string"}
            }
        }
    },
    
    "hypergraph_assemble": {
        "name": "hypergraph_assemble",
        "description": """Assemble structured content from hypergraph relationships.
        
Generates organized documentation, relationship maps, or knowledge summaries
by traversing the hypergraph from a starting concept.""",
        "parameters": {
            "type": "object",
            "properties": {
                "seed_concept": {
                    "type": "string",
                    "description": "Starting concept for content assembly"
                },
                "depth": {
                    "type": "integer",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 5,
                    "description": "How many relationship levels to include"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["markdown", "outline", "narrative", "structured"],
                    "default": "markdown",
                    "description": "Format for assembled content"
                },
                "include_sources": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include source document references"
                },
                "max_sections": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum sections in output"
                },
                "temporal_order": {
                    "type": "boolean",
                    "default": False,
                    "description": "Order content chronologically vs by relevance"
                }
            },
            "required": ["seed_concept"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "sections": {"type": "integer"},
                "concepts_included": {"type": "array", "items": {"type": "string"}},
                "sources_referenced": {"type": "array", "items": {"type": "string"}}
            }
        }
    },
    
    "hypergraph_update": {
        "name": "hypergraph_update",
        "description": """Incrementally update hypergraph with new or modified content.
        
Efficiently processes changes without rebuilding entire graph.
Applies confidence decay to aging information and tracks freshness.""",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to new/modified markdown file"
                },
                "operation": {
                    "type": "string",
                    "enum": ["add", "update", "remove"],
                    "default": "update",
                    "description": "Type of update operation"
                },
                "apply_decay": {
                    "type": "boolean",
                    "default": True,
                    "description": "Apply confidence decay to existing relationships"
                },
                "decay_rate": {
                    "type": "number",
                    "default": 0.1,
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "How much confidence decays per period"
                }
            },
            "required": ["file_path"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "nodes_affected": {"type": "integer"},
                "edges_affected": {"type": "integer"},
                "new_concepts": {"type": "array", "items": {"type": "string"}},
                "updated_relationships": {"type": "integer"}
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


def validate_params(tool_name: str, params: Dict[str, Any]) -> tuple[bool, str]:
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
        "description": "Temporal hypergraph toolkit for knowledge graph operations with provenance tracking",
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
        handler = HypergraphToolHandler(vault_path="/path/to/vault")
        result = handler.handle("hypergraph_query", {"concept": "emergence"})
    """
    
    def __init__(self, default_vault_path: str = None):
        self.default_vault_path = default_vault_path
        self._hypergraph = None
        
    def _ensure_loaded(self, vault_path: str = None):
        """Lazy load hypergraph from vault."""
        path = vault_path or self.default_vault_path
        if self._hypergraph is None and path:
            from temporal_hypergraph import TemporalHypergraph
            self._hypergraph = TemporalHypergraph()
            # Would load from vault here
        return self._hypergraph
    
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
            "hypergraph_evolution": self._handle_evolution,
            "hypergraph_export": self._handle_export,
            "hypergraph_assemble": self._handle_assemble,
            "hypergraph_update": self._handle_update,
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
        from temporal_hypergraph import TemporalHypergraph
        
        vault_path = params["vault_path"]
        self._hypergraph = TemporalHypergraph()
        self._hypergraph.build_from_vault(vault_path)
        
        stats = self._hypergraph.get_statistics()
        return {
            "success": True,
            "nodes": stats.get("nodes", 0),
            "edges": stats.get("hyperedges", 0),
            "documents": stats.get("documents", 0),
            "top_concepts": stats.get("top_concepts", [])[:10]
        }
    
    def _handle_query(self, params: Dict) -> Dict:
        """Query the hypergraph."""
        hg = self._ensure_loaded()
        if not hg:
            return {"success": False, "error": "No hypergraph loaded"}
        
        concept = params["concept"]
        results = hg.query_concept(concept)
        
        return {
            "found": results is not None,
            "concept": concept,
            **results
        }
    
    def _handle_bridges(self, params: Dict) -> Dict:
        """Find cross-vault bridges."""
        from cross_vault_bridge import CrossVaultBridgeFinder
        
        finder = CrossVaultBridgeFinder()
        for path in params["vault_paths"]:
            finder.add_vault(path)
        
        bridges = finder.find_bridges(
            min_vaults=params.get("min_vaults", 2),
            similarity_threshold=params.get("similarity_threshold", 0.8)
        )
        
        return {
            "bridges": bridges[:50],  # Limit response size
            "total_bridges": len(bridges),
            "strongest_connection": bridges[0]["concept"] if bridges else None
        }
    
    def _handle_evolution(self, params: Dict) -> Dict:
        """Track concept evolution."""
        hg = self._ensure_loaded()
        if not hg:
            return {"success": False, "error": "No hypergraph loaded"}
        
        return hg.track_evolution(
            params["concept"],
            granularity=params.get("granularity", "month")
        )
    
    def _handle_export(self, params: Dict) -> Dict:
        """Export to visualization format."""
        from visualization_export import HypergraphExporter
        
        hg = self._ensure_loaded()
        if not hg:
            return {"success": False, "error": "No hypergraph loaded"}
        
        exporter = HypergraphExporter(hg)
        format_map = {
            "graphml": exporter.to_graphml,
            "dot": exporter.to_dot,
            "json": exporter.to_json,
            "cytoscape": exporter.to_cytoscape
        }
        
        export_func = format_map.get(params["format"])
        if not export_func:
            return {"success": False, "error": f"Unknown format: {params['format']}"}
        
        output_path = params.get("output_path")
        result = export_func(output_path)
        
        return {
            "success": True,
            "output_path": output_path,
            "format": params["format"],
            "nodes_exported": result.get("nodes", 0),
            "edges_exported": result.get("edges", 0)
        }
    
    def _handle_assemble(self, params: Dict) -> Dict:
        """Assemble content from hypergraph."""
        from content_assembly import ContentAssembler
        
        hg = self._ensure_loaded()
        if not hg:
            return {"success": False, "error": "No hypergraph loaded"}
        
        assembler = ContentAssembler(hg)
        return assembler.assemble(
            params["seed_concept"],
            depth=params.get("depth", 2),
            output_format=params.get("output_format", "markdown")
        )
    
    def _handle_update(self, params: Dict) -> Dict:
        """Incrementally update hypergraph."""
        from hypergraph_updater import HypergraphUpdater
        
        hg = self._ensure_loaded()
        if not hg:
            return {"success": False, "error": "No hypergraph loaded"}
        
        updater = HypergraphUpdater(hg)
        return updater.process_file(
            params["file_path"],
            operation=params.get("operation", "update")
        )


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
