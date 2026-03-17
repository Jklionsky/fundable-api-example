#!/usr/bin/env python3
"""
Example: Get a company's full funding history using /company/deals.

This script demonstrates how to look up all deals for a specific company
by domain, LinkedIn URL, or Crunchbase URL, with pagination support.
"""

import json
import os

from fundable import FundableClient, format_usd

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')


def print_deal(deal):
    """Print a single deal with round type modifiers."""
    amount = format_usd(deal.get('total_round_raised'))
    label = deal.get('round_type', 'Unknown')
    if deal.get('pre'):
        label = f"Pre-{label}"
    if deal.get('extension'):
        label = f"{label} (Extension)"
    date = (deal.get('date') or 'N/A')[:10]
    num_investors = len(deal.get('investor_ids', []))
    print(f"    {date} | {label} | {amount} | {num_investors} investors")


def main():
    client = FundableClient()

    # --- Test 1: Funding history by domain ---
    print("=" * 70)
    print("TEST 1: Funding history by domain (databricks.com)")
    print("=" * 70)
    result = client.get_company_deals(domain="databricks.com", page_size=25)
    deals = result['deals']
    meta = result['meta']
    print(f"  Found {meta.get('total_count', len(deals))} total deals (page {meta.get('page', 0)})\n")
    for deal in deals:
        print_deal(deal)

    # --- Test 2: Funding history by LinkedIn URL ---
    print(f"\n{'=' * 70}")
    print("TEST 2: Funding history by LinkedIn URL (Anduril)")
    print("=" * 70)
    result = client.get_company_deals(linkedin="linkedin.com/company/andurilindustries/", page_size=25)
    deals = result['deals']
    meta = result['meta']
    print(f"  Found {meta.get('total_count', len(deals))} total deals (page {meta.get('page', 0)})\n")
    for deal in deals:
        print_deal(deal)

    # --- Test 3: Funding history by Crunchbase URL ---
    print(f"\n{'=' * 70}")
    print("TEST 3: Full funding history by Crunchbase URL (Lovable)")
    print("=" * 70)
    result = client.get_company_deals(crunchbase="https://www.crunchbase.com/organization/lovable-803a", page_size=25)
    deals = result['deals']
    meta = result['meta']
    print(f"  Found {meta.get('total_count', len(deals))} total deals (page {meta.get('page', 0)})\n")
    for deal in deals:
        print_deal(deal)

    # --- Test 4: Pagination ---
    print(f"\n{'=' * 70}")
    print("TEST 4: Pagination — page 0 vs page 1 (databricks.com, page_size=3)")
    print("=" * 70)
    for pg in [0, 1]:
        result = client.get_company_deals(domain="databricks.com", page=pg, page_size=3)
        deals = result['deals']
        meta = result['meta']
        print(f"\n  Page {pg} ({len(deals)} deals, {meta.get('total_count', '?')} total):")
        for deal in deals:
            print_deal(deal)

    # Save a sample for inspection
    result = client.get_company_deals(domain="databricks.com", page_size=10)
    if result['deals']:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, 'company_deals.json')
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n  Saved full history to {output_path}")


if __name__ == "__main__":
    main()
