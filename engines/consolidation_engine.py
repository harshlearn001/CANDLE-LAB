#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidation Engine - Unified Output Analysis
Combines filtered_trades and master_trades into a single prioritized output
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Paths
BASE_PATH = Path(r'H:\CANDLE-LAB\analysis\equity')
FILTERED_PATH = BASE_PATH / 'filtered'
MASTER_PATH = BASE_PATH / 'master'
CONSOLIDATED_PATH = BASE_PATH / 'consolidated'

# Create consolidated folder if it doesn't exist
CONSOLIDATED_PATH.mkdir(exist_ok=True, parents=True)

def get_latest_file(directory, pattern):
    """Get the most recent file matching pattern"""
    files = list(Path(directory).glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[0]

def consolidate_trades(date_str=None):
    """
    Consolidate filtered and master trades into a single ranked output
    """
    # Auto-detect date if not provided
    if not date_str:
        filtered_file = get_latest_file(FILTERED_PATH, 'filtered_trades_*.csv')
        if not filtered_file:
            print("❌ No filtered_trades files found")
            return False
        date_str = filtered_file.stem.split('_')[-1]
    
    filtered_file = FILTERED_PATH / f'filtered_trades_{date_str}.csv'
    master_file = MASTER_PATH / f'master_trades_{date_str}.csv'
    output_file = CONSOLIDATED_PATH / f'consolidated_analysis_{date_str}.csv'
    
    # Check if files exist
    if not filtered_file.exists():
        print(f"❌ {filtered_file} not found")
        return False
    if not master_file.exists():
        print(f"❌ {master_file} not found")
        return False
    
    try:
        # Load data
        print(f"\n📊 CONSOLIDATION ENGINE")
        print(f"{'='*70}")
        print(f"Loading filtered trades from: {filtered_file.name}")
        filtered_df = pd.read_csv(filtered_file)
        
        print(f"Loading master trades from: {master_file.name}")
        master_df = pd.read_csv(master_file)
        
        # Mark source and priority
        filtered_df['SOURCE'] = 'FILTERED'
        filtered_df['PRIORITY'] = 1  # Filtered trades are higher priority
        
        master_df['SOURCE'] = 'MASTER'
        master_df['PRIORITY'] = 2
        
        # Combine: Filtered trades first (higher quality), then master trades not in filtered
        filtered_symbols = set(filtered_df['SYMBOL'].unique())
        master_unique = master_df[~master_df['SYMBOL'].isin(filtered_symbols)].copy()
        
        combined_df = pd.concat([
            filtered_df,
            master_unique
        ], ignore_index=True)
        
        # Sort by PRIORITY (1 = filtered first), then by FINAL_SCORE descending
        combined_df = combined_df.sort_values(
            ['PRIORITY', 'FINAL_SCORE'],
            ascending=[True, False]
        ).reset_index(drop=True)
        
        # Add rank
        combined_df.insert(0, 'RANK', range(1, len(combined_df) + 1))
        
        # Summary statistics
        print(f"\n📈 CONSOLIDATION SUMMARY")
        print(f"{'='*70}")
        print(f"Filtered Trades (High Priority): {len(filtered_df)}")
        print(f"Master Trades (Added): {len(master_unique)}")
        print(f"Total Consolidated: {len(combined_df)}")
        print(f"\n🎯 TOP 10 OPPORTUNITIES")
        print(combined_df[['RANK', 'SYMBOL', 'SOURCE', 'FINAL_SCORE', 'DIRECTION']].head(10).to_string(index=False))
        
        # Save consolidated output
        combined_df.to_csv(output_file, index=False)
        print(f"\n✔ Saved → {output_file}")
        
        # Create summary by source
        print(f"\n📊 BREAKDOWN BY SOURCE")
        print(f"{'='*70}")
        source_summary = combined_df.groupby('SOURCE').agg({
            'SYMBOL': 'count',
            'FINAL_SCORE': ['mean', 'max', 'min']
        }).round(4)
        print(source_summary)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during consolidation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    success = consolidate_trades(date_arg)
    sys.exit(0 if success else 1)
