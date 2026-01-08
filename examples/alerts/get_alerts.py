#!/usr/bin/env python3
"""
Examples demonstrating the Alerts API with various use cases.

This script shows how to:
1. Fetch alerts from the last day using a single alert_id
2. Fetch multiple alert_ids and separate by alert name
3. Fetch alerts and enrich with additional company info
4. Fetch alerts and get investor info (limited to 5 deals)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

from dotenv import load_dotenv
load_dotenv()

from fundable import FundableClient

# Script-relative paths for output
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

# =============================================================================
# PLACEHOLDER ALERT IDS - Replace these with your actual alert IDs
# You can get your alert IDs from client.get_alert_configurations()
# =============================================================================
EXAMPLE_ALERT_ID_1 = "a2c9fa30-c479-4deb-856c-266622e5dcdf"
EXAMPLE_ALERT_ID_2 = "e1307820-9ed8-49c9-95df-16b81ce9fc15"


# =============================================================================
# DATA EXTRACTION HELPERS
# =============================================================================

def extract_alert_deal_summary(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key information from an alert deal.

    Alert deals have a simplified structure compared to regular deals.
    This helper extracts the most useful fields.
    """
    return {
        'deal_id': deal.get('id'),
        'company_id': deal.get('company_id'),
        'company_name': deal.get('company_name'),
        'round_type': deal.get('round_type'),
        'amount': f"${deal.get('total_round_raised')}M" if deal.get('total_round_raised') else 'Undisclosed',
        'date': deal.get('date'),
        'website': deal.get('company_website'),
        'linkedin': deal.get('company_linkedin'),
        'region': deal.get('region'),
        'reasoning': deal.get('reasoning'),  # AI-generated reasoning for why this matched
        'short_description': deal.get('deal_short_description'),
        'long_description': deal.get('deal_long_description'),
        'articles': deal.get('articles', []),
    }


