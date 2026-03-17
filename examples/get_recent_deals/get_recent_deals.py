#!/usr/bin/env python3
"""
Example: Get recent deals with various filters.

This script demonstrates basic usage of the FundableClient to fetch
recent deals using different filter combinations.
"""

import json
import os
from datetime import datetime, timedelta

from fundable import FundableClient, DataExtractor, format_usd

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

def print_deal_summary(deal):
    """Print a single deal summary line."""
    amount = format_usd(deal.get('total_round_raised'))
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

    # # Test 1: Basic pagination with last 7 days
    # print("=" * 70)
    # print(f"TEST 1: Basic pagination (last 7 days: {last_7_days_start} to {today_str})")
    # print("=" * 70)
    # deals = client.get_deals(
    #     page=0,
    #     page_size=5,
    #     deal_start_date=last_7_days_start,
    #     deal_end_date=today_str
    # )
    # print(f"  Found {len(deals)} deals")
    # for deal in deals:
    #     print_deal_summary(deal)

    # # Test 2: Financing types filter (object format with type field)
    # print(f"\n{'=' * 70}")
    # print(f"TEST 2: Financing types filter — SERIES_A + SEED (last 7 days)")
    # print("=" * 70)
    # deals = client.get_deals(
    #     financing_types=[{'type': 'SERIES_A'}, {'type': 'SEED'}],
    #     page_size=5,
    #     deal_start_date=last_7_days_start,
    #     deal_end_date=today_str,
    # )
    # print(f"  Found {len(deals)} deals")
    # for deal in deals:
    #     print_deal_summary(deal)

    # # Test 3: Company filters — AI in San Francisco
    # # Enrich with company details to prove the location/industry filters work
    # print(f"\n{'=' * 70}")
    # print(f"TEST 3: Company filters — AI + San Francisco (last 30 days)")
    # print("=" * 70)
    # deals = client.get_deals(
    #     super_categories=['artificial-intelligence-e551'],
    #     locations=['san-francisco-california'],
    #     page_size=5,
    #     deal_start_date=last_30_days_start,
    #     deal_end_date=today_str,
    # )
    # print(f"  Found {len(deals)} deals\n")
    # for deal in deals:
    #     amount = format_usd(deal.get('total_round_raised'))
    #     print(f"    {deal.get('round_type', '?')} | {amount} | {deal.get('date', 'N/A')}")
    #     company = client.get_company(deal['company_id'])
    #     if company:
    #         location = company.get('location', {}) or {}
    #         loc_parts = []
    #         for key in ['city', 'state', 'country']:
    #             part = location.get(key)
    #             if isinstance(part, dict) and part.get('name'):
    #                 loc_parts.append(part['name'])
    #         loc_str = ', '.join(loc_parts)
    #         industries = [ind.get('name') for ind in company.get('industries', [])[:3]]
    #         super_cats = [sc.get('name') for sc in company.get('super_categories', [])[:3]]
    #         print(f"      Company: {company.get('name')} ({company.get('domain', 'N/A')})")
    #         print(f"      Location: {loc_str or 'N/A'}")
    #         print(f"      Industries: {', '.join(industries) if industries else 'N/A'}")
    #         print(f"      Super Categories: {', '.join(super_cats) if super_cats else 'N/A'}")
    #     else:
    #         print(f"      company_id: {deal.get('company_id')}")

    # # Test 4: Deal size range
    # print(f"\n{'=' * 70}")
    # print(f"TEST 4: Deal size range $100M–$150M (last 30 days)")
    # print("=" * 70)
    # deals = client.get_deals(
    #     deal_size_min=100_000_000,
    #     deal_size_max=150_000_000,
    #     page_size=5,
    #     deal_start_date=last_30_days_start,
    #     deal_end_date=today_str
    # )
    # print(f"  Found {len(deals)} deals")
    # for deal in deals:
    #     print_deal_summary(deal)

    # # Test 5: Pre-Seed (using pre modifier on financing type)
    # print(f"\n{'=' * 70}")
    # print(f"TEST 5: Pre-Seed deals (last 30 days)")
    # print("=" * 70)
    # deals = client.get_deals(
    #     financing_types=[{'type': 'SEED', 'pre': True}],
    #     page_size=5,
    #     deal_start_date=last_30_days_start,
    #     deal_end_date=today_str,
    # )
    # print(f"  Found {len(deals)} deals")
    # for deal in deals:
    #     amount = format_usd(deal.get('total_round_raised'))
    #     label = deal.get('round_type', '?')
    #     if deal.get('pre'):
    #         label = f"Pre-{label}"
    #     if deal.get('extension'):
    #         label = f"{label} (Extension)"
    #     print(f"    {deal.get('date', 'N/A')} | {label} | {amount}")

    # Test 6: Deal Investors — search for an investor, find their deals, show full syndicates
    print(f"\n{'=' * 70}")
    print(f"TEST 6: Search investor → filter deals → show deal syndicates")
    print("=" * 70)
    # Step 1: Search for investors by domain (may return multiple matches)
    investor_domain = "sequoiacap.com"
    print(f"  Searching for investors with domain: {investor_domain}")
    search_results = client.search_investors(domain=investor_domain)
    if search_results:
        print(f"  Found {len(search_results)} investor(s):")
        for inv in search_results:
            print(f"    - {inv.get('name')} (ID: {inv['id']})")

        # Step 2: Filter deals by ALL matching investor IDs
        investor_ids = [inv['id'] for inv in search_results]
        investor_deals = client.get_deals(
            investor_ids=investor_ids,
            page_size=3,
            sort_by='most_recent_deal',
        )
        print(f"\n  {len(investor_deals)} most recent deals across all Sequoia entities:\n")

        # Step 3: For each deal, get the full investor syndicate
        all_syndicates = []
        for deal in investor_deals:
            deal_id = deal['id']
            amount = format_usd(deal.get('total_round_raised'))
            round_type = deal.get('round_type', '?')
            date = deal.get('date', 'N/A')
            print(f"  {round_type} | {amount} | {date}")
            print(f"    Deal ID: {deal_id}")

            syndicate = client.get_deal_investors(deal_id)
            print(f"    Syndicate ({len(syndicate)} investors):")
            for inv in syndicate:
                lead = " [LEAD]" if inv.get('lead_investor') else ""
                angel = " [ANGEL]" if inv.get('angel_investor') else ""
                ftype = inv.get('financing_type') or ''
                domain = inv.get('domain') or 'N/A'
                print(f"      {inv.get('name', 'Unknown')}{lead}{angel} | {ftype} | {domain}")
            print()
            all_syndicates.append({
                'deal_id': deal_id,
                'round_type': round_type,
                'amount': deal.get('total_round_raised'),
                'date': date,
                'investors': syndicate,
            })

        # Save results
        if all_syndicates:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            inv_path = os.path.join(OUTPUT_DIR, 'sample_deal_investors.json')
            with open(inv_path, 'w') as f:
                json.dump(all_syndicates, f, indent=2)
            print(f"  Saved to {inv_path}")
    else:
        print(f"  No results found for '{investor_domain}'")



if __name__ == "__main__":
    test_all_parameters()