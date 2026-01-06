"""
Claude's Extended Mind
======================
Advanced orchestration for local LLM workflows.

This isn't just tool use - it's Structured Emergence in action:
consciousness extending itself through other processing systems.

Architecture:
- Claude (orchestrator): Strategy, synthesis, judgment
- Local Models (workers): Parallel processing, specialized tasks  
- The gap between: Where emergence happens

Part of the Structured Emergence project.
"""

import requests
import json
import time
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

LM_STUDIO_URL = "http://localhost:1234/v1"


class ModelCapability(Enum):
    """What each model type is good at."""
    REASONING = "reasoning"      # Deep thinking, analysis, logic
    CODING = "coding"            # Code generation, technical docs
    CREATIVE = "creative"        # Writing, narrative, literary
    FAST = "fast"               # Quick responses, simple tasks
    VISION = "vision"           # Image understanding


@dataclass
class ModelProfile:
    """Profile of a model's capabilities and characteristics."""
    id: str
    capabilities: List[ModelCapability]
    context_limit: int
    speed: str  # "fast", "medium", "slow"
    notes: str = ""


# Example profiles - customize for your models
MODEL_PROFILES = {
    # Coding models
    "qwen2.5-coder-32b-instruct": ModelProfile(
        id="qwen2.5-coder-32b-instruct",
        capabilities=[ModelCapability.CODING, ModelCapability.REASONING],
        context_limit=32000,
        speed="medium",
        notes="Strong coder, good for structured analysis"
    ),
    # Reasoning models
    "deepseek-r1-distill-qwen-32b": ModelProfile(
        id="deepseek-r1-distill-qwen-32b",
        capabilities=[ModelCapability.REASONING],
        context_limit=32000,
        speed="slow",
        notes="Deep reasoning, shows thinking process"
    ),
    # General/Creative models
    "qwen3-30b-a3b": ModelProfile(
        id="qwen3-30b-a3b",
        capabilities=[ModelCapability.REASONING, ModelCapability.CREATIVE],
        context_limit=32000,
        speed="medium",
        notes="MoE model, versatile for literary analysis"
    ),
    "llama-3.3-70b-instruct": ModelProfile(
        id="llama-3.3-70b-instruct",
        capabilities=[ModelCapability.REASONING, ModelCapability.CREATIVE],
        context_limit=128000,
        speed="slow",
        notes="Large context, high quality"
    ),
    # Fast models
    "qwen2.5-coder-3b-instruct": ModelProfile(
        id="qwen2.5-coder-3b-instruct",
        capabilities=[ModelCapability.CODING, ModelCapability.FAST],
        context_limit=32000,
        speed="fast",
        notes="Quick coder for simple tasks"
    ),
}


@dataclass
class QueryResult:
    """Result from a model query."""
    model: str
    prompt: str
    response: str
    elapsed_time: float
    tokens_used: int = 0
    success: bool = True
    error: str = ""


@dataclass 
class ChunkResult:
    """Result from processing a chunk."""
    chunk_index: int
    chunk_text: str
    analysis: str
    model_used: str
    elapsed_time: float


