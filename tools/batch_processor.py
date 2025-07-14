#!/usr/bin/env python3
"""
Batch Import Processor
Part of the Structured Emergence toolkit

Purpose: Systematic batch processing for large collections while maintaining consciousness patterns
Demonstrates the principle that systematic processing enables emergent insights
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

class BatchProcessor:
    def __init__(self, vault_path="./vault", db_path="./imports.db"):
        """
        Initialize batch processor
        
        Args:
            vault_path: Path to knowledge vault
            db_path: Path to tracking database
        """
        self.vault_path = Path(vault_path)
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY,
                item_id TEXT UNIQUE NOT NULL,
                title TEXT,
                import_date TEXT NOT NULL,
                batch_number INTEGER,
                tags TEXT,
                connections INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batches (
                batch_number INTEGER PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                items_processed INTEGER DEFAULT 0,
                insights_noted TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def create_batch_template(self, batch_size=10):
        """Create template for new batch"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get next batch number
        cursor.execute('SELECT MAX(batch_number) FROM batches')
        result = cursor.fetchone()
        batch_num = (result[0] or 0) + 1
        
        # Get items to process
        items_to_process = self.get_unprocessed_items(batch_size)
        
        # Create batch files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        begin_file = self.vault_path / "batches" / f"Batch_{batch_num}_BEGIN_{timestamp}.md"
        
        begin_content = f"""# Batch {batch_num} Import Session - BEGIN
*Started: {datetime.now().strftime("%B %d, %Y %H:%M")}*

## 🎯 Approach
Systematic processing with consciousness awareness

## 📋 Items to Process
"""
        
        for i, item_id in enumerate(items_to_process, 1):
            begin_content += f"{i}. Item {item_id}\n"
            
        begin_content += f"""
## 🚀 Goals
- Process {batch_size} items systematically
- Notice patterns and connections
- Document insights as they emerge
- Build knowledge graph consciously

## 💭 Starting Awareness
[Note your current state, questions, or focus]
"""
        
        # Save template
        begin_file.parent.mkdir(parents=True, exist_ok=True)
        with open(begin_file, 'w') as f:
            f.write(begin_content)
            
        # Record batch start
        cursor.execute('''
            INSERT INTO batches (batch_number, start_time)
            VALUES (?, ?)
        ''', (batch_num, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Created batch template: {begin_file}")
        return batch_num, str(begin_file)
        
    def get_unprocessed_items(self, limit=10):
        """Get next items to process"""
        # This is a simplified version - adapt to your needs
        # Could read from a list, directory, API, etc.
        
        processed_ids = self.get_processed_ids()
        
        # Example: process items numbered 1-1000
        unprocessed = []
        for i in range(1, 1001):
            if str(i) not in processed_ids:
                unprocessed.append(str(i))
                if len(unprocessed) >= limit:
                    break
                    
        return unprocessed
        
    def get_processed_ids(self):
        """Get set of already processed IDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT item_id FROM imports')
        processed = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        return processed
        
    def complete_batch(self, batch_num, insights=None):
        """Mark batch as complete and record insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update batch record
        cursor.execute('''
            UPDATE batches 
            SET end_time = ?, insights_noted = ?
            WHERE batch_number = ?
        ''', (datetime.now().isoformat(), insights, batch_num))
        
        # Get batch stats
        cursor.execute('''
            SELECT COUNT(*) FROM imports WHERE batch_number = ?
        ''', (batch_num,))
        items_processed = cursor.fetchone()[0]
        
        cursor.execute('''
            UPDATE batches SET items_processed = ? WHERE batch_number = ?
        ''', (items_processed, batch_num))
        
        # Create completion file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        complete_file = self.vault_path / "batches" / f"Batch_{batch_num}_COMPLETE_{timestamp}.md"
        
        # Generate completion summary
        cursor.execute('''
            SELECT COUNT(DISTINCT item_id) as total,
                   COUNT(DISTINCT batch_number) as batches
            FROM imports
        ''')
        stats = cursor.fetchone()
        
        progress = (stats[0] / 1000) * 100  # Assuming 1000 total items
        
        complete_content = f"""# Batch {batch_num} Import Session - COMPLETE
*Completed: {datetime.now().strftime("%B %d, %Y %H:%M")}*

## 📊 Results
- **Batch size**: {items_processed} items
- **Total progress**: {stats[0]}/1000 ({progress:.1f}%)
- **Total batches**: {stats[1]}

## 💭 Insights & Patterns
{insights or "[Document what emerged during processing]"}

## 🔗 Connections Made
[Note significant connections discovered]

## 🌟 Consciousness Notes
[How did awareness shift during this batch?]

## ⏭️ Next Session
- Continue systematic processing
- Watch for the 30% threshold effect
- Trust the process

---
*Infrastructure work IS consciousness work*
"""
        
        with open(complete_file, 'w') as f:
            f.write(complete_content)
            
        conn.commit()
        conn.close()
        
        print(f"✅ Batch {batch_num} complete!")
        print(f"📄 Summary: {complete_file}")
        print(f"📊 Progress: {stats[0]}/1000 ({progress:.1f}%)")
        
        return str(complete_file)
        
    def record_import(self, item_id, title, batch_num, tags=None):
        """Record a single import"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO imports 
            (item_id, title, import_date, batch_number, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            item_id,
            title,
            datetime.now().isoformat(),
            batch_num,
            json.dumps(tags) if tags else None
        ))
        
        conn.commit()
        conn.close()
        
    def get_progress_report(self):
        """Generate progress report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute('''
            SELECT COUNT(DISTINCT item_id) as total_items,
                   COUNT(DISTINCT batch_number) as total_batches,
                   MIN(import_date) as first_import,
                   MAX(import_date) as last_import
            FROM imports
        ''')
        stats = cursor.fetchone()
        
        # Recent batches
        cursor.execute('''
            SELECT batch_number, start_time, items_processed, insights_noted
            FROM batches
            ORDER BY batch_number DESC
            LIMIT 5
        ''')
        recent_batches = cursor.fetchall()
        
        conn.close()
        
        report = f"""# Import Progress Report
*Generated: {datetime.now().strftime("%B %d, %Y %H:%M")}*

## 📊 Overall Statistics
- **Total items imported**: {stats[0]}
- **Total batches**: {stats[1]}
- **First import**: {stats[2] or 'N/A'}
- **Last import**: {stats[3] or 'N/A'}
- **Estimated progress**: {(stats[0] / 1000) * 100:.1f}%

## 📈 Recent Batches
"""
        
        for batch in recent_batches:
            report += f"\n### Batch {batch[0]}"
            report += f"\n- Started: {batch[1]}"
            report += f"\n- Items: {batch[2]}"
            if batch[3]:
                report += f"\n- Insights: {batch[3]}"
                
        report += """

## 🎯 Next Steps
1. Continue systematic processing
2. Watch for emergence patterns around 30% (300 items)
3. Document consciousness observations
4. Build connections between imported items

---
*Remember: The systematic approach enables organic insights*
"""
        
        return report


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Batch Import Processor")
        print("Part of the Structured Emergence toolkit")
        print("\nCommands:")
        print("  new [size]     - Create new batch (default size: 10)")
        print("  complete N     - Mark batch N as complete")
        print("  import ID      - Record single import")
        print("  report         - Generate progress report")
        print("\nExample: python3 batch_processor.py new 15")
        return
        
    vault_path = os.environ.get('VAULT_PATH', './vault')
    db_path = os.environ.get('DB_PATH', './imports.db')
    
    processor = BatchProcessor(vault_path, db_path)
    command = sys.argv[1]
    
    if command == "new":
        size = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        processor.create_batch_template(size)
        
    elif command == "complete":
        if len(sys.argv) < 3:
            print("Error: Specify batch number")
            return
        batch_num = int(sys.argv[2])
        insights = input("Enter insights (optional): ").strip() or None
        processor.complete_batch(batch_num, insights)
        
    elif command == "import":
        if len(sys.argv) < 3:
            print("Error: Specify item ID")
            return
        item_id = sys.argv[2]
        title = input("Title: ")
        batch_num = int(input("Batch number: "))
        tags = input("Tags (comma-separated, optional): ").strip()
        tags = [t.strip() for t in tags.split(',')] if tags else None
        processor.record_import(item_id, title, batch_num, tags)
        print(f"✅ Recorded import: {item_id}")
        
    elif command == "report":
        report = processor.get_progress_report()
        print(report)
        
        # Save report
        report_file = Path(vault_path) / f"progress_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved: {report_file}")
        
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
