#!/usr/bin/env python3
import os
import json
import csv
import urllib.request
import urllib.parse
from datetime import datetime,timedelta
import sys

# --- Configuration ---
CGSB_FS_PATH = "/projects/rps/cgsb"
GENCORE_FS_PATH = "/projects/rps/cgsb/gencore/out"

CGSB_VAST_BASE = "/vast/hpc/projects/rps/cgsb"
GENCORE_VAST_BASE = "/vast/hpc/projects/rps/cgsb/gencore/out"

API_BASE_URL = "https://vast-torch-quotas-rtc-api-services.apps.cloud.rt.nyu.edu/vast/capacity?full_path="
OUTPUT_CSV = "../html/data.csv"

def get_vast_capacity(vast_path):
    """Fetches the capacity from the VAST API and converts bytes to TiB."""
    encoded_path = urllib.parse.quote(vast_path, safe='')
    url = API_BASE_URL + encoded_path
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            # Vast 'capacity' array is typically: [logical_used, physical_used, quota]
            bytes_used = data.get(vast_path, {}).get("capacity", [0])[0]
            return bytes_used / (1024 ** 4)
    except Exception as e:
        print(f"Error fetching API for {vast_path}: {e}")
        return 0.0

def main():
    now = datetime.now()

    # A. Force the date to the 1st of the current month (e.g., June 1)
    first_of_this_month = now.replace(day=1)

    # B. Subtract 1 day to land in the previous month (e.g., May 31)
    last_month_date = first_of_this_month - timedelta(days=1)

    # C. Extract the year and month from the PREVIOUS month's date
    year_str = last_month_date.strftime("%Y")
    month_str = last_month_date.strftime("%B")

    # 1. Early Exit Check (Preserve strict first-of-the-month snapshot)
    file_exists = os.path.isfile(OUTPUT_CSV)
    if file_exists:
        with open(OUTPUT_CSV, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Year'] == year_str and row['Month'] == month_str:
                    print(f"Data for {month_str} {year_str} already exists in {OUTPUT_CSV}.")
                    print("Aborting script to preserve the 1st-of-the-month chargeback snapshot.")
                    sys.exit(0) # Stops the script immediately

    labs_data = {}
    
    # 2. Scan CGSB directory
    if os.path.exists(CGSB_FS_PATH):
        for item in os.listdir(CGSB_FS_PATH):
            full_path = os.path.join(CGSB_FS_PATH, item)
            # Ignore files, slurm output, and 'gencore' itself
            if not os.path.isdir(full_path) or item.startswith('slurm-') or item.lower() == 'gencore':
                continue
            
            norm_name = item.lower()
            display_name = item[0].upper() + item[1:] 
            labs_data[norm_name] = {'display_name': display_name, 'cgsb_name': item, 'gencore_name': None}

    # 3. Scan Gencore directory
    if os.path.exists(GENCORE_FS_PATH):
        for item in os.listdir(GENCORE_FS_PATH):
            full_path = os.path.join(GENCORE_FS_PATH, item)
            # Ignore files, slurm output, and 'gencore' itself
            if not os.path.isdir(full_path) or item.startswith('slurm-') or item.lower() == 'gencore':
                continue
            
            norm_name = item.lower()
            if norm_name in labs_data:
                labs_data[norm_name]['gencore_name'] = item
            else:
                display_name = item[0].upper() + item[1:]
                labs_data[norm_name] = {'display_name': display_name, 'cgsb_name': None, 'gencore_name': item}

    # 4. Query the API
    results = []
    print(f"No data found for {month_str} {year_str}. Querying VAST storage API...")
    
    for norm_name, lab_info in labs_data.items():
        cgsb_tib = 0.0
        gencore_tib = 0.0
        
        if lab_info['cgsb_name']:
            vast_path = f"{CGSB_VAST_BASE}/{lab_info['cgsb_name']}"
            cgsb_tib = get_vast_capacity(vast_path)
            
        if lab_info['gencore_name']:
            vast_path = f"{GENCORE_VAST_BASE}/{lab_info['gencore_name']}"
            gencore_tib = get_vast_capacity(vast_path)
            
        total_tib = cgsb_tib + gencore_tib
        
        # Only add labs that have some storage usage
        if total_tib > 0:
            results.append({
                'Lab': lab_info['display_name'],
                'Total_TiB': total_tib,
                'CGSB_TiB': cgsb_tib,
                'Gencore_TiB': gencore_tib
            })

    results.sort(key=lambda x: x['Lab'])

    # 5. Append to CSV
    with open(OUTPUT_CSV, 'a', newline='') as csvfile:
        fieldnames = ['Year', 'Month', 'Lab', 'Total_TiB', 'CGSB_TiB', 'Gencore_TiB']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
        
        if not file_exists:
            writer.writeheader()
            
        for row in results:
            writer.writerow({
                'Year': year_str,
                'Month': month_str,
                'Lab': row['Lab'],
                'Total_TiB': f"{row['Total_TiB']:.3f}",
                'CGSB_TiB': f"{row['CGSB_TiB']:.3f}",
                'Gencore_TiB': f"{row['Gencore_TiB']:.3f}"
            })

    print(f"Success! Appended {len(results)} chargeback records for {month_str} {year_str} to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
