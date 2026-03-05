#!/usr/bin/env python3
"""
Example: List and filter investors using various criteria.

This script demonstrates usage of the FundableClient to fetch investors
using investor filters (who the investor is) and portfolio filters
(who they've invested in).
"""

import csv
import json
import os
from datetime import datetime, timedelta

from fundable import FundableClient

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
CSV_PATH = os.path.join(REPO_ROOT, 'test_sets', 'San_Francisco_2026-03-05.csv')


def print_investor(investor):
    """Print a single investor summary.

    Fields:
    - total_deal_count: all-time deal count
    - lead_deal_count: all-time deals where investor was lead
    - recent_deal_count: deals in the last 12 months
    - filtered_deal_count: deals matching your active portfolio filters
      (date range, industry, location, financing type, etc.)
    """
    name = investor.get('name', 'Unknown')
    domain = investor.get('domain', 'N/A')
    total = investor.get('total_deal_count', 0)
    recent = investor.get('recent_deal_count', 0)
    leads = investor.get('lead_deal_count', 0)
    filtered = investor.get('filtered_deal_count')

    line = f"  {name} ({domain})"
    line += f" — {total} all-time, {leads} led (all-time), {recent} last 12mo"
    if filtered is not None:
        line += f", {filtered} matching filters"
    print(line)


def main():
    client = FundableClient()

    today = datetime.now()
    last_30_days = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    # --- Test 1: Basic — recent investors ---
    print("=" * 60)
    print("TEST 1: Recent investors (last 30 days)")
    print("=" * 60)
    investors = client.get_investors(
        page_size=5,
        deal_start_date=last_30_days,
        deal_end_date=today_str,
        sort_by='Matching Deals',
    )
    print(f"Found {len(investors)} investors (sorted by matching deals)\n")
    for inv in investors:
        print_investor(inv)

    # --- Test 2: Financing type filter ---
    print(f"\n{'=' * 60}")
    print("TEST 2: Investors in SEED deals (last 30 days)")
    print("=" * 60)
    investors = client.get_investors(
        financing_types=['SEED'],
        page_size=5,
        deal_start_date=last_30_days,
        deal_end_date=today_str,
        sort_by='Matching Deals',
    )
    print(f"Found {len(investors)} investors (sorted by matching deals)\n")
    for inv in investors:
        print_investor(inv)

    # --- Test 3: Industry + location ---
    print(f"\n{'=' * 60}")
    print("TEST 3: Investors in AI companies in San Francisco (last 30 days)")
    print("=" * 60)
    investors = client.get_investors(
        super_categories=['artificial-intelligence-e551'],
        locations=['san-francisco-california'],
        page_size=5,
        deal_start_date=last_30_days,
        deal_end_date=today_str,
        sort_by='Matching Deals',
    )
    print(f"Found {len(investors)} investors (sorted by matching deals)\n")
    for inv in investors:
        print_investor(inv)

    # --- Test 4: Investor domain batch lookup ---
    print(f"\n{'=' * 60}")
    print("TEST 4: Batch lookup by investor domain")
    print("=" * 60)
    vc_domains = ['sequoiacap.com', 'a16z.com', 'accel.com', 'khoslaventures.com', 'ycombinator.com']
    investors = client.get_investors(
        investor_domains=vc_domains,
        page_size=100,
    )
    print(f"Matched {len(investors)} / {len(vc_domains)} investor domains\n")
    for inv in investors:
        print_investor(inv)

    # --- Test 5: Portfolio company domain filter ---
    print(f"\n{'=' * 60}")
    print("TEST 5: Find investors in SF companies (from CSV test set)")
    print("=" * 60)
    # Load first 10 domains from CSV
    company_domains = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                d = row.get('Website', '').strip()
                if d:
                    company_domains.append(d)
                if len(company_domains) >= 10:
                    break

    investors = client.get_investors(
        domains=company_domains,
        page_size=10,
        sort_by='Matching Deals',
    )
    print(f"Found {len(investors)} investors across {len(company_domains)} portfolio companies (sorted by matching deals)\n")
    for inv in investors:
        print_investor(inv)

    # --- Save sample output ---
    if investors:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, 'sample_investors.json')
        with open(output_path, 'w') as f:
            json.dump(investors, f, indent=2)
        print(f"\nSaved {len(investors)} investors to {output_path}")

    # --- Print full sample ---
    if investors:
        print(f"\n{'=' * 60}")
        print("SAMPLE INVESTOR OUTPUT:")
        print("=" * 60)
        print(json.dumps(investors[0], indent=2, default=str))


if __name__ == "__main__":
    main()
