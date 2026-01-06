#!/usr/bin/env python3
"""
LM Query Tool
-------------
Basic functions for querying local LLMs via LM Studio.

Part of the Structured Emergence local LLM orchestration toolkit.
"""

import requests
import json
import sys
from typing import Optional, List, Dict, Any

LM_STUDIO_URL = "http://localhost:1234/v1"


def list_models() -> List[str]:
    """List available models in LM Studio."""
    try:
        r = requests.get(f"{LM_STUDIO_URL}/models", timeout=10)
        return [m['id'] for m in r.json()['data']]
    except Exception as e:
        print(f"Error connecting to LM Studio: {e}", file=sys.stderr)
        return []


def query(
    prompt: str,
    model: str = None,
    system: str = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """
    Query a local LLM.
    
    Args:
        prompt: The user prompt
        model: Model ID from LM Studio (uses first available if None)
        system: Optional system prompt
        max_tokens: Max response tokens
        temperature: Sampling temperature (0.2 for coding, 0.6 for general)
        
    Returns:
        Model response text
    """
    if model is None:
        models = list_models()
        if not models:
            return "Error: No models available in LM Studio"
        model = models[0]
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(
            f"{LM_STUDIO_URL}/chat/completions",
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=300,
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error querying model: {e}"


def chunk_text(
    text: str,
    chunk_size: int = 20000,
    overlap: int = 500,
) -> List[str]:
    """
    Chunk text for processing by context-limited models.
    
    Args:
        text: Text to chunk
        chunk_size: Target characters per chunk
        overlap: Overlap between chunks for continuity
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at paragraph boundary
        if end < len(text):
            break_point = text.rfind('\n\n', start + chunk_size // 2, end)
            if break_point > start:
                end = break_point
        
        chunks.append(text[start:end])
        start = end - overlap if end < len(text) else end
    
    return chunks


def chunk_and_query(
    text: str,
    query_template: str,
    model: str = None,
    chunk_size: int = 20000,
    overlap: int = 500,
) -> List[str]:
    """
    Chunk text and query each chunk.
    
    Args:
        text: Large text to process
        query_template: Query with {chunk} placeholder
        model: Model to use
        chunk_size: Characters per chunk
        overlap: Overlap between chunks
        
    Returns:
        List of responses, one per chunk
    """
    chunks = chunk_text(text, chunk_size, overlap)
    
    results = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...", file=sys.stderr)
        prompt = query_template.replace("{chunk}", chunk)
        result = query(prompt, model=model)
        results.append(result)
    
    return results


def analyze_document(
    filepath: str,
    task: str,
    model: str = None,
    chunk_size: int = 20000,
) -> Dict[str, Any]:
    """
    Analyze a document using the RLM pattern: chunk, analyze, synthesize.
    
    Args:
        filepath: Path to document
        task: What to analyze for (e.g., "Extract thematic elements")
        model: Model to use
        chunk_size: Size of chunks
        
    Returns:
        Dict with chunks, results, and synthesis
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Loaded {len(text):,} characters", file=sys.stderr)
    
    # Phase 1: Chunk and analyze
    query_template = f"{task}\n\nText:\n{{chunk}}"
    chunk_results = chunk_and_query(text, query_template, model, chunk_size)
    
    # Phase 2: Synthesize
    print("Synthesizing results...", file=sys.stderr)
    synthesis_prompt = f"""You analyzed a document in {len(chunk_results)} chunks.
    
Task: {task}

Here are the findings from each chunk:

{chr(10).join(f"=== Chunk {i+1} ==={chr(10)}{r}" for i, r in enumerate(chunk_results))}

Synthesize these findings into a coherent overall answer."""

    synthesis = query(synthesis_prompt, model=model, max_tokens=8000)
    
    return {
        "task": task,
        "chunks": len(chunk_results),
        "chunk_results": chunk_results,
        "synthesis": synthesis,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Query local LLMs via LM Studio")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--query", "-q", type=str, help="Query to send")
    parser.add_argument("--model", "-m", type=str, help="Model to use")
    parser.add_argument("--file", "-f", type=str, help="File to analyze")
    parser.add_argument("--task", "-t", type=str, help="Analysis task")
    
    args = parser.parse_args()
    
    if args.list_models:
        models = list_models()
        if models:
            print("Available models:")
            for m in models:
                print(f"  - {m}")
        else:
            print("No models found. Is LM Studio running?")
    elif args.query:
        print(query(args.query, model=args.model))
    elif args.file and args.task:
        result = analyze_document(args.file, args.task, model=args.model)
        print("\n" + "="*60)
        print("SYNTHESIS")
        print("="*60)
        print(result['synthesis'])
    else:
        parser.print_help()