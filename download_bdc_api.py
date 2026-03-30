#!/usr/bin/env python3
"""Download FCC BDC data for Sonic Telecom and CA competitors."""

import os
import sys
import json
import time
import subprocess
import zipfile
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from pathlib import Path

# Config
BASE_URL = 'https://bdc.fcc.gov'
AS_OF_DATE = '2025-06-30'
RATE_LIMIT_DELAY = 6.5
DATA_DIR = Path('fcc_data')
DATA_DIR.mkdir(exist_ok=True)

# Sonic + key CA competitors
TARGET_PROVIDERS = {
    '190425': 'Sonic Telecom',
    '130077': 'AT&T',
    '130317': 'Comcast',
    '130258': 'Frontier',
    '330062': 'Race Communications',
}

TARGET_STATES = ['06']  # California only

def load_env():
    env_path = Path('.env')
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")
    return os.environ.get('FCC_USERNAME', ''), os.environ.get('FCC_TOKEN', '')

def list_files(username, token):
    """List available BDC files via API."""
    params = urlencode({
        'category': 'Provider',
        'subcategory': 'Location Coverage',
        'technology_type': 'Fixed Broadband',
    })
    url = f'{BASE_URL}/api/public/map/downloads/listAvailabilityData/{AS_OF_DATE}?{params}'
    
    result = subprocess.run(
        ['curl', '-s', '-H', f'username: {username}', '-H', f'hash_value: {token}', url],
        capture_output=True, text=True, timeout=120
    )
    data = json.loads(result.stdout)
    items = data.get('data', data) if isinstance(data, dict) else data
    return items

def download_file(file_id, username, token, filename_hint=''):
    """Download a single BDC file."""
    url = f'{BASE_URL}/api/public/map/downloads/downloadFile/{file_id}'
    out_path = DATA_DIR / (filename_hint or f'{file_id}.zip')
    
    if out_path.with_suffix('.csv').exists():
        print(f'  Already exists: {out_path.with_suffix(".csv")}')
        return out_path.with_suffix('.csv')
    
    print(f'  Downloading {file_id} -> {out_path}...')
    result = subprocess.run(
        ['curl', '-s', '-o', str(out_path),
         '-H', f'username: {username}', '-H', f'hash_value: {token}', url],
        capture_output=True, text=True, timeout=300
    )
    
    # Check if it's a zip and extract
    if out_path.exists() and zipfile.is_zipfile(str(out_path)):
        with zipfile.ZipFile(str(out_path), 'r') as z:
            z.extractall(DATA_DIR)
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            print(f'  Extracted: {csv_files}')
        out_path.unlink()
        if csv_files:
            return DATA_DIR / csv_files[0]
    elif out_path.exists():
        # Might be a direct CSV
        csv_path = out_path.with_suffix('.csv')
        if out_path.suffix != '.csv':
            out_path.rename(csv_path)
        return csv_path
    
    return out_path

def main():
    username, token = load_env()
    if not username or not token:
        print('Error: Set FCC_USERNAME and FCC_TOKEN in .env')
        sys.exit(1)
    
    list_only = '--list-only' in sys.argv
    force = '--force' in sys.argv
    search = '--search' in sys.argv
    
    print(f'Fetching file list (as of {AS_OF_DATE})...')
    items = list_files(username, token)
    print(f'Total available: {len(items)} files')
    
    if search:
        query = sys.argv[sys.argv.index('--search') + 1].lower() if len(sys.argv) > sys.argv.index('--search') + 1 else ''
        for item in items:
            name = (item.get('provider_name', '') or '').lower()
            if query in name:
                print(f"  {item.get('provider_id', '')} | {item.get('provider_name', '')} | state={item.get('state_fips', '')}")
        return
    
    # Filter to target providers + states
    targets = []
    for item in items:
        pid = str(item.get('provider_id', ''))
        state = str(item.get('state_fips', ''))
        if pid in TARGET_PROVIDERS and state in TARGET_STATES:
            targets.append(item)
    
    print(f'\nTarget files to download: {len(targets)}')
    for t in targets:
        print(f"  {TARGET_PROVIDERS.get(str(t.get('provider_id', '')), '?')} (pid={t.get('provider_id', '')}) state={t.get('state_fips', '')}")
    
    if list_only:
        return
    
    print(f'\nDownloading {len(targets)} files...')
    for i, item in enumerate(targets):
        file_id = item.get('file_id', item.get('id', ''))
        pid = str(item.get('provider_id', ''))
        state = str(item.get('state_fips', ''))
        pname = TARGET_PROVIDERS.get(pid, pid)
        filename = f'bdc_{state}_{pid}_{pname.replace(" ", "_").replace("/", "_")}.zip'
        
        print(f'\n[{i+1}/{len(targets)}] {pname} (CA)')
        download_file(file_id, username, token, filename)
        
        if i < len(targets) - 1:
            print(f'  Rate limit: waiting {RATE_LIMIT_DELAY}s...')
            time.sleep(RATE_LIMIT_DELAY)
    
    print('\nDone!')

if __name__ == '__main__':
    main()