def print_alert_summary(alerts: List[Dict[str, Any]], title: str = "Alert Results"):
    """Print a formatted summary of alert results."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

    if not alerts:
        print("No alerts found.")
        return

    for alert in alerts:
        print(f"\n{alert['alertName']}")
        print(f"   Frequency: {alert['alertFrequency']}")
        print(f"   Total Deals: {alert['totalDealCount']}")
        print("-" * 50)

        for i, deal in enumerate(alert['deals'][:5], 1):
            summary = extract_alert_deal_summary(deal)
            print(f"   {i}. {summary['company_name']} - {summary['amount']} ({summary['round_type']})")
            print(f"      Date: {summary['date']}")
            if summary['website']:
                print(f"      Website: {summary['website']}")
            if summary['reasoning']:
                reasoning = summary['reasoning'][:100] + "..." if len(summary['reasoning']) > 100 else summary['reasoning']
                print(f"      Why matched: {reasoning}")

        if alert['totalDealCount'] > 5:
            print(f"\n   ... and {alert['totalDealCount'] - 5} more deals")


# =============================================================================
# SIMPLE SELF-CONTAINED EXAMPLE (No FundableClient dependency)
# =============================================================================

def get_alerts_simple(alert_id: str):
    """
    Self-contained example - fetches alerts without using FundableClient.

    This function demonstrates the complete API call in one place,
    making it easy to understand and adapt. Copy this function to use
    the Alerts API in your own code.

    Args:
        alert_id: Your alert UUID (get from https://tryfundable.ai)

    Returns:
        List of alert objects with their deals
    """
    print("\n" + "="*80)
    print("SIMPLE ALERTS EXAMPLE (Self-Contained)")
    print("="*80)

    # -------------------------------------------------------------------------
    # STEP 1: Get API key from environment
    # -------------------------------------------------------------------------
    api_key = os.getenv("FUNDABLE_API_KEY")
    if not api_key:
        raise ValueError("Set FUNDABLE_API_KEY environment variable")

    # API base URL (can be overridden for local development)
    base_url = os.getenv("FUNDABLE_API_URL", "https://www.tryfundable.ai/api/v1")

    # -------------------------------------------------------------------------
    # STEP 2: Calculate date range (last 7 days)
    # -------------------------------------------------------------------------
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    start_date = week_ago.strftime("%Y-%m-%dT00:00:00.000Z")
    end_date = today.strftime("%Y-%m-%dT23:59:59.999Z")

    print(f"Fetching alerts from {week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")

    # -------------------------------------------------------------------------
    # STEP 3: Make the API request
    # -------------------------------------------------------------------------
    response = requests.get(
        f"{base_url}/alerts/",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        params={
            "alertIds": alert_id,
            "startDate": start_date,
            "endDate": end_date
        },
        timeout=30
    )

    # Check for errors
    response.raise_for_status()
    data = response.json()

    # -------------------------------------------------------------------------
    # STEP 4: Extract and display results
    # -------------------------------------------------------------------------
    if not data.get("success"):
        print("API request failed")
        return []

    alerts = data["data"]["alerts"]
    total_deals = data["data"].get("totalDealCount", 0)

    print(f"\nFound {len(alerts)} alert(s) with {total_deals} total deals")

    # Print summary using helper
    print_alert_summary(alerts, "Alert Results")

    # Extract key info from each deal
    all_extracted = []
    for alert in alerts:
        for deal in alert['deals']:
            extracted = extract_alert_deal_summary(deal)
            extracted['alert_name'] = alert['alertName']
            all_extracted.append(extracted)

    # Save to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'simple_alerts_output.json')
    with open(output_path, 'w') as f:
        json.dump(all_extracted, f, indent=2)
    print(f"\nSaved {len(all_extracted)} extracted deals to {output_path}")

    return alerts


# =============================================================================
# EXAMPLE 2: Multiple Alerts by Name
# =============================================================================

def example_2_multiple_alerts_by_name(alert_ids: List[str]):
    """
    Fetch multiple alert_ids and separate results by alert name.

    This shows how to query multiple alerts at once and organize
    the results by alert name.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Multiple Alerts by Name")
    print("="*80)

    client = FundableClient()

    # Calculate date range for last 7 days
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    start_date = week_ago.strftime("%Y-%m-%dT00:00:00.000Z")
    end_date = today.strftime("%Y-%m-%dT23:59:59.999Z")

    print(f"Fetching {len(alert_ids)} alerts from {week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")

    result = client.get_alerts(
        alert_ids=alert_ids,
        start_date=start_date,
        end_date=end_date
    )

    # Group deals by alert name
    alerts_by_name = {}
    for alert in result.get('alerts', []):
        name = alert['alertName']
        alerts_by_name[name] = {
            'alert_id': alert['alertId'],
            'frequency': alert['alertFrequency'],
            'total_deals': alert['totalDealCount'],
            'deals': [extract_alert_deal_summary(d) for d in alert['deals']]
        }

    # Print summary
    print(f"\nFound {len(alerts_by_name)} alerts:")
    for name, data in alerts_by_name.items():
        print(f"  - {name}: {data['total_deals']} deals ({data['frequency']})")

    # Save grouped results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'example_2_alerts_by_name.json')
    with open(output_path, 'w') as f:
        json.dump(alerts_by_name, f, indent=2)
    print(f"\nSaved grouped results to {output_path}")

    return alerts_by_name


# =============================================================================
# EXAMPLE 3: Alerts with Company Info
# =============================================================================

def example_3_alerts_with_company_info(alert_id: str, max_companies: int = 5):
    """
    Fetch alerts and enrich each deal with additional company details.

    Alert deals have simplified company info. This example shows how to
    fetch full company details for each deal.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Alerts with Company Info")
    print("="*80)

    client = FundableClient()

    # Calculate date range for last 7 days
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    start_date = week_ago.strftime("%Y-%m-%dT00:00:00.000Z")
    end_date = today.strftime("%Y-%m-%dT23:59:59.999Z")

    print(f"Fetching alert and enriching up to {max_companies} companies with full details...")

    result = client.get_alerts(
        alert_ids=[alert_id],
        start_date=start_date,
        end_date=end_date
    )

    enriched_deals = []
    companies_fetched = 0

    for alert in result.get('alerts', []):
        for deal in alert['deals']:
            if companies_fetched >= max_companies:
                break

            company_id = deal.get('company_id')
            if not company_id:
                continue

            # Get full company details
            print(f"  Fetching company: {deal.get('company_name', 'Unknown')}...")
            company_details = client.get_company(company_id, identifier_type='id')

            # Create enriched deal
            enriched = extract_alert_deal_summary(deal)
            enriched['company_details'] = company_details

            # Extract key company info
            if company_details:
                enriched['company_enriched'] = {
                    'full_description': company_details.get('full_description'),
                    'num_employees': company_details.get('num_employees'),
                    'total_raised': company_details.get('total_raised'),
                    'num_funding_rounds': company_details.get('num_funding_rounds'),
                    'industries': [ind.get('name') for ind in company_details.get('industries', [])],
                    'linkedin': company_details.get('linkedin'),
                    'twitter': company_details.get('twitter'),
                }

            enriched_deals.append(enriched)
            companies_fetched += 1

    # Print summary
    print(f"\nEnriched {len(enriched_deals)} deals with company info:")
    for deal in enriched_deals:
        print(f"\n  {deal['company_name']}:")
        print(f"    Deal: {deal['amount']} {deal['round_type']}")
        if deal.get('company_enriched'):
            ce = deal['company_enriched']
            print(f"    Employees: {ce.get('num_employees', 'N/A')}")
            print(f"    Total Raised: ${ce.get('total_raised', 'N/A')}M")
            if ce.get('industries'):
                print(f"    Industries: {', '.join(ce['industries'][:3])}")

    # Save enriched results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'example_3_enriched_with_company.json')
    with open(output_path, 'w') as f:
        json.dump(enriched_deals, f, indent=2)
    print(f"\nSaved enriched deals to {output_path}")

    return enriched_deals


# =============================================================================
# EXAMPLE 4: Alerts with Investor Info
# =============================================================================

def example_4_alerts_with_investor_info(alert_id: str, max_deals: int = 5):
    """
    Fetch alerts, then get investor info for each deal.

    This example:
    1. Fetches alert deals
    2. Uses the deals endpoint to get full deal info (with investor IDs)
    3. Fetches detailed investor info for each investor

    Limited to max_deals to avoid too many API calls.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Alerts with Investor Info")
    print("="*80)

    client = FundableClient()

    # Calculate date range for last 7 days
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    start_date = week_ago.strftime("%Y-%m-%dT00:00:00.000Z")
    end_date = today.strftime("%Y-%m-%dT23:59:59.999Z")

    print(f"Fetching alert and investor details for up to {max_deals} deals...")

    result = client.get_alerts(
        alert_ids=[alert_id],
        start_date=start_date,
        end_date=end_date
    )

    deals_with_investors = []
    deals_processed = 0

    for alert in result.get('alerts', []):
        for alert_deal in alert['deals']:
            if deals_processed >= max_deals:
                break

            print(f"\n  Processing: {alert_deal.get('company_name', 'Unknown')}")

            # Get full deal from deals endpoint to get investor details
            # Use company_id to filter deals
            company_id = alert_deal.get('company_id')
            if not company_id:
                continue

            # Fetch deals for this company to get investor info
            full_deals = client.get_deals(
                company_ids=[company_id],
                deal_start_date=week_ago.strftime("%Y-%m-%d"),
                deal_end_date=today.strftime("%Y-%m-%d"),
                page_size=5
            )

            if not full_deals:
                print(f"    No full deal data found")
                continue

            # Use the first matching deal
            full_deal = full_deals[0]
            deal_investors = full_deal.get('deal_investors', [])

            print(f"    Found {len(deal_investors)} investors")

            # Fetch detailed info for each investor
            enriched_investors = []
            for investor in deal_investors[:5]:  # Limit to 5 investors per deal
                investor_id = investor.get('id')
                investor_name = investor.get('name', 'Unknown')

                if investor_id:
                    print(f"      Fetching: {investor_name}...")
                    investor_details = client.get_investor(investor_id)

                    if investor_details:
                        enriched_investors.append({
                            'name': investor_name,
                            'id': investor_id,
                            'is_lead': investor.get('lead_investor', False),
                            'details': {
                                'description': investor_details.get('description'),
                                'website': investor_details.get('website'),
                                'total_investments': investor_details.get('total_investments'),
                                'lead_investments': investor_details.get('lead_investments'),
                                'top_industries': investor_details.get('industry_data', [])[:3],
                            }
                        })
                    else:
                        enriched_investors.append({
                            'name': investor_name,
                            'id': investor_id,
                            'is_lead': investor.get('lead_investor', False),
                            'details': None
                        })

            # Build enriched deal
            enriched_deal = extract_alert_deal_summary(alert_deal)
            enriched_deal['investors'] = enriched_investors
            deals_with_investors.append(enriched_deal)

            deals_processed += 1

    # Print summary
    print(f"\n{'='*60}")
    print("INVESTOR SUMMARY")
    print(f"{'='*60}")

    for deal in deals_with_investors:
        print(f"\n{deal['company_name']} - {deal['amount']} {deal['round_type']}")
        for inv in deal['investors']:
            lead = " (LEAD)" if inv.get('is_lead') else ""
            print(f"  - {inv['name']}{lead}")
            if inv.get('details'):
                d = inv['details']
                if d.get('total_investments'):
                    print(f"      Total Investments: {d['total_investments']}")
                if d.get('top_industries'):
                    industries = [i.get('industry_name', '') for i in d['top_industries']]
                    print(f"      Top Industries: {', '.join(industries)}")

    # Save results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'example_4_with_investor_info.json')
    with open(output_path, 'w') as f:
        json.dump(deals_with_investors, f, indent=2)
    print(f"\nSaved deals with investor info to {output_path}")

    return deals_with_investors


# =============================================================================
# BONUS: List Your Alert Configurations
# =============================================================================

def list_alert_configurations():
    """
    List all alert configurations for your account.

    Use this to find your alert IDs to use in the other examples.
    """
    print("\n" + "="*80)
    print("YOUR ALERT CONFIGURATIONS")
    print("="*80)

    client = FundableClient()
    configs = client.get_alert_configurations()

    if not configs:
        print("\nNo alert configurations found for your account.")
        print("Create alerts at https://tryfundable.ai to use these examples.")
        return []

    print(f"\nFound {len(configs)} alert configurations:\n")

    for config in configs:
        print(f"  Name: {config['configuration_name']}")
        print(f"  ID:   {config['configuration_id']}")
        print(f"  Frequency: {config['frequency']}")
        if config.get('description'):
            desc = config['description'][:80] + "..." if len(config.get('description', '')) > 80 else config.get('description', '')
            print(f"  Description: {desc}")
        print()

    # Save configurations
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'alert_configurations.json')
    with open(output_path, 'w') as f:
        json.dump(configs, f, indent=2)
    print(f"Saved configurations to {output_path}")

    return configs


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run the alert examples."""
    print("\nFundable Alerts API Examples")
    print("="*80)
    print("\nThese examples demonstrate various ways to fetch and enrich alert data.")
    print("\nBefore running the examples, you need to:")
    print("1. Set your FUNDABLE_API_KEY environment variable")
    print("2. Replace the placeholder alert IDs with your actual alert IDs")
    print("   (Run list_alert_configurations() first to find your IDs)\n")

    # First, list your alert configurations to find your alert IDs
    configs = list_alert_configurations()

    if not configs:
        print("\nNo alerts configured. Skipping examples.")
        return

    # # Use the first alert ID for examples
    first_alert_id = configs[0]['configuration_id']
    first_alert_name = configs[0]['configuration_name']

    print(f"\nUsing alert ID: {first_alert_id} for examples\n")
    print(f"  Name: {first_alert_name}")

    # Uncomment the examples you want to run:

    # Example 1: Single alert, last day
    get_alerts_simple(first_alert_id)

    # Example 2: Multiple alerts by name (requires 2+ alert IDs)
    # if len(configs) >= 2:
    #     alert_ids = [c['configuration_id'] for c in configs[:2]]
    #     example_2_multiple_alerts_by_name(alert_ids)

    # Example 3: Enrich with company info
    # example_3_alerts_with_company_info(first_alert_id, max_companies=3)

    # Example 4: Get investor details
    # example_4_alerts_with_investor_info(first_alert_id, max_deals=3)

    print("\n" + "="*80)
    print("Examples complete!")
    print("="*80)
    print(f"\nOutput saved to: {OUTPUT_DIR}")
    print("\nTo run other examples, edit this file and uncomment the example calls in main().\n")


if __name__ == "__main__":
    main()
