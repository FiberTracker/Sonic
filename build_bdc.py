#!/usr/bin/env python3
"""
build_bdc.py — Process FCC BDC CSVs into GeoJSON for Sonic FiberComp map.

Reads BDC CSVs, filters to FTTP (tech=50), aggregates by census block group,
fetches TIGERweb polygons (Layer 8 = Census 2020 for HU100/POP100),
and outputs per-provider GeoJSON JS files for the Leaflet map.
"""

import csv
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen

# ============================================
# CONFIGURATION
# ============================================

DATA_DIR = Path('fcc_data')
OUTPUT_DIR = Path('bdc_output')
OUTPUT_DIR.mkdir(exist_ok=True)

CACHE_FILE = DATA_DIR / 'polygon_cache.json'

TIGER_URL = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2020/MapServer/8/query'

# Provider mapping: filename substring -> key
PROVIDER_MAP = {
    '190425': {'key': 'sonic', 'name': 'Sonic Telecom', 'color': '#0C7EC6'},
    '130077': {'key': 'att', 'name': 'AT&T', 'color': '#00759E'},
    '130317': {'key': 'comcast', 'name': 'Comcast', 'color': '#4972AC'},
    '130258': {'key': 'frontier', 'name': 'Frontier', 'color': '#469A6C'},
    '330062': {'key': 'race', 'name': 'Race Communications', 'color': '#879420'},
}

TECH_FTTP = 50  # Fiber to the Premises


# ============================================
# STEP 1: READ BDC CSVs
# ============================================

def read_bdc_csvs():
    """Read all BDC CSVs and return per-provider block group BSL counts."""
    provider_bg_counts = {}  # provider_key -> { bg_geoid: bsl_count }

    csv_files = sorted(DATA_DIR.glob('*.csv'))
    if not csv_files:
        print("ERROR: No CSV files found in fcc_data/")
        sys.exit(1)

    for csv_file in csv_files:
        # Detect provider from filename
        pid = None
        for p in PROVIDER_MAP:
            if p in csv_file.name:
                pid = p
                break
        if not pid:
            print(f"  Skipping unknown file: {csv_file.name}")
            continue

        pinfo = PROVIDER_MAP[pid]
        pkey = pinfo['key']
        print(f"\n  Processing {pinfo['name']} ({csv_file.name})...")

        if pkey not in provider_bg_counts:
            provider_bg_counts[pkey] = defaultdict(int)

        row_count = 0
        fttp_count = 0

        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1
                tech = int(row.get('technology_code', row.get('technology', 0)) or 0)
                if tech != TECH_FTTP:
                    continue
                fttp_count += 1

                # Block GEOID is 15 digits; block group = first 12
                block_geoid = row.get('block_geoid', '')
                if len(block_geoid) >= 12:
                    bg = block_geoid[:12]
                    provider_bg_counts[pkey][bg] += 1

        print(f"    Total rows: {row_count:,}, FTTP rows: {fttp_count:,}, Block groups: {len(provider_bg_counts[pkey]):,}")

    return provider_bg_counts


# ============================================
# STEP 2: FETCH TIGERWEB POLYGONS
# ============================================

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def fetch_county_bgs(state_fips, county_fips, cache):
    """Fetch all block group polygons for a county from TIGERweb Layer 8."""
    cache_key = f"{state_fips}_{county_fips}"
    if cache_key in cache:
        return cache[cache_key]

    where = f"STATE='{state_fips}'+AND+COUNTY='{county_fips}'"
    url = (TIGER_URL + "?where=" + where +
           "&outFields=GEOID,AREALAND,HU100,POP100" +
           "&f=geojson&outSR=4326&returnGeometry=true")

    retries = 3
    for attempt in range(retries):
        try:
            with urlopen(url, timeout=60) as resp:
                data = json.loads(resp.read())
            features = data.get('features', [])
            result = {}
            for feat in features:
                props = feat.get('properties', {})
                geoid = props.get('GEOID', '')
                result[geoid] = {
                    'geometry': feat.get('geometry'),
                    'hu100': int(props.get('HU100', 0) or 0),
                    'pop100': int(props.get('POP100', 0) or 0),
                    'arealand': float(props.get('AREALAND', 0) or 0),
                }
            cache[cache_key] = result
            return result
        except Exception as e:
            if attempt < retries - 1:
                print(f"      Retry {attempt+1} for {state_fips}/{county_fips}: {e}")
                time.sleep(2)
            else:
                print(f"      FAILED {state_fips}/{county_fips}: {e}")
                return {}