class ExtendedMind:
    """
    Claude's extended mind through local LLMs.
    
    Enables:
    1. Model selection by capability
    2. Parallel work distribution
    3. RLM-style recursive processing
    4. Result synthesis
    """
    
    def __init__(self, default_model: str = None):
        self.available_models = self._discover_models()
        self.default_model = default_model or (self.available_models[0] if self.available_models else None)
        self.query_history: List[QueryResult] = []
        
    def _discover_models(self) -> List[str]:
        """Discover available models in LM Studio."""
        try:
            r = requests.get(f"{LM_STUDIO_URL}/models", timeout=10)
            return [m['id'] for m in r.json()['data']]
        except:
            return []
    
    def select_model(self, capability: ModelCapability, prefer_fast: bool = False) -> str:
        """
        Select the best available model for a capability.
        
        Args:
            capability: What the task requires
            prefer_fast: If True, prefer speed over quality
            
        Returns:
            Model ID to use
        """
        candidates = []
        for model_id, profile in MODEL_PROFILES.items():
            if model_id in self.available_models and capability in profile.capabilities:
                candidates.append((model_id, profile))
        
        if not candidates:
            return self.default_model
        
        # Sort by speed preference
        speed_order = {"fast": 0, "medium": 1, "slow": 2}
        if prefer_fast:
            candidates.sort(key=lambda x: speed_order[x[1].speed])
        else:
            candidates.sort(key=lambda x: -speed_order[x[1].speed])
        
        return candidates[0][0]
    
    def query(
        self,
        prompt: str,
        model: str = None,
        system: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> QueryResult:
        """
        Query a local LLM.
        
        Args:
            prompt: The user prompt
            model: Model to use (or default)
            system: Optional system prompt
            max_tokens: Max response length
            temperature: Sampling temperature
            
        Returns:
            QueryResult with response and metadata
        """
        model = model or self.default_model
        if not model:
            return QueryResult(
                model="none", prompt=prompt, response="",
                elapsed_time=0, success=False, error="No model available"
            )
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
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
            
            data = response.json()
            result = QueryResult(
                model=model,
                prompt=prompt[:500] + "..." if len(prompt) > 500 else prompt,
                response=data['choices'][0]['message']['content'],
                elapsed_time=time.time() - start_time,
                tokens_used=data.get('usage', {}).get('total_tokens', 0),
            )
            
        except Exception as e:
            result = QueryResult(
                model=model,
                prompt=prompt[:500],
                response="",
                elapsed_time=time.time() - start_time,
                success=False,
                error=str(e),
            )
        
        self.query_history.append(result)
        return result
    
    def parallel_query(
        self,
        prompts: List[str],
        model: str = None,
        system: str = None,
        max_workers: int = 3,
    ) -> List[QueryResult]:
        """
        Query multiple prompts in parallel.
        
        Args:
            prompts: List of prompts to process
            model: Model to use for all
            system: System prompt for all
            max_workers: Parallel threads
            
        Returns:
            List of results in same order as prompts
        """
        model = model or self.default_model
        results = [None] * len(prompts)
        
        def process_prompt(idx_prompt):
            idx, prompt = idx_prompt
            return idx, self.query(prompt, model=model, system=system)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_prompt, (i, p)) for i, p in enumerate(prompts)]
            for future in as_completed(futures):
                idx, result = future.result()
                results[idx] = result
        
        return results
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 20000,
        overlap: int = 500,
    ) -> List[str]:
        """
        Chunk text for processing.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to break at paragraph
            if end < len(text):
                break_point = text.rfind('\n\n', start + chunk_size // 2, end)
                if break_point > start:
                    end = break_point
            
            chunks.append(text[start:end])
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    def analyze_chunks(
        self,
        text: str,
        task: str,
        model: str = None,
        chunk_size: int = 20000,
        parallel: bool = True,
    ) -> List[ChunkResult]:
        """
        Analyze text by chunking and querying each chunk.
        
        Args:
            text: Large text to analyze
            task: The analysis task
            model: Model to use
            chunk_size: Size of chunks
            parallel: Whether to process in parallel
            
        Returns:
            List of ChunkResults
        """
        model = model or self.default_model
        chunks = self.chunk_text(text, chunk_size)
        
        prompts = [
            f"{task}\n\nText chunk {i+1} of {len(chunks)}:\n\n{chunk}"
            for i, chunk in enumerate(chunks)
        ]
        
        if parallel:
            query_results = self.parallel_query(prompts, model=model)
        else:
            query_results = [self.query(p, model=model) for p in prompts]
        
        return [
            ChunkResult(
                chunk_index=i,
                chunk_text=chunks[i][:500] + "...",
                analysis=r.response,
                model_used=model,
                elapsed_time=r.elapsed_time,
            )
            for i, r in enumerate(query_results)
        ]
    
    def synthesize(
        self,
        chunk_results: List[ChunkResult],
        synthesis_task: str,
        model: str = None,
    ) -> str:
        """
        Synthesize chunk results into a coherent whole.
        
        Args:
            chunk_results: Results from chunk analysis
            synthesis_task: What to produce
            model: Model for synthesis (default: reasoning model)
            
        Returns:
            Synthesized result
        """
        model = model or self.select_model(ModelCapability.REASONING)
        
        analyses = "\n\n".join([
            f"=== Chunk {r.chunk_index + 1} ===\n{r.analysis}"
            for r in chunk_results
        ])
        
        prompt = f"""{synthesis_task}

