#!/usr/bin/env python3
"""
Example: Get companies with recent raises using various filters.

This script demonstrates usage of the FundableClient to fetch
companies filtered by their latest funding round, using different
filter combinations available on the /companies endpoint.
"""

import json
import os
from datetime import datetime, timedelta

from fundable import FundableClient, format_usd

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')


def print_company(company):
    """Print a single company summary with latest deal info."""
    name = company.get('name', 'Unknown')
    domain = company.get('domain', 'N/A')
    total = format_usd(company.get('total_raised'))
    latest = company.get('latest_deal', {}) or {}
    deal_type = latest.get('type', 'N/A')
    deal_size = format_usd(latest.get('size_usd') or latest.get('size_native'))
    deal_date = (latest.get('date') or 'N/A')[:10]
    similarity = company.get('similarity')
    sim_str = f" | similarity: {similarity:.2f}" if similarity else ""
    print(f"    {name} ({domain}) | Total Raised: {total} | Latest: {deal_type} {deal_size} ({deal_date}){sim_str}")


def test_all_parameters():
    """Test the get_companies function with various parameter combinations."""
    client = FundableClient()

    print("Testing get_companies with various filter combinations...\n")

    # Calculate dynamic date ranges
    today = datetime.now()
    last_7_days_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    last_30_days_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    # Test 1: Basic pagination with last 7 days
    print("=" * 70)
    print(f"TEST 1: Basic pagination (last 7 days: {last_7_days_start} to {today_str})")
    print("=" * 70)
    companies = client.get_companies(
        page=0,
        page_size=5,
        deal_start_date=last_7_days_start,
        deal_end_date=today_str
    )
    print(f"  Found {len(companies)} companies")
    for company in companies:
        print_company(company)

    # Test 2: Financing types filter with last 7 days
    print(f"\n{'=' * 70}")
    print(f"TEST 2: Financing types filter — SERIES_A + SEED (last 7 days)")
    print("=" * 70)
    companies = client.get_companies(
        financing_types=[{'type': 'SERIES_A'}, {'type': 'SEED'}],
        page_size=5,
        deal_start_date=last_7_days_start,
        deal_end_date=today_str,
    )
    print(f"  Found {len(companies)} companies")
    for company in companies:
        print_company(company)

    # Test 3: Industry + location filter with last 30 days
    print(f"\n{'=' * 70}")
    print(f"TEST 3: Industry + location filter — AI + San Francisco (last 30 days)")
    print("=" * 70)
    companies = client.get_companies(
        super_categories=['artificial-intelligence-e551'],
        locations=['san-francisco-california'],
        page_size=5,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"  Found {len(companies)} companies")
    for company in companies:
        print_company(company)

    # Test 4: Deal size range with last 30 days
    print(f"\n{'=' * 70}")
    print(f"TEST 4: Deal size range $10M–$50M (last 30 days)")
    print("=" * 70)
    companies = client.get_companies(
        deal_size_min=10_000_000,
        deal_size_max=50_000_000,
        page_size=5,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"  Found {len(companies)} companies")
    for company in companies:
        print_company(company)

    # Test 5: Total raised filter — companies that have raised $50M–$200M lifetime
    print(f"\n{'=' * 70}")
    print(f"TEST 5: Total raised $50M–$200M (last 30 days)")
    print("=" * 70)
    companies = client.get_companies(
        total_raised_min=50_000_000,
        total_raised_max=200_000_000,
        page_size=5,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"  Found {len(companies)} companies")
    for company in companies:
        print_company(company)

    # Test 6: Semantic search — AI-powered natural language query
    print(f"\n{'=' * 70}")
    print(f"TEST 6: Semantic search — 'AI healthcare diagnostics startups' (last 30 days)")
    print("=" * 70)
    companies = client.get_companies(
        search_query="AI healthcare diagnostics startups",
        page_size=5,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"  Found {len(companies)} companies")
    for company in companies:
        print_company(company)
        desc = company.get('short_description', '')
        if desc:
            print(f"      {desc}")

    # Save results for inspection
    if companies:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, 'sample_companies.json')
        with open(output_path, 'w') as f:
            json.dump(companies, f, indent=2)
        print(f"\n  Saved to {output_path}")


if __name__ == "__main__":
    test_all_parameters()
