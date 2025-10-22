#!/usr/bin/env python3
"""
Example: Get recent deals with various filters.

This script demonstrates basic usage of the FundableClient to fetch
recent deals using different filter combinations.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add repo root directory to path to import fundableClient
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, repo_root)

from fundableClient import FundableClient, DataExtractor

def test_all_parameters():
    """Test the updated get_deals function with various parameter combinations."""
    # You can pass your API key directly here if needed
    # client = FundableClient(api_key="your_api_key_here")
    client = FundableClient()

    print("Testing updated get_deals function with all OpenAPI parameters...")

    # Calculate dynamic date ranges
    today = datetime.now()
    last_7_days_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    last_30_days_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    print(f"Using date range: {last_7_days_start} to {today_str}")

    # Test 1: Basic pagination with last 7 days
    deals = client.get_deals(
        page=0,
        page_size=5,
        deal_start_date=last_7_days_start,
        deal_end_date=today_str
    )
    print(f"✓ Basic pagination (last 7 days): {len(deals)} deals")

    # Test 2: Financing types filter with last 7 days
    deals = client.get_deals(
        financing_types=['SERIES_A', 'SEED'],
        page_size=3,
        deal_start_date=last_7_days_start,
        deal_end_date=today_str,
    )
    print(f"✓ Financing types filter (last 7 days): {len(deals)} deals")

    # Test 3: Company filters with last 30 days for broader results
    deals = client.get_deals(
        super_categories=['artificial-intelligence-e551'],
        locations=['san-francisco-california'],
        page_size=3,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str,
    )
    print(f"✓ Company filters (last 30 days): {len(deals)} deals")

    # Test 4: Deal size range with last 30 days
    deals = client.get_deals(
        deal_size_min=100,
        deal_size_max=150,
        page_size=3,
        deal_start_date=last_30_days_start,
        deal_end_date=today_str
    )
    print(f"✓ Deal size range (last 30 days): {len(deals)} deals")

    # Test 5: Print deals using existing functionality
    if deals:
        print("\n" + "="*60)
        print("SAMPLE DEALS OUTPUT:")
        print("="*60)

        # Extract and print deals using existing DataExtractor
        extracted_deals = [DataExtractor.extract_deal(deal) for deal in deals[:2]]
        DataExtractor.print_deals(extracted_deals, "Recent Large Deals")

    # Test 6: Save full deal objects for inspection
    if deals:
        print(f"\n📁 Saving {len(deals)} full deal objects to 'sample_deals.json'...")
        with open('output/sample_deals.json', 'w') as f:
            json.dump(deals, f, indent=2)
        print("✓ Full deal objects saved - users can inspect the complete API response structure")

if __name__ == "__main__":
    test_all_parameters()