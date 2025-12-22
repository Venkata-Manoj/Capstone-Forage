"""
Local Database Management
Replaces Supabase with local JSON storage
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from config import settings

logger = logging.getLogger(__name__)

class LocalDatabase:
    """Manages local JSON-based database"""
    
    def __init__(self):
        self.data_dir = Path(settings.generated_dir) / "db"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.files_path = self.data_dir / "reference_files.json"
        self.reports_path = self.data_dir / "reports.json"
        
        # Initialize files if they don't exist
        self._init_db_file(self.files_path)
        self._init_db_file(self.reports_path)
        
    def _init_db_file(self, path: Path):
        """Initialize empty JSON array in file if not exists"""
        if not path.exists():
            with open(path, 'w') as f:
                json.dump([], f)
                
    def _read_json(self, path: Path) -> List[Dict]:
        """Read data from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read DB {path}: {e}")
            return []
            
    def _write_json(self, path: Path, data: List[Dict]):
        """Write data to JSON file"""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write DB {path}: {e}")

    # --- Reference Files Operations ---
    
    def add_file(self, file_data: Dict):
        """Add a reference file record"""
        files = self._read_json(self.files_path)
        # Remove existing if any (update)
        files = [f for f in files if f['id'] != file_data['id']]
        files.append(file_data)
        self._write_json(self.files_path, files)
        
    def get_files(self) -> List[Dict]:
        """Get all reference files"""
        return self._read_json(self.files_path)
        
    def get_file(self, file_id: str) -> Optional[Dict]:
        """Get a specific file by ID"""
        files = self._read_json(self.files_path)
        for f in files:
            if f['id'] == file_id:
                return f
        return None

    # --- Reports Operations ---
    
    def add_report(self, report_data: Dict):
        """Add or update a report record"""
        reports = self._read_json(self.reports_path)
        # Remove existing if any (update)
        reports = [r for r in reports if r['id'] != report_data['id']]
        reports.append(report_data)
        self._write_json(self.reports_path, reports)
        
    def get_reports(self) -> List[Dict]:
        """Get all reports"""
        return self._read_json(self.reports_path)
        
    def get_report(self, report_id: str) -> Optional[Dict]:
        """Get a specific report by ID"""
        reports = self._read_json(self.reports_path)
        for r in reports:
            if r['id'] == report_id:
                return r
        return None
        
    def update_report_status(self, report_id: str, status: str, **kwargs):
        """Update report status and other fields"""
        reports = self._read_json(self.reports_path)
        updated = False
        for r in reports:
            if r['id'] == report_id:
                r['status'] = status
                r.update(kwargs)
                updated = True
                break
        
        if updated:
            self._write_json(self.reports_path, reports)


# Global Database Instance
_db_instance = None

def get_db() -> LocalDatabase:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = LocalDatabase()
    return _db_instance

# Deprecated but kept for compatibility with existing imports initially (will trigger cleanup)
class Tables:
    """Database table name constants (Legacy)"""
    USERS = "users"
    REFERENCE_FILES = "reference_files"
    REPORTS = "reports"
    REVIEWS = "reviews"
    VERSIONS = "versions"
