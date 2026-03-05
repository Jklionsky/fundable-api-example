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

from fundable import FundableClient

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')


def test_all_parameters():
    """Test the get_companies function with various parameter combinations."""
    client = FundableClient()

    print("Testing get_companies with various filter combinations...")

    # Calculate dynamic date ranges
    today = datetime.now()
    last_7_days_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    last_30_days_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    print(f"Using date range: {last_7_days_start} to {today_str}")

    # Test 1: Basic pagination with last 7 days
    companies = client.get_companies(
        page=0,
        page_size=5,
        deal_start_date=last_7_days_start,
        deal_end_date=today_str
    )
    print(f"\u2713 Basic pagination (last 7 days): {len(companies)} companies")

    # Test 2: Financing types filter with last 7 days
    companies = client.get_companies(
        financing_types=['SERIES_A', 'SEED'],
        page_size=3,
        deal_start_date=last_7_days_start,
        deal_end_date=today_str,
    )
    print(f"\u2713 Financing types filter (last 7 days): {len(companies)} companies")

    # Test 3: Industry + location filter with last 30 days
    companies = client.get_companies(
        super_categories=['artificial-intelligence-e551'],
        locations=['san-francisco-california'],
        page_size=3,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"\u2713 Industry + location filter (last 30 days): {len(companies)} companies")

    # Test 4: Deal size range with last 30 days
    companies = client.get_companies(
        deal_size_min=10,
        deal_size_max=50,
        page_size=3,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"\u2713 Deal size range $10M-$50M (last 30 days): {len(companies)} companies")

    # Test 5: Semantic search — AI-powered natural language query
    companies = client.get_companies(
        search_query="AI healthcare diagnostics startups",
        page_size=3,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"\u2713 Semantic search (last 30 days): {len(companies)} companies")
    for company in companies:
        name = company.get('name', 'Unknown')
        domain = company.get('domain', 'N/A')
        similarity = company.get('similarity')
        desc = company.get('short_description', 'No description')
        latest = company.get('latest_deal', {})
        deal_info = ""
        if latest:
            deal_info = f" | {latest.get('type', 'N/A')} ${latest.get('size') or 'Undisclosed'}M"
        sim_str = f" (similarity: {similarity:.2f})" if similarity else ""
        print(f"  {name} ({domain}){sim_str}{deal_info}")
        print(f"    {desc}")

    # Test 6: Print a sample company
    if companies:
        print("\n" + "="*60)
        print("SAMPLE COMPANY OUTPUT:")
        print("="*60)
        print(companies[0])

    # Test 7: Save full company objects for inspection
    if companies:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, 'sample_companies.json')
        print(f"\n\U0001f4c1 Saving {len(companies)} full company objects to '{output_path}'...")
        with open(output_path, 'w') as f:
            json.dump(companies, f, indent=2)
        print("\u2713 Full company objects saved - inspect the complete API response structure")


if __name__ == "__main__":
    test_all_parameters()
