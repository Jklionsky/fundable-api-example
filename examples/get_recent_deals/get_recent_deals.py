#!/usr/bin/env python3
"""
Example: Get recent deals with various filters.

This script demonstrates basic usage of the FundableClient to fetch
recent deals using different filter combinations.
"""

import json
import os
from datetime import datetime, timedelta

from fundable import FundableClient, DataExtractor

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

def print_deal_summary(deal):
    """Print a single deal summary line."""
    amount = f"${deal.get('total_round_raised')}M" if deal.get('total_round_raised') else "Undisclosed"
    round_type = deal.get('round_type', 'Unknown')
    date = deal.get('date', 'N/A')
    num_investors = len(deal.get('investor_ids', []))
    print(f"    {date} | {round_type} | {amount} | {num_investors} investors | company_id: {deal.get('company_id', '?')}")


def test_all_parameters():
    """Test the get_deals function with various parameter combinations."""
    client = FundableClient()

    print("Testing get_deals with various filter combinations...\n")

    # Calculate dynamic date ranges
    today = datetime.now()
    last_7_days_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    last_30_days_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    # Test 1: Basic pagination with last 7 days
    print("=" * 70)
    print(f"TEST 1: Basic pagination (last 7 days: {last_7_days_start} to {today_str})")
    print("=" * 70)
    deals = client.get_deals(
        page=0,
        page_size=5,
        deal_start_date=last_7_days_start,
        deal_end_date=today_str
    )
    print(f"  Found {len(deals)} deals")
    for deal in deals:
        print_deal_summary(deal)

    # Test 2: Financing types filter (object format with type field)
    print(f"\n{'=' * 70}")
    print(f"TEST 2: Financing types filter — SERIES_A + SEED (last 7 days)")
    print("=" * 70)
    deals = client.get_deals(
        financing_types=[{'type': 'SERIES_A'}, {'type': 'SEED'}],
        page_size=5,
        deal_start_date=last_7_days_start,
        deal_end_date=today_str,
    )
    print(f"  Found {len(deals)} deals")
    for deal in deals:
        print_deal_summary(deal)

    # Test 3: Company filters — AI in San Francisco
    # Enrich with company details to prove the location/industry filters work
    print(f"\n{'=' * 70}")
    print(f"TEST 3: Company filters — AI + San Francisco (last 30 days)")
    print("=" * 70)
    deals = client.get_deals(
        super_categories=['artificial-intelligence-e551'],
        locations=['san-francisco-california'],
        page_size=5,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"  Found {len(deals)} deals\n")
    for deal in deals:
        amount = f"${deal.get('total_round_raised')}M" if deal.get('total_round_raised') else "Undisclosed"
        print(f"    {deal.get('round_type', '?')} | {amount} | {deal.get('date', 'N/A')}")
        company = client.get_company(deal['company_id'])
        if company:
            location = company.get('location', {}) or {}
            loc_parts = []
            for key in ['city', 'state', 'country']:
                part = location.get(key)
                if isinstance(part, dict) and part.get('name'):
                    loc_parts.append(part['name'])
            loc_str = ', '.join(loc_parts)
            industries = [ind.get('name') for ind in company.get('industries', [])[:3]]
            super_cats = [sc.get('name') for sc in company.get('super_categories', [])[:3]]
            print(f"      Company: {company.get('name')} ({company.get('domain', 'N/A')})")
            print(f"      Location: {loc_str or 'N/A'}")
            print(f"      Industries: {', '.join(industries) if industries else 'N/A'}")
            print(f"      Super Categories: {', '.join(super_cats) if super_cats else 'N/A'}")
        else:
            print(f"      company_id: {deal.get('company_id')}")

    # Test 4: Deal size range
    print(f"\n{'=' * 70}")
    print(f"TEST 4: Deal size range $100M–$150M (last 30 days)")
    print("=" * 70)
    deals = client.get_deals(
        deal_size_min=100,
        deal_size_max=150,
        page_size=5,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str
    )
    print(f"  Found {len(deals)} deals")
    for deal in deals:
        print_deal_summary(deal)

    # Test 5: Pre-Seed (using pre modifier on financing type)
    print(f"\n{'=' * 70}")
    print(f"TEST 5: Pre-Seed deals (last 30 days)")
    print("=" * 70)
    deals = client.get_deals(
        financing_types=[{'type': 'SEED', 'pre': True}],
        page_size=5,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"  Found {len(deals)} deals")
    for deal in deals:
        amount = f"${deal.get('total_round_raised')}M" if deal.get('total_round_raised') else "Undisclosed"
        label = deal.get('round_type', '?')
        if deal.get('pre'):
            label = f"Pre-{label}"
        if deal.get('extension'):
            label = f"{label} (Extension)"
        print(f"    {deal.get('date', 'N/A')} | {label} | {amount}")

    # Save last result for inspection
    if deals:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, 'sample_deals.json')
        with open(output_path, 'w') as f:
            json.dump(deals, f, indent=2)
        print(f"\n  Saved to {output_path}")


if __name__ == "__main__":
    test_all_parameters()