#!/usr/bin/env python3
"""
Example: Search for companies, investors, industries, and locations.

This script demonstrates usage of the FundableClient search endpoints:
- /company/search — fuzzy search companies by name/domain
- /investor/search — fuzzy search investors by name/domain
- /industry/search — fuzzy search industries and super categories
- /location/search — fuzzy search locations (cities, states, countries, regions)
"""

import json
import os

from fundable import FundableClient

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')


def main():
    client = FundableClient()

    all_results = {}

    # --- Test 1: Company search ---
    print("=" * 60)
    print("TEST 1: Search companies")
    print("=" * 60)
    companies = client.search_companies(q="stripe")
    print(f"Found {len(companies)} companies matching 'stripe'\n")
    for c in companies[:5]:
        score = c.get('relevance_score', 'N/A')
        print(f"  {c.get('name')} ({c.get('domain', 'N/A')}) — relevance: {score}")
    all_results['company_search'] = companies

    # --- Test 2: Investor search ---
    print(f"\n{'=' * 60}")
    print("TEST 2: Search investors")
    print("=" * 60)
    investors = client.search_investors(q="sequoia")
    print(f"Found {len(investors)} investors matching 'sequoia'\n")
    for inv in investors[:5]:
        score = inv.get('relevance_score', 'N/A')
        print(f"  {inv.get('name')} ({inv.get('domain', 'N/A')}) — relevance: {score}")
    all_results['investor_search'] = investors

    # --- Test 3: Industry search (all types) ---
    print(f"\n{'=' * 60}")
    print("TEST 3: Search industries (all types)")
    print("=" * 60)
    industries = client.search_industries(q="artificial intelligence")
    print(f"Found {len(industries)} results matching 'artificial intelligence'\n")
    for ind in industries[:10]:
        print(f"  {ind.get('name')} — {ind.get('industry_type')} (permalink: {ind.get('permalink')})")
    all_results['industry_search_all'] = industries

    # --- Test 4: Industry search (filtered to INDUSTRY only) ---
    print(f"\n{'=' * 60}")
    print("TEST 4: Search industries (INDUSTRY type only)")
    print("=" * 60)
    industries_only = client.search_industries(q="fintech", type="INDUSTRY")
    print(f"Found {len(industries_only)} industries matching 'fintech'\n")
    for ind in industries_only[:10]:
        print(f"  {ind.get('name')} (permalink: {ind.get('permalink')})")
    all_results['industry_search_filtered'] = industries_only

    # --- Test 5: Location search ---
    print(f"\n{'=' * 60}")
    print("TEST 5: Search locations")
    print("=" * 60)
    locations = client.search_locations(q="san francisco")
    print(f"Found {len(locations)} locations matching 'san francisco'\n")
    for loc in locations[:10]:
        print(f"  {loc.get('name')} — {loc.get('location_type')} (permalink: {loc.get('permalink')})")
    all_results['location_search_all'] = locations

    # --- Test 6: Location search (filtered to STATE) ---
    print(f"\n{'=' * 60}")
    print("TEST 6: Search locations (STATE type only)")
    print("=" * 60)
    states = client.search_locations(q="california", type="STATE")
    print(f"Found {len(states)} states matching 'california'\n")
    for loc in states[:10]:
        print(f"  {loc.get('name')} (permalink: {loc.get('permalink')})")
    all_results['location_search_filtered'] = states

    # --- Save results ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'search_results.json')
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved all search results to {output_path}")


if __name__ == "__main__":
    main()
