"""Combine the 2024 and 2026 apartment sale datasets and clean them.

Usage: python clean_data.py [DATA_2024_CSV] [DATA_2026_CSV] [OUTPUT_CSV]
"""
import csv
import math
import re
import sys
from collections import Counter

DATA_DIR = 'realestate/spiders'
DATA_2024_CSV = f'{DATA_DIR}/apartmentsdata.csv'        # scraped May 2024 (4zida + halooglasi)
DATA_2026_CSV = f'{DATA_DIR}/apartmentsdata2026.csv'    # scraped September 2026 (4zida)

OUTPUT_CSV = f'{DATA_DIR}/apartments_dataset.csv'

COLUMNS = ['title', 'city', 'location', 'price', 'square_price', 'area', 'rooms', 'floor', 'source', 'year']

# Sources are published as numeric codes instead of website names
SOURCE_CODES = {'4zida': 1, 'halooglasi': 2}

MIN_AREA, MAX_AREA = 10, 1000
MIN_PRICE, MAX_PRICE = 9900, 10_000_000
# Also catches prices entered in dinars instead of euros
MIN_SQUARE_PRICE, MAX_SQUARE_PRICE = 200, 20000


def clean_text(value):
    return re.sub(r'\s+', ' ', value.replace('\xa0', ' ')).strip()


def clean_location(value):
    parts = (clean_text(part) for part in value.split(','))
    return ', '.join(part for part in parts if part)


def read_rows(path, year):
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = [h for h in next(reader) if h]
        assert header[-1] == 'title', f'{path}: expected title as the last column'
        for values in reader:
            # Titles containing commas were written unquoted in the 2024 export and spilled into trailing columns
            row = dict(zip(header, values))
            row['title'] = ', '.join(v.strip() for v in values[len(header) - 1:] if v.strip())
            row['year'] = year
            yield row


def clean_row(row, stats):
    row['title'] = clean_text(row['title'])
    row['city'] = clean_text(row['city'])
    row['location'] = clean_location(row['location'])
    row['source'] = SOURCE_CODES[clean_text(row['source'])]
    row['floor'] = clean_text(row['floor']).lower() or 'n/a'

    try:
        row['price'] = int(float(row['price']))
    except (TypeError, ValueError):
        stats['dropped: undefined price'] += 1
        return None

    try:
        row['area'] = int(math.ceil(float(row['area'])))
        row['rooms'] = float(row['rooms'])
    except ValueError:
        stats['dropped: unparseable number'] += 1
        return None

    if not all(row[c] for c in ('title', 'city', 'location')):
        stats['dropped: missing text field'] += 1
        return None

    if not MIN_AREA <= row['area'] <= MAX_AREA:
        stats['dropped: implausible area'] += 1
        return None

    if row['price'] < MIN_PRICE:
        stats['dropped: price below 9900 €'] += 1
        return None

    if row['price'] > MAX_PRICE:
        stats['dropped: implausible price'] += 1
        return None

    # Recompute €/m² from price and area so every row uses the same definition
    square_price = int(round(row['price'] / row['area']))
    try:
        recorded = float(row['square_price'])
    except (TypeError, ValueError):
        recorded = None
    if recorded is not None and abs(recorded - square_price) > 0.05 * square_price:
        stats['fixed: square_price mismatch'] += 1
    row['square_price'] = square_price

    if not MIN_SQUARE_PRICE <= square_price <= MAX_SQUARE_PRICE:
        stats['dropped: implausible price per m²'] += 1
        return None

    return {c: row[c] for c in COLUMNS}


def main(data_2024_csv=DATA_2024_CSV, data_2026_csv=DATA_2026_CSV, output_csv=OUTPUT_CSV):
    stats = Counter()
    raw = list(read_rows(data_2024_csv, 2024)) + list(read_rows(data_2026_csv, 2026))
    stats['input rows'] = len(raw)

    # Duplicates are only removed within a year; the same ad in both years is a separate observation
    cleaned, seen = [], set()
    for row in raw:
        row = clean_row(row, stats)
        if row is None:
            continue
        key = tuple(row.values())
        if key in seen:
            stats['dropped: duplicate'] += 1
            continue
        seen.add(key)
        cleaned.append(row)

    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(cleaned)

    stats['output rows'] = len(cleaned)
    for key, value in stats.items():
        print(f'{key}: {value}')
    print(dict(Counter(r['year'] for r in cleaned)))


if __name__ == '__main__':
    main(*sys.argv[1:])
