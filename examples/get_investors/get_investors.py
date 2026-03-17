#!/usr/bin/env python3
"""
Example: List and filter investors using various criteria.

This script demonstrates usage of the FundableClient to fetch investors
using investor filters (who the investor is) and portfolio filters
(who they've invested in).
"""

import json
import os
from datetime import datetime, timedelta

from fundable import FundableClient

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')


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
        sort_by='matching_deals',
    )
    print(f"Found {len(investors)} investors (sorted by matching deals)\n")
    for inv in investors:
        print_investor(inv)

    # --- Test 2: Financing type filter ---
    print(f"\n{'=' * 60}")
    print("TEST 2: Investors in SEED deals (last 30 days)")
    print("=" * 60)
    investors = client.get_investors(
        financing_types=[{'type': 'SEED'}],
        page_size=5,
        deal_start_date=last_30_days,
        deal_end_date=today_str,
        sort_by='matching_deals',
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
        sort_by='matching_deals',
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

    # --- Test 5: Portfolio filter by company IDs ---
    # Look up company IDs by domain first, then filter investors by those IDs
    print(f"\n{'=' * 60}")
    print("TEST 5: Find investors in specific companies (by company_ids)")
    print("=" * 60)
    lookup_domains = ['stripe.com', 'openai.com', 'anthropic.com']
    company_ids = []
    for domain in lookup_domains:
        results = client.search_companies(domain=domain)
        if results:
            company_ids.append(results[0]['id'])
            print(f"  Resolved {domain} -> {results[0]['id']}")

    investors = client.get_investors(
        company_ids=company_ids,
        page_size=10,
        sort_by='matching_deals',
    )
    print(f"\n  Found {len(investors)} investors across {len(company_ids)} portfolio companies\n")
    for inv in investors:
        print_investor(inv)

    # --- Test 6: Batch lookup by investor Crunchbase slug ---
    print(f"\n{'=' * 60}")
    print("TEST 6: Batch lookup by investor Crunchbase URL")
    print("=" * 60)
    vc_cb_urls = [
        'https://crunchbase.com/organization/sequoia-capital',
        'https://crunchbase.com/organization/andreessen-horowitz',
        'https://crunchbase.com/organization/accel',
        'https://crunchbase.com/organization/khosla-ventures',
    ]
    investors = client.get_investors(
        investor_crunchbases=vc_cb_urls,
        page_size=100,
    )
    print(f"Matched {len(investors)} / {len(vc_cb_urls)} investor Crunchbase URLs\n")
    for inv in investors:
        print_investor(inv)

    # --- Test 7: Portfolio filter with deal filters ---
    print(f"\n{'=' * 60}")
    print("TEST 7: Investors in SERIES_A deals for AI companies (last 30 days)")
    print("=" * 60)
    investors = client.get_investors(
        super_categories=['artificial-intelligence-e551'],
        financing_types=[{'type': 'SERIES_A'}],
        deal_start_date=last_30_days,
        deal_end_date=today_str,
        page_size=5,
        sort_by='matching_deals',
    )
    print(f"Found {len(investors)} investors\n")
    for inv in investors:
        print_investor(inv)

    # --- Test 8: Most active recent investors with their last deals ---
    print(f"\n{'=' * 60}")
    print("TEST 8: Most active investors (by recent deals) + last 3 deals")
    print("=" * 60)
    investors = client.get_investors(
        page_size=5,
        sort_by='recent_deals',
    )
    print(f"Found {len(investors)} investors (sorted by recent deal count)\n")
    for inv in investors:
        print_investor(inv)
        for deal in inv.get('last_three_deals', []):
            amount = f"${deal['deal_size']}M" if deal.get('deal_size') else "Undisclosed"
            print(f"    -> {deal.get('company_name', '?')} — {deal.get('round_type', '?')} ({amount})")

    # --- Test 9: Portfolio filters → matching_deal_ids → fetch full deals ---
    print(f"\n{'=' * 60}")
    print("TEST 9: Top AI seed investors + fetch their matching deals by ID")
    print("=" * 60)
    investors = client.get_investors(
        super_categories=['artificial-intelligence-e551'],
        financing_types=[{'type': 'SEED'}],
        deal_start_date=last_30_days,
        deal_end_date=today_str,
        page_size=3,
        sort_by='matching_deals',
    )
    print(f"Found {len(investors)} investors\n")
    for inv in investors:
        filtered = inv.get('filtered_deal_count', 0)
        deal_ids = inv.get('matching_deal_ids') or []
        print(f"  {inv['name']} — {filtered} matching deals")

        # Fetch full deal details using matching_deal_ids
        for deal_id in deal_ids:
            deal = client.get_deal(deal_id)
            if deal:
                amount = f"${deal.get('total_round_raised')}M" if deal.get('total_round_raised') else "Undisclosed"
                # company_id is available inline; call get_company(deal['company_id']) for full name
                print(f"    -> company_id:{deal.get('company_id', '?')} — {deal.get('round_type', '?')} ({amount})")

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
