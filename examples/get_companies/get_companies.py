#!/usr/bin/env python3
"""
Example: Batch lookup companies by domain using a CSV file.

This script demonstrates how to use the /companies endpoint's `domains`
and `linkedins` filters to batch-lookup companies from a CSV test set.
"""

import csv
import json
import os

from fundable import FundableClient

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
CSV_PATH = os.path.join(REPO_ROOT, 'test_sets', 'San_Francisco_2026-03-05.csv')


def load_csv(path):
    """Load company domains and LinkedIn slugs from CSV."""
    domains = []
    linkedin_slugs = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            domain = row.get('Website', '').strip()
            linkedin = row.get('LinkedIn', '').strip()
            if domain:
                domains.append(domain)
            if linkedin:
                # Extract slug from full URL
                slug = linkedin.rstrip('/').split('/')[-1]
                linkedin_slugs.append(slug)
    return domains, linkedin_slugs


def main():
    client = FundableClient()

    # Load test set
    print(f"Loading CSV from {CSV_PATH}...")
    domains, linkedin_slugs = load_csv(CSV_PATH)
    print(f"Found {len(domains)} domains and {len(linkedin_slugs)} LinkedIn slugs\n")

    # --- Test 1: Batch lookup by domain ---
    print("=" * 60)
    print(f"BATCH LOOKUP BY DOMAIN ({len(domains)} domains)")
    print("=" * 60)

    companies = client.get_companies(
        domains=domains,
        page_size=100,
    )
    print(f"\nMatched {len(companies)} / {len(domains)} domains\n")

    for company in companies:
        latest = company.get('latest_deal') or {}
        deal_size = f"${latest.get('size')}M" if latest.get('size') else 'Undisclosed'
        deal_type = latest.get('type', 'N/A')
        deal_date = (latest.get('date') or '')[:10]
        total = f"${company.get('total_raised')}M" if company.get('total_raised') else 'N/A'

        print(f"  {company['name']} ({company.get('domain', 'N/A')})")
        print(f"    Total Raised: {total} | Latest: {deal_type} {deal_size} ({deal_date})")

    # Save results
    if companies:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, 'sf_companies.json')
        with open(output_path, 'w') as f:
            json.dump(companies, f, indent=2)
        print(f"\nSaved {len(companies)} companies to {output_path}")

    # --- Test 2: Batch lookup by LinkedIn slug (first 10) ---
    subset = linkedin_slugs[:10]
    print(f"\n{'=' * 60}")
    print(f"BATCH LOOKUP BY LINKEDIN ({len(subset)} slugs)")
    print("=" * 60)

    companies_li = client.get_companies(
        linkedins=subset,
        page_size=100,
    )
    print(f"\nMatched {len(companies_li)} / {len(subset)} LinkedIn slugs\n")

    for company in companies_li:
        print(f"  {company['name']} ({company.get('domain', 'N/A')})")

    # --- Test 3: Batch lookup by Crunchbase slug ---
    cb_slugs = ['stripe', 'airbnb', 'notion-so']
    print(f"\n{'=' * 60}")
    print(f"BATCH LOOKUP BY CRUNCHBASE ({len(cb_slugs)} slugs)")
    print("=" * 60)

    companies_cb = client.get_companies(
        crunchbases=cb_slugs,
        page_size=100,
    )
    print(f"\nMatched {len(companies_cb)} / {len(cb_slugs)} Crunchbase slugs\n")

    for company in companies_cb:
        print(f"  {company['name']} ({company.get('domain', 'N/A')})")


if __name__ == "__main__":
    main()
