import json
import time
from datetime import datetime
from pathlib import Path
from config import BASE_DIR, SAFETY_MAX_RUNS_PER_DAY, SAFETY_MAX_RUNS_PER_HOUR

SAFETY_FILE = BASE_DIR / "safety_usage.json"

class SafetyMonitor:
    def __init__(self):
        self._load_stats()
        
    def _load_stats(self):
        if SAFETY_FILE.exists():
            try:
                self.stats = json.loads(SAFETY_FILE.read_text(encoding="utf-8"))
            except:
                self.stats = {"date": "", "daily_count": 0, "timestamps": []}
        else:
            self.stats = {"date": "", "daily_count": 0, "timestamps": []}
            
    def _save_stats(self):
        SAFETY_FILE.write_text(json.dumps(self.stats), encoding="utf-8")
        
    def check_limits(self) -> bool:
        """Return True if safe to run, False if limits exceeded."""
        today = datetime.now().date().isoformat()
        now_ts = time.time()
        
        # Reset if new day
        if self.stats.get("date") != today:
            self.stats = {"date": today, "daily_count": 0, "timestamps": []}
            self._save_stats()
            
        # Clean old timestamps (> 1 hour)
        self.stats["timestamps"] = [ts for ts in self.stats["timestamps"] if now_ts - ts < 3600]
        
        # Check Daily Limit
        if self.stats["daily_count"] >= SAFETY_MAX_RUNS_PER_DAY:
            print(f"🛑 SAFETY STOP: Daily limit reached ({self.stats['daily_count']}/{SAFETY_MAX_RUNS_PER_DAY})")
            return False
            
        # Check Hourly Limit
        if len(self.stats["timestamps"]) >= SAFETY_MAX_RUNS_PER_HOUR:
            print(f"🛑 SAFETY STOP: Hourly limit reached ({len(self.stats['timestamps'])}/{SAFETY_MAX_RUNS_PER_HOUR})")
            return False
            
        return True
        
    def record_run(self):
        """Log a successful run execution."""
        self.stats["daily_count"] += 1
        self.stats["timestamps"].append(time.time())
        self._save_stats()
