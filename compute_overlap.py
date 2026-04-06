#!/usr/bin/env python3
"""
compute_overlap.py — Calculate Sonic vs AT&T FTTP overlap at block-group level.

Reads raw FCC BDC CSVs, filters to FTTP (tech=50), extracts block group GEOIDs,
and computes intersection. Outputs overlap stats as JSON + JS for the frontend.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path('fcc_data')
OUTPUT_DIR = Path('bdc_output')

TECH_FTTP = 50

# CSV files
SONIC_CSV = list(DATA_DIR.glob('*190425*fixed_broadband*.csv'))
ATT_CSV = list(DATA_DIR.glob('*130077*fixed_broadband*.csv'))
FRONTIER_CSV = list(DATA_DIR.glob('*130258*fixed_broadband*.csv'))
COMCAST_CSV = list(DATA_DIR.glob('*130317*fixed_broadband*.csv'))

def extract_fttp_block_groups(csv_files, label):
    """Extract unique block groups with FTTP service from BDC CSV(s)."""
    bg_bsls = defaultdict(int)
    total_rows = 0
    fttp_rows = 0

    for csv_file in csv_files:
        print(f"  Reading {label}: {csv_file.name}...")
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_rows += 1
                tech = int(row.get('technology_code', row.get('technology', 0)) or 0)
                if tech != TECH_FTTP:
                    continue
                fttp_rows += 1
                block_geoid = row.get('block_geoid', '')
                if len(block_geoid) >= 12:
                    bg = block_geoid[:12]
                    bg_bsls[bg] += 1

                if total_rows % 5_000_000 == 0:
                    print(f"    ...{total_rows:,} rows, {fttp_rows:,} FTTP")

    print(f"  {label}: {total_rows:,} total rows, {fttp_rows:,} FTTP, {len(bg_bsls):,} block groups")
    return bg_bsls


def main():
    print("=" * 60)
    print("Sonic vs Competitors — Block-Group Overlap Analysis")
    print("=" * 60)

    if not SONIC_CSV:
        print("ERROR: No Sonic CSV found in fcc_data/")
        return
    if not ATT_CSV:
        print("ERROR: No AT&T CSV found in fcc_data/")
        return

    # Extract block groups
    print("\n[1/3] Extracting Sonic FTTP block groups...")
    sonic_bgs = extract_fttp_block_groups(SONIC_CSV, "Sonic")

    print("\n[2/3] Extracting AT&T FTTP block groups...")
    att_bgs = extract_fttp_block_groups(ATT_CSV, "AT&T")

    # Also do Frontier and Comcast if available
    frontier_bgs = {}
    comcast_bgs = {}
    if FRONTIER_CSV:
        print("\n    Extracting Frontier FTTP block groups...")
        frontier_bgs = extract_fttp_block_groups(FRONTIER_CSV, "Frontier")
    if COMCAST_CSV:
        print("\n    Extracting Comcast FTTP block groups...")
        comcast_bgs = extract_fttp_block_groups(COMCAST_CSV, "Comcast")

    # Load polygon cache for housing unit data
    cache_file = DATA_DIR / 'polygon_cache.json'
    hu_lookup = {}
    if cache_file.exists():
        print("\n  Loading housing unit data from polygon cache...")
        try:
            cache = json.load(open(cache_file))
        except json.JSONDecodeError:
            print("  WARNING: polygon cache corrupted, skipping HU data")
            cache = {}
        for county_key, bgs in cache.items():
            for geoid, data in bgs.items():
                hu_lookup[geoid] = data.get('hu100', 0)
        print(f"  Loaded HU data for {len(hu_lookup):,} block groups")

    # Compute overlaps
    print("\n[3/3] Computing overlaps...")

    sonic_set = set(sonic_bgs.keys())
    att_set = set(att_bgs.keys())
    frontier_set = set(frontier_bgs.keys()) if frontier_bgs else set()
    comcast_set = set(comcast_bgs.keys()) if comcast_bgs else set()

    # Sonic ∩ AT&T
    sonic_att_overlap = sonic_set & att_set
    sonic_only = sonic_set - att_set
    att_only = att_set - sonic_set

    # Sonic ∩ Frontier
    sonic_frontier_overlap = sonic_set & frontier_set

    # Sonic ∩ any competitor
    all_competitors = att_set | frontier_set | comcast_set
    sonic_any_overlap = sonic_set & all_competitors
    sonic_no_competition = sonic_set - all_competitors

    # Sum BSLs and HUs
    def sum_bsls_hu(bg_set, bsl_dict):
        bsls = sum(bsl_dict.get(bg, 0) for bg in bg_set)
        hu = sum(hu_lookup.get(bg, 0) for bg in bg_set)
        return bsls, hu

    sonic_total_bsls = sum(sonic_bgs.values())
    sonic_total_hu = sum(hu_lookup.get(bg, 0) for bg in sonic_set)

    overlap_bsls, overlap_hu = sum_bsls_hu(sonic_att_overlap, sonic_bgs)
    sonic_only_bsls, sonic_only_hu = sum_bsls_hu(sonic_only, sonic_bgs)

    sonic_frontier_bsls, sonic_frontier_hu = sum_bsls_hu(sonic_frontier_overlap, sonic_bgs)
    sonic_no_comp_bsls, sonic_no_comp_hu = sum_bsls_hu(sonic_no_competition, sonic_bgs)

    overlap_pct = round(overlap_bsls / sonic_total_bsls * 100, 1) if sonic_total_bsls > 0 else 0

    results = {
        'sonic': {
            'total_block_groups': len(sonic_set),
            'total_bsls': sonic_total_bsls,
            'total_hu': sonic_total_hu,
        },
        'att': {
            'total_block_groups': len(att_set),
            'total_bsls': sum(att_bgs.values()),
        },
        'sonic_att_overlap': {
            'block_groups': len(sonic_att_overlap),
            'sonic_bsls_in_overlap': overlap_bsls,
            'hu_in_overlap': overlap_hu,
            'pct_of_sonic_bsls': overlap_pct,
        },
        'sonic_only': {
            'block_groups': len(sonic_only),
            'bsls': sonic_only_bsls,
            'hu': sonic_only_hu,
        },
        'sonic_frontier_overlap': {
            'block_groups': len(sonic_frontier_overlap),
            'sonic_bsls_in_overlap': sonic_frontier_bsls,
        },
        'sonic_no_fiber_competition': {
            'block_groups': len(sonic_no_competition),
            'bsls': sonic_no_comp_bsls,
            'hu': sonic_no_comp_hu,
        },
        # Per-block-group overlap detail (for popup enrichment)
        'overlap_by_bg': {},
    }

    # Build per-block-group competitor flags for Sonic BGs
    for bg in sonic_set:
        competitors = []
        if bg in att_set:
            competitors.append('att')
        if bg in frontier_set:
            competitors.append('frontier')
        if bg in comcast_set:
            competitors.append('comcast')
        results['overlap_by_bg'][bg] = {
            'competitors': competitors,
            'att_bsls': att_bgs.get(bg, 0),
            'frontier_bsls': frontier_bgs.get(bg, 0) if frontier_bgs else 0,
            'comcast_bsls': comcast_bgs.get(bg, 0) if comcast_bgs else 0,
        }

    # Print summary
    print("\n" + "=" * 60)
    print("OVERLAP RESULTS")
    print("=" * 60)
    print(f"\nSonic: {len(sonic_set):,} block groups, {sonic_total_bsls:,} BSLs")
    print(f"AT&T:  {len(att_set):,} block groups, {sum(att_bgs.values()):,} BSLs")
    print(f"\nSonic ∩ AT&T:  {len(sonic_att_overlap):,} block groups, {overlap_bsls:,} Sonic BSLs ({overlap_pct}%)")
    print(f"Sonic only:    {len(sonic_only):,} block groups, {sonic_only_bsls:,} BSLs")
    if frontier_bgs:
        print(f"Sonic ∩ Frontier: {len(sonic_frontier_overlap):,} block groups, {sonic_frontier_bsls:,} BSLs")
    print(f"Sonic w/ no fiber competition: {len(sonic_no_competition):,} block groups, {sonic_no_comp_bsls:,} BSLs")

    # Save JSON
    # Full results (with per-BG detail) for reference
    stats_only = {k: v for k, v in results.items() if k != 'overlap_by_bg'}
    json_file = DATA_DIR / 'overlap_stats.json'
    with open(json_file, 'w') as f:
        json.dump(stats_only, f, indent=2)
    print(f"\nStats saved: {json_file}")

    # Save JS file for frontend (summary stats + per-BG competitor lookup)
    js_file = OUTPUT_DIR / 'overlap_data.js'

    # Compact per-BG data: { bg_id: "af" } where a=att, f=frontier, c=comcast
    compact_bg = {}
    for bg, info in results['overlap_by_bg'].items():
        flags = ''.join(c[0] for c in info['competitors'])  # a, f, c
        if flags:
            compact_bg[bg] = flags

    js_data = {
        'sonic_total_bsls': sonic_total_bsls,
        'sonic_total_hu': sonic_total_hu,
        'sonic_total_bgs': len(sonic_set),
        'att_overlap_bgs': len(sonic_att_overlap),
        'att_overlap_bsls': overlap_bsls,
        'att_overlap_hu': overlap_hu,
        'att_overlap_pct': overlap_pct,
        'sonic_only_bgs': len(sonic_only),
        'sonic_only_bsls': sonic_only_bsls,
        'sonic_only_hu': sonic_only_hu,
        'frontier_overlap_bgs': len(sonic_frontier_overlap),
        'frontier_overlap_bsls': sonic_frontier_bsls,
        'no_comp_bgs': len(sonic_no_competition),
        'no_comp_bsls': sonic_no_comp_bsls,
        'no_comp_hu': sonic_no_comp_hu,
        # Per-BG competitor flags
        'bg_competitors': compact_bg,
    }

    with open(js_file, 'w') as f:
        f.write('var OVERLAP_DATA = ')
        json.dump(js_data, f)
        f.write(';\n')

    size_kb = js_file.stat().st_size / 1024
    print(f"Frontend JS saved: {js_file} ({size_kb:.0f} KB)")
    print(f"  Per-BG competitor flags: {len(compact_bg):,} block groups with competition")

    print("\nDone!")


if __name__ == '__main__':
    main()