def fetch_all_polygons(provider_bg_counts):
    """Fetch TIGERweb polygons for all block groups across all providers."""
    # Collect all unique counties needed
    counties = set()
    for pkey, bg_counts in provider_bg_counts.items():
        for bg in bg_counts:
            state = bg[:2]
            county = bg[2:5]
            counties.add((state, county))

    print(f"\n  Unique counties to fetch: {len(counties)}")

    cache = load_cache()
    cached_count = sum(1 for s, c in counties if f"{s}_{c}" in cache)
    print(f"  Already cached: {cached_count}, need to fetch: {len(counties) - cached_count}")

    all_bgs = {}  # geoid -> {geometry, hu100, pop100, arealand}

    for i, (state, county) in enumerate(sorted(counties)):
        if f"{state}_{county}" in cache:
            county_bgs = cache[f"{state}_{county}"]
        else:
            if i > 0 and f"{state}_{county}" not in cache:
                time.sleep(0.5)  # be nice to TIGERweb
            print(f"    [{i+1}/{len(counties)}] Fetching {state}/{county}...", end=' ', flush=True)
            county_bgs = fetch_county_bgs(state, county, cache)
            print(f"{len(county_bgs)} BGs")

            # Save cache periodically
            if (i + 1) % 20 == 0:
                save_cache(cache)

        all_bgs.update(county_bgs)

    save_cache(cache)
    print(f"  Total polygons loaded: {len(all_bgs)}")
    return all_bgs


# ============================================
# STEP 3: BUILD GEOJSON OUTPUT
# ============================================

def build_geojson(provider_bg_counts, all_bgs):
    """Build per-provider GeoJSON files with coverage data."""
    stats = {}

    for pkey, bg_counts in provider_bg_counts.items():
        pinfo = None
        for pid, info in PROVIDER_MAP.items():
            if info['key'] == pkey:
                pinfo = info
                break
        if not pinfo:
            continue

        features = []
        total_bsls = 0
        total_hu = 0
        total_pop = 0
        matched_bgs = 0

        for bg, bsl_count in bg_counts.items():
            if bg not in all_bgs:
                continue

            bg_data = all_bgs[bg]
            if not bg_data.get('geometry'):
                continue

            matched_bgs += 1
            hu = bg_data['hu100']
            pop = bg_data['pop100']
            area_km2 = bg_data['arealand'] / 1e6 if bg_data['arealand'] else 0

            coverage_pct = round(bsl_count / hu * 100, 1) if hu > 0 else 0
            density = round(bsl_count / area_km2, 1) if area_km2 > 0 else 0

            total_bsls += bsl_count
            total_hu += hu
            total_pop += pop

            features.append({
                'type': 'Feature',
                'properties': {
                    'id': bg,
                    'bsls': bsl_count,
                    'hu100': hu,
                    'pop100': pop,
                    'coveragePct': min(coverage_pct, 100),
                    'density': density,
                },
                'geometry': bg_data['geometry'],
            })

        geojson = {
            'type': 'FeatureCollection',
            'features': features,
        }

        out_file = OUTPUT_DIR / f"{pkey}_bdc.js"
        with open(out_file, 'w') as f:
            f.write(f"const BDC_{pkey.upper()} = ")
            json.dump(geojson, f)
            f.write(";")

        stats[pkey] = {
            'name': pinfo['name'],
            'total_bsls': total_bsls,
            'total_hu': total_hu,
            'total_pop': total_pop,
            'block_groups': matched_bgs,
            'overall_coverage': round(total_bsls / total_hu * 100, 1) if total_hu > 0 else 0,
        }

        print(f"\n  {pinfo['name']}:")
        print(f"    FTTP BSLs: {total_bsls:,}")
        print(f"    Housing units in footprint: {total_hu:,}")
        print(f"    Block groups: {matched_bgs:,}")
        print(f"    Overall coverage: {stats[pkey]['overall_coverage']}%")
        print(f"    Output: {out_file} ({out_file.stat().st_size / 1e6:.1f} MB)")

    # Write stats
    stats_file = DATA_DIR / 'provider_stats.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\n  Stats: {stats_file}")

    return stats


# ============================================
# MAIN
# ============================================

def main():
    print("=" * 60)
    print("Sonic FiberComp — BDC Builder")
    print("=" * 60)

    # Only process Sonic by default, or all with --all
    process_all = '--all' in sys.argv
    sonic_only = '--sonic-only' in sys.argv

    print("\n[1/3] Reading BDC CSVs...")
    provider_bg_counts = read_bdc_csvs()

    if sonic_only:
        provider_bg_counts = {k: v for k, v in provider_bg_counts.items() if k == 'sonic'}
    elif not process_all:
        # Default: Sonic + competitors (but skip AT&T/Comcast to keep fast — huge files)
        # Process all that were loaded
        pass

    print("\n[2/3] Fetching TIGERweb polygons...")
    all_bgs = fetch_all_polygons(provider_bg_counts)

    print("\n[3/3] Building GeoJSON output...")
    stats = build_geojson(provider_bg_counts, all_bgs)

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)

    return stats


if __name__ == '__main__':
    main()
