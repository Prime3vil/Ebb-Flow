#!/usr/bin/env python3
"""
compile_tides4fishing.py
Compiles all tide station coordinates, regions, and telemetry URLs across 6 continents:
- North & Central America (/am)
- South America (/su)
- Asia (/as)
- Africa (/af)
- Oceania (/oc)
- Europe (/eu)
Outputs both tide_stations.json and app/src/main/assets/map/tides_data.js.
"""

import urllib.request
import urllib.parse
import re
import json
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

CONTINENT_MAP = {
    'am': 'North & Central America',
    'su': 'South America',
    'as': 'Asia',
    'af': 'Africa',
    'oc': 'Oceania',
    'eu': 'Europe'
}

def build_country_to_continent():
    c2cont = {'us': 'am', 'ca': 'am', 'mx': 'am'}
    for cont in ['am', 'su', 'as', 'af', 'oc', 'eu']:
        url = f"https://tides4fishing.com/{cont}"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as r:
                soup = BeautifulSoup(r.read().decode('utf-8', errors='ignore'), 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    m = re.search(r'tides4fishing\.com/([a-z]{2})(?:/|$)', href)
                    if not m:
                        m = re.match(r'^/([a-z]{2})(?:/|$)', href)
                    if m:
                        c = m.group(1)
                        if c not in CONTINENT_MAP:
                            c2cont[c] = cont
        except Exception as e:
            print(f"Warning mapping continent {cont}: {e}")
    return c2cont

def dms2dec(dms_str):
    # Match degrees, minutes, seconds, and direction
    m = re.search(r'(\d+)\s*°\s*(\d+)\s*[\'′]\s*(\d+(?:\.\d+)?)\s*[\"″]?\s*([NSEWnsew])', dms_str)
    if m:
        deg, minutes, sec, direction = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4).upper()
        dec = deg + minutes / 60.0 + sec / 3600.0
        return -dec if direction in ['S', 'W'] else dec
    m2 = re.search(r'(\d+)\s*°\s*(\d+(?:\.\d+)?)\s*[\'′]?\s*([NSEWnsew])', dms_str)
    if m2:
        deg, minutes, direction = float(m2.group(1)), float(m2.group(2)), m2.group(3).upper()
        dec = deg + minutes / 60.0
        return -dec if direction in ['S', 'W'] else dec
    return None

def fetch_region_stations(url, c2cont):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', class_='sitio_estacion_a')
            
            parts = url.replace('https://tides4fishing.com/', '').strip('/').split('/')
            cc = parts[0] if len(parts) > 0 else 'us'
            region_slug = parts[1] if len(parts) > 1 else ''
            region_name = region_slug.replace('-', ' ').title()
            cont_code = c2cont.get(cc, 'am')

            stations = []
            for a in links:
                text = a.text.strip()
                coords_m = re.search(r'(\d+°.*?N|\d+°.*?S)\s*(\d+°.*?E|\d+°.*?W)', text)
                if coords_m:
                    lat = dms2dec(coords_m.group(1))
                    lng = dms2dec(coords_m.group(2))
                    name = text[:coords_m.start()].strip()
                    href = a.get('href', '')
                    if not href.startswith('http'):
                        href = f"https://tides4fishing.com{href}"
                    slug = href.replace('https://tides4fishing.com/', '').strip('/').split('/')[-1]
                    station_id = f"{cc}_{slug}"
                    
                    if lat is not None and lng is not None and -90 <= lat <= 90 and -180 <= lng <= 180:
                        stations.append({
                            'id': station_id,
                            'name': name,
                            'region': region_name,
                            'country': cc.upper(),
                            'continent': cont_code,
                            'lat': round(lat, 5),
                            'lng': round(lng, 5),
                            'url': href
                        })
            return url, stations
    except Exception as e:
        return url, []

def main():
    print("🌊 Compiling Tides4Fishing Global Stations...")
    c2cont = build_country_to_continent()
    print(f"Mapped {len(c2cont)} countries to 6 continents.")

    sitemap_url = 'https://tides4fishing.com/sitemap.xml'
    print(f"Fetching sitemap from {sitemap_url}...")
    req = urllib.request.Request(sitemap_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        xml = r.read().decode('utf-8', errors='ignore')

    urls = re.findall(r'<loc>(https://tides4fishing\.com/[^<]+)</loc>', xml)
    region_urls = [u for u in urls if len(u.replace('https://tides4fishing.com/', '').strip('/').split('/')) == 2]
    print(f"Found {len(region_urls)} regional pages across all continents.")

    all_stations = []
    seen_ids = set()
    t0 = time.time()
    completed = 0
    total = len(region_urls)

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(fetch_region_stations, u, c2cont): u for u in region_urls}
        for future in as_completed(futures):
            url, stations = future.result()
            completed += 1
            for s in stations:
                if s['id'] not in seen_ids:
                    seen_ids.add(s['id'])
                    all_stations.append(s)
            if completed % 100 == 0 or completed == total:
                print(f"Progress: [{completed}/{total}] regions fetched in {time.time()-t0:.1f}s — Total stations: {len(all_stations)}")

    print(f"\n✅ Finished in {time.time()-t0:.1f}s. Extracted {len(all_stations)} valid tide stations.")

    all_stations.sort(key=lambda x: (x['continent'], x['country'], x['name']))

    base_dir = '/home/prime3vil/Documents/Antigravity/App Dev/Ebb&Flow'
    json_path = os.path.join(base_dir, 'tide_stations.json')
    js_path = os.path.join(base_dir, 'app', 'src', 'main', 'assets', 'map', 'tides_data.js')

    os.makedirs(os.path.dirname(js_path), exist_ok=True)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_stations, f, indent=2, ensure_ascii=False)
    print(f"Saved {json_path} ({os.path.getsize(json_path) / (1024*1024):.2f} MB)")

    compact_data = [
        [
            s['id'],
            s['name'],
            s['region'],
            s['country'],
            s['continent'],
            s['lat'],
            s['lng'],
            s['url'].replace('https://tides4fishing.com', '')
        ]
        for s in all_stations
    ]

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("// Ebb&Flow Global Tide Station Database (Auto-compiled from Tides4Fishing)\n")
        f.write("// Schema: [id, name, region, country, continent, lat, lng, url_path]\n")
        f.write("window.TIDES_STATIONS = ")
        json.dump(compact_data, f, separators=(',', ':'), ensure_ascii=False)
        f.write(";\n")
    print(f"Saved {js_path} ({os.path.getsize(js_path) / (1024*1024):.2f} MB)")

if __name__ == '__main__':
    main()
