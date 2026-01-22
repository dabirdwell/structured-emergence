#!/usr/bin/env python3
"""
Hypergraph Incremental Updater

Watches vault directories for changes and incrementally updates the hypergraph.
Adds confidence decay and source freshness tracking.

Key features:
- Detect new/modified documents since last update
- Extract relations and merge into existing graph
- Track source freshness (when was each doc last processed?)
- Apply confidence decay to old assertions
- Flag stale knowledge needing refresh
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import pickle

from temporal_hypergraph import TemporalHypergraph, Provenance, ChangeType
from nested_hypergraph import NestedHypergraph, HyperEdge


@dataclass
class SourceFreshness:
    """Tracks when a source document was last processed."""
    path: str
    last_hash: str  # Content hash when last processed
    last_processed: datetime
    last_modified: datetime
    extraction_count: int = 0  # How many hyperedges from this doc
    needs_refresh: bool = False


@dataclass
class UpdateState:
    """Persistent state for incremental updates."""
    last_full_scan: Optional[datetime] = None
    sources: Dict[str, SourceFreshness] = field(default_factory=dict)
    total_updates: int = 0
    last_update: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'last_full_scan': self.last_full_scan.isoformat() if self.last_full_scan else None,
            'sources': {
                k: {
                    'path': v.path,
                    'last_hash': v.last_hash,
                    'last_processed': v.last_processed.isoformat(),
                    'last_modified': v.last_modified.isoformat(),
                    'extraction_count': v.extraction_count,
                    'needs_refresh': v.needs_refresh
                }
                for k, v in self.sources.items()
            },
            'total_updates': self.total_updates,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'UpdateState':
        state = cls()
        state.last_full_scan = datetime.fromisoformat(d['last_full_scan']) if d.get('last_full_scan') else None
        state.total_updates = d.get('total_updates', 0)
        state.last_update = datetime.fromisoformat(d['last_update']) if d.get('last_update') else None
        
        for k, v in d.get('sources', {}).items():
            state.sources[k] = SourceFreshness(
                path=v['path'],
                last_hash=v['last_hash'],
                last_processed=datetime.fromisoformat(v['last_processed']),
                last_modified=datetime.fromisoformat(v['last_modified']),
                extraction_count=v.get('extraction_count', 0),
                needs_refresh=v.get('needs_refresh', False)
            )
        return state
    
    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'UpdateState':
        if not os.path.exists(path):
            return cls()
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))


def file_hash(path: str) -> str:
    """Compute hash of file contents."""
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def scan_directory(dir_path: str, extensions: List[str] = ['.md']) -> List[Tuple[str, datetime, str]]:
    """
    Scan a directory for files.
    Returns list of (path, mtime, content_hash).
    """
    results = []
    dir_path = Path(dir_path)
    
    for ext in extensions:
        for file_path in dir_path.rglob(f'*{ext}'):
            # Skip hidden files
            if any(part.startswith('.') for part in file_path.parts):
                continue
                
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                content_hash = file_hash(str(file_path))
                results.append((str(file_path), mtime, content_hash))
            except Exception as e:
                print(f"  Warning: Could not read {file_path}: {e}")
    
    return results


def find_changed_files(state: UpdateState, directories: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Find files that are new or modified since last scan.
    
    Args:
        state: Current update state
        directories: Dict of name -> path to scan
    
    Returns:
        Dict of directory_name -> [changed_file_paths]
    """
    changed = {}
    
    for name, path in directories.items():
        dir_changed = []
        files = scan_directory(path)
        
        for file_path, mtime, content_hash in files:
            if file_path not in state.sources:
                # New file
                dir_changed.append(file_path)
            elif state.sources[file_path].last_hash != content_hash:
                # Modified file
                dir_changed.append(file_path)
        
        if dir_changed:
            changed[name] = dir_changed
    
    return changed


def apply_confidence_decay(thg: TemporalHypergraph, 
                           decay_rate: float = 0.1,
                           decay_period_days: int = 90) -> int:
    """
    Apply confidence decay to old assertions.
    
    Assertions older than decay_period_days lose (decay_rate * periods_elapsed)
    from their confidence, minimum 0.1.
    
    Returns number of assertions affected.
    """
    now = datetime.now()
    affected = 0
    
    for version in thg.versions.values():
        if version.change_type == ChangeType.RETRACTED:
            continue
            
        age_days = (now - version.timestamp).days
        if age_days > decay_period_days:
            periods = age_days // decay_period_days
            for prov in version.provenance:
                original_conf = prov.confidence
                decay = decay_rate * periods
                prov.confidence = max(0.1, original_conf - decay)
                if prov.confidence < original_conf:
                    affected += 1
                    prov.metadata['decay_applied'] = {
                        'original': original_conf,
                        'periods': periods,
                        'decay_date': now.isoformat()
                    }
    
    return affected


def flag_stale_sources(state: UpdateState, stale_days: int = 180) -> List[str]:
    """
    Flag sources that haven't been refreshed in stale_days.
    Returns list of stale source paths.
    """
    now = datetime.now()
    stale = []
    
    for path, freshness in state.sources.items():
        age = (now - freshness.last_processed).days
        if age > stale_days:
            freshness.needs_refresh = True
            stale.append(path)
    
    return stale


def get_update_summary(state: UpdateState) -> Dict:
    """Get summary of hypergraph update state."""
    now = datetime.now()
    
    # Count sources by freshness
    fresh = 0  # < 30 days
    aging = 0  # 30-90 days
    stale = 0  # 90-180 days
    very_stale = 0  # > 180 days
    
    for freshness in state.sources.values():
        age = (now - freshness.last_processed).days
        if age < 30:
            fresh += 1
        elif age < 90:
            aging += 1
        elif age < 180:
            stale += 1
        else:
            very_stale += 1
    
    return {
        'total_sources': len(state.sources),
        'freshness': {
            'fresh_under_30d': fresh,
            'aging_30_90d': aging,
            'stale_90_180d': stale,
            'very_stale_over_180d': very_stale
        },
        'needs_refresh': sum(1 for s in state.sources.values() if s.needs_refresh),
        'total_updates': state.total_updates,
        'last_update': state.last_update.isoformat() if state.last_update else None,
        'last_full_scan': state.last_full_scan.isoformat() if state.last_full_scan else None
    }


if __name__ == '__main__':
    import sys
    
    print("""
Hypergraph Incremental Updater

This module provides functions for incremental hypergraph updates:

- scan_directory(path) - Find all markdown files
- find_changed_files(state, dirs) - Detect new/modified files
- apply_confidence_decay(thg) - Decay old assertion confidence
- flag_stale_sources(state) - Identify sources needing refresh
- get_update_summary(state) - Get freshness statistics

See README.md for integration examples.
    """)