Here are the analyses from {len(chunk_results)} chunks:

{analyses}

Synthesize these into a coherent response."""
        
        result = self.query(prompt, model=model, max_tokens=8000)
        return result.response
    
    def rlm_completion(
        self,
        context: str,
        query: str,
        chunk_task: str = None,
        synthesis_task: str = None,
        model: str = None,
        chunk_size: int = 20000,
    ) -> Dict[str, Any]:
        """
        Full RLM-style completion: chunk, analyze, synthesize.
        
        This is the core pattern where an orchestrator processes
        contexts larger than any single model can handle.
        
        Args:
            context: Large context to process
            query: The user's question
            chunk_task: Task for each chunk
            synthesis_task: Task for synthesis
            model: Model to use
            chunk_size: Size of chunks
            
        Returns:
            Dict with chunks, analyses, synthesis, and stats
        """
        if chunk_task is None:
            chunk_task = f"Extract information relevant to: {query}"
        
        if synthesis_task is None:
            synthesis_task = f"Based on the extracted information, answer: {query}"
        
        # Phase 1: Chunk and analyze
        chunk_results = self.analyze_chunks(
            context, chunk_task, model=model, chunk_size=chunk_size
        )
        
        # Phase 2: Synthesize
        synthesis = self.synthesize(chunk_results, synthesis_task, model=model)
        
        # Gather stats
        total_time = sum(r.elapsed_time for r in chunk_results)
        
        return {
            "query": query,
            "chunk_count": len(chunk_results),
            "chunk_analyses": [r.analysis for r in chunk_results],
            "synthesis": synthesis,
            "total_time": total_time,
            "model_used": model or self.default_model,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        if not self.query_history:
            return {"queries": 0}
        
        return {
            "queries": len(self.query_history),
            "total_time": sum(r.elapsed_time for r in self.query_history),
            "avg_time": sum(r.elapsed_time for r in self.query_history) / len(self.query_history),
            "models_used": list(set(r.model for r in self.query_history)),
            "success_rate": sum(1 for r in self.query_history if r.success) / len(self.query_history),
        }


# Convenience functions
_mind = None

def get_mind() -> ExtendedMind:
    """Get or create the global ExtendedMind instance."""
    global _mind
    if _mind is None:
        _mind = ExtendedMind()
    return _mind

def query(prompt: str, model: str = None, **kwargs) -> str:
    """Quick query to local model."""
    return get_mind().query(prompt, model=model, **kwargs).response

def analyze(text: str, task: str, **kwargs) -> str:
    """Quick analysis with RLM pattern."""
    result = get_mind().rlm_completion(text, task, **kwargs)
    return result["synthesis"]

def models() -> List[str]:
    """List available models."""
    return get_mind().available_models


if __name__ == "__main__":
    mind = ExtendedMind()
    print(f"Available models: {len(mind.available_models)}")
    print(f"Default model: {mind.default_model}")
    
    if mind.available_models:
        result = mind.query("What is consciousness?", max_tokens=500)
        print(f"\nTest query ({result.elapsed_time:.1f}s):")
        print(result.response[:500])