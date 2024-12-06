import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.utils.crypto import DataCrypto
import json

class StealthAnalyzer:
    def __init__(self):
        self.crypto = DataCrypto()
        self.config = self._load_config()
        self.db_path = self._find_latest_db()
        
    def _load_config(self):
        """Load storage configuration"""
        config_path = os.path.join(os.path.dirname(__file__), 'src', 'config', 'storage.json')
        with open(config_path, 'r') as f:
            return json.load(f)
        
    def _find_latest_db(self):
        """Find most recent database"""
        base_path = self.config['cache_dir']
        latest = None
        latest_time = None
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.startswith("sys_") and file.endswith(".dat"):
                    full_path = os.path.join(root, file)
                    file_time = os.path.getmtime(full_path)
                    if latest_time is None or file_time > latest_time:
                        latest = full_path
                        latest_time = file_time
        return latest

    def get_sample(self, limit=10):
        """Get recent samples in a compact format"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT 
                ts,
                val,
                rid,
                pid,
                spin_time,
                c1
            FROM sys_cache 
            ORDER BY ts DESC 
            LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
            conn.close()
            
            # Decode data
            samples = []
            for _, row in df.iterrows():
                try:
                    num = self.crypto.decode_number(row['val'])
                    ts = pd.to_datetime(row['ts'])
                    color = row['c1']
                    spin_ms = row['spin_time']
                    
                    # Format timestamp as HH:MM:SS
                    time_str = ts.strftime("%H:%M:%S")
                    
                    # Create compact sample string
                    sample = f"{time_str}|{num:02d}|{color[0]}|{spin_ms}"
                    samples.append(sample)
                except:
                    continue
                    
            return samples
            
        except Exception as e:
            return []

    def get_table_summary(self, table_id=None, hours=24):
        """Get summary for specific table"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Encode table ID if provided
            table_condition = ""
            params = [datetime.now() - timedelta(hours=hours)]
            if table_id:
                encoded_rid = self.crypto.encode_number(hash(str(table_id)))
                table_condition = "AND rid = ?"
                params.append(encoded_rid)
            
            query = f"""
            SELECT 
                val,
                COUNT(*) as count,
                AVG(spin_time) as avg_spin,
                MIN(spin_time) as min_spin,
                MAX(spin_time) as max_spin
            FROM sys_cache 
            WHERE ts > ?
            {table_condition}
            GROUP BY val
            ORDER BY count DESC
            """
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            if df.empty:
                return None
                
            summary = {
                'numbers': {},
                'timing': {
                    'avg': int(df['avg_spin'].mean()),
                    'min': int(df['min_spin'].min()),
                    'max': int(df['max_spin'].max())
                }
            }
            
            # Decode top numbers
            for _, row in df.head(5).iterrows():
                num = self.crypto.decode_number(row['val'])
                if num is not None:
                    summary['numbers'][num] = int(row['count'])
                    
            return summary
            
        except Exception as e:
            return None

    def get_provider_stats(self, provider_id=None):
        """Get statistics for specific provider"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Base conditions
            conditions = ["ts > ?"]
            params = [datetime.now() - timedelta(hours=24)]
            
            # Add provider condition if specified
            if provider_id:
                encoded_pid = self.crypto.encode_number(hash(str(provider_id)))
                conditions.append("pid = ?")
                params.append(encoded_pid)
                
            where_clause = " AND ".join(conditions)
            
            query = f"""
            SELECT 
                rid,
                COUNT(*) as spins,
                AVG(spin_time) as avg_time,
                COUNT(DISTINCT val) as unique_nums
            FROM sys_cache 
            WHERE {where_clause}
            GROUP BY rid
            """
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            if df.empty:
                return None
                
            return {
                'tables': len(df),
                'total_spins': int(df['spins'].sum()),
                'avg_time': int(df['avg_time'].mean()),
                'coverage': int(df['unique_nums'].mean())
            }
            
        except Exception as e:
            return None

def main():
    analyzer = StealthAnalyzer()
    
    # Get recent samples
    print("\nRecent samples (Time|Number|Color|SpinMS):")
    samples = analyzer.get_sample(5)
    for s in samples:
        print(s)
        
    # Get table summary
    print("\nTable summary (last 24h):")
    summary = analyzer.get_table_summary()
    if summary:
        print(f"Top numbers: {summary['numbers']}")
        print(f"Spin times: {summary['timing']['avg']}ms (avg)")
        
    # Get provider stats
    print("\nProvider stats (last 24h):")
    stats = analyzer.get_provider_stats()
    if stats:
        print(f"Tables: {stats['tables']}")
        print(f"Coverage: {stats['coverage']}/37")

if __name__ == "__main__":
    main()
