
import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

class CSVService:
    def __init__(self, storage_dir: str = "storage/sessions"):
        self.storage_dir = storage_dir
        self.current_file = None
        self.csv_writer = None
        self.current_filename = None
        
        # Ensure directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
        self.header_written = False

    def start_new_session(self, prefix: str = "session", patient_name: str = "Guest"):
        """Create a new CSV file for the session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_filename = f"{prefix}_{timestamp}.csv"
        
        # Sanitize patient name for directory usage
        safe_name = "".join(c for c in patient_name if c.isalnum() or c in (' ', '_', '-')).strip()
        if not safe_name:
            safe_name = "Guest"

        # Determine target directory
        target_dir = os.path.join(self.storage_dir, safe_name)
        os.makedirs(target_dir, exist_ok=True)
        
        filepath = os.path.join(target_dir, self.current_filename)
        
        try:
            self.current_file = open(filepath, mode='w', newline='')
            # Defer writer creation until first row to know columns
            self.csv_writer = None
            self.header_written = False
            
            print(f"Started new CSV session: {filepath}")
            return self.current_filename
        except Exception as e:
            print(f"Error starting CSV session: {e}")
            return None

    def write_row(self, data: Dict[str, Any]):
        """Write a row of data to the current CSV"""
        if self.current_file and data:
            try:
                # Initialize DictWriter on first write
                if not self.header_written:
                    # fixed order for common fields, others sorted
                    fixed_fields = ['timestamp', 'name', 'label']
                    other_fields = sorted([k for k in data.keys() if k not in fixed_fields])
                    fieldnames = fixed_fields + other_fields
                    
                    self.csv_writer = csv.DictWriter(self.current_file, fieldnames=fieldnames)
                    self.csv_writer.writeheader()
                    self.header_written = True

                # Write row
                if self.csv_writer:
                    self.csv_writer.writerow(data)
                    self.current_file.flush() # Ensure it's written to disk
                    
            except Exception as e:
                print(f"Error writing to CSV: {e}")

    def stop_session(self):
        """Close the current CSV file"""
        if self.current_file:
            try:
                self.current_file.close()
                print(f"Closed CSV session: {self.current_filename}")
            except Exception as e:
                print(f"Error closing CSV: {e}")
            finally:
                self.current_file = None
                self.csv_writer = None
                self.current_filename = None
                self.header_written = False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available CSV sessions recursively"""
        sessions = []
        if not os.path.exists(self.storage_dir):
            return []
            
        for root, dirs, files in os.walk(self.storage_dir):
            for f in files:
                if f.endswith(".csv"):
                    full_path = os.path.join(root, f)
                    # Get relative path from storage dir (e.g. "test/session_1.csv" or "session_1.csv")
                    rel_path = os.path.relpath(full_path, self.storage_dir)
                    # Normalize separators for consistency
                    rel_path = rel_path.replace("\\", "/")
                    
                    try:
                        stats = os.stat(full_path)
                        sessions.append({
                            "filename": rel_path,
                            "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                            "size_bytes": stats.st_size
                        })
                    except OSError:
                        pass
        
        # Sort by active (newest first)
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        return sessions

    def get_session_path(self, filename: str) -> Optional[str]:
        """Get full path for a session file"""
        filepath = os.path.join(self.storage_dir, filename)
        if os.path.exists(filepath):
            return filepath
        return None

# Singleton instance
csv_service = CSVService()
