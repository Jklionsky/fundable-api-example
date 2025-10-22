#!/usr/bin/env python3
"""
Generalized investor analysis module for Fundable API.
"""

import json
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fundableClient import FundableClient


class InvestorAnalyzer:
    """Analyze investor activity across deals with flexible filtering."""

    def __init__(self, client: FundableClient):
        """Initialize with a FundableClient instance."""
        self.client = client

    def analyze_top_investors(
        self,
        top_n: int = 25,
        months_back: int = 2,
        **deal_filters
    ) -> List[Dict[str, Any]]:
        """
        Find top N most active investors based on any deal filter criteria.
        
        This is a generalized method that accepts any combination of deal filters
        and returns ranked investors based on their deal participation.
        
        Args:
            top_n: Number of top investors to return (default: 25)
            months_back: Number of months to look back for deals (default: 2)
            **deal_filters: Any valid deal filter parameters:
                - financing_types: List[str] - e.g., ['SEED', 'SERIES_A']
                - locations: List[str] - e.g., ['san-francisco', 'new-york']
                - industries: List[str] - e.g., ['artificial-intelligence']
                - super_categories: List[str] - e.g., ['technology']
                - deal_size_min: float - Minimum deal size in $M
                - deal_size_max: float - Maximum deal size in $M
                - employee_count: List[str] - e.g., ['1-10', '11-50']
                - ipo_status: List[str] - e.g., ['private', 'public']
                - Any other parameters supported by get_deals()
                
        Returns:
            List of dicts containing investor details and deal counts, sorted by activity
        """
        print(f"\n🔍 Analyzing top {top_n} investors over last {months_back} months...")
        print(f"📊 Filters applied: {deal_filters if deal_filters else 'None (all deals)'}")
        
        # Set date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        deal_filters['deal_start_date'] = start_date.strftime("%Y-%m-%d")
        deal_filters['deal_end_date'] = end_date.strftime("%Y-%m-%d")
        
        # Fetch all matching deals with pagination
        all_deals = self._fetch_all_deals(**deal_filters)
        
        if not all_deals:
            print("⚠️  No deals found matching the criteria")
            return []
        
        print(f"✓ Found {len(all_deals)} deals matching criteria")
        
        # Count investor occurrences
        investor_counts = self._count_investors(all_deals)
        
        if not investor_counts:
            print("⚠️  No investors found in the deals")
            return []
        
        print(f"✓ Found {len(investor_counts)} unique investors")
        
        # Get top N investors
        top_investor_ids = [inv_id for inv_id, _ in investor_counts.most_common(top_n)]
        
        # Fetch detailed information for top investors
        results = self._fetch_investor_details(
            top_investor_ids,
            investor_counts,
            all_deals
        )
        
        print(f"✓ Retrieved details for {len(results)} investors\n")
        
        return results

    def _fetch_all_deals(self, **deal_filters) -> List[Dict[str, Any]]:
        """Fetch all deals across multiple pages."""
        all_deals = []
        page = 0
        page_size = 100
        
        print("📥 Fetching deals...", end="", flush=True)
        
        while True:
            deals = self.client.get_deals(
                page=page,
                page_size=page_size,
                **deal_filters
            )
            
            if not deals:
                break
                
            all_deals.extend(deals)
            print(f" {len(all_deals)}", end="", flush=True)
            
            # Stop if we got fewer results than page size (last page)
            if len(deals) < page_size:
                break
                
            page += 1
        
        print()  # New line
        return all_deals

    def _count_investors(self, deals: List[Dict[str, Any]]) -> Counter:
        """Count investor occurrences across deals."""
        investor_counts = Counter()
        
        for deal in deals:
            deal_investors = deal.get('deal_investors', [])
            for investor in deal_investors:
                investor_id = investor.get('id')
                if investor_id:
                    investor_counts[investor_id] += 1
        
        return investor_counts

    def _fetch_investor_details(
        self,
        investor_ids: List[str],
        investor_counts: Counter,
        deals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fetch detailed information for each investor."""
        results = []
        
        print(f"🔍 Fetching details for top investors...")
        
        for i, investor_id in enumerate(investor_ids, 1):
            print(f"  [{i}/{len(investor_ids)}] ", end="", flush=True)
            
            # Get investor details from API
            investor_details = self.client.get_investor(investor_id)
            
            if not investor_details:
                print(f"⚠️  Could not fetch details for investor {investor_id}")
                continue
            
            # Extract key information
            deal_count = investor_counts[investor_id]
            
            result = {
                'rank': i,
                'investor_id': investor_id,
                'name': investor_details.get('name', 'Unknown'),
                'domain': investor_details.get('domain'),
                'website': investor_details.get('website'),
                'deal_count': deal_count,
                'location': self._format_location(investor_details),
                'description': investor_details.get('description') or investor_details.get('about'),
                'investment_stage': investor_details.get('investment_stage'),
                'total_investments': investor_details.get('total_investments'),
                'lead_investments': investor_details.get('lead_investments'),
                'top_industries': investor_details.get('industry_data', [])[:5],
                'linkedin': investor_details.get('linkedin'),
                'crunchbase': investor_details.get('crunchbase'),
            }
            
            # Get sample deals this investor participated in
            result['sample_deals'] = self._get_investor_sample_deals(
                investor_id, deals, max_samples=3
            )
            
            results.append(result)
            print(f"✓ {result['name']}")
        
        return results

    def _format_location(self, investor_details: Dict[str, Any]) -> str:
        """Format investor location from various fields."""
        region = investor_details.get('region')
        country = investor_details.get('country_code')
        
        parts = [p for p in [region, country] if p]
        return ', '.join(parts) if parts else 'Unknown'

    def _get_investor_sample_deals(
        self,
        investor_id: str,
        deals: List[Dict[str, Any]],
        max_samples: int = 3
    ) -> List[Dict[str, Any]]:
        """Get sample deals where this investor participated."""
        investor_deals = []
        
        for deal in deals:
            deal_investors = deal.get('deal_investors', [])
            
            # Check if investor participated in this deal
            investor_in_deal = any(
                inv.get('id') == investor_id for inv in deal_investors
            )
            
            if investor_in_deal:
                company = deal.get('company', {}) or {}
                investor_deals.append({
                    'company_name': company.get('name', 'Unknown'),
                    'round_type': deal.get('round_type'),
                    'date': deal.get('date'),
                    'amount': deal.get('total_round_raised')
                })
                
                if len(investor_deals) >= max_samples:
                    break
        
        return investor_deals

    def print_results(self, results: List[Dict[str, Any]], title: str = "Top Investors"):
        """Print investor analysis results in a readable format."""
        if not results:
            print("No results to display")
            return
        
        print(f"\n{'='*80}")
        print(f"🏆 {title}")
        print(f"{'='*80}\n")
        
        for investor in results:
            print(f"{investor['rank']}. {investor['name']}")
            print(f"   📊 Deals in Period: {investor['deal_count']}")
            
            if investor.get('location'):
                print(f"   📍 Location: {investor['location']}")
            
            if investor.get('domain'):
                print(f"   🌐 Domain: {investor['domain']}")
            
            if investor.get('investment_stage'):
                print(f"   🎯 Stage Focus: {investor['investment_stage']}")
            
            if investor.get('total_investments'):
                print(f"   💼 Total Investments: {investor['total_investments']} "
                      f"({investor.get('lead_investments', 0)} as lead)")
            
            if investor.get('description'):
                desc = investor['description']
                if len(desc) > 120:
                    desc = desc[:120] + "..."
                print(f"   📝 {desc}")
            
            if investor.get('top_industries'):
                industries = ', '.join([
                    f"{ind.get('industry_name')} ({ind.get('count')})"
                    for ind in investor['top_industries'][:3]
                ])
                print(f"   🏭 Top Industries: {industries}")
            
            if investor.get('sample_deals'):
                print(f"   🎪 Sample Deals:")
                for deal in investor['sample_deals']:
                    amount = f"${deal['amount']}M" if deal['amount'] else "Undisclosed"
                    print(f"      • {deal['company_name']} - {deal['round_type']} ({amount})")
            
            print()

    def save_results(self, results: List[Dict[str, Any]], filepath: str):
        """Save results to JSON file."""
        output = {
            'generated_at': datetime.now().isoformat(),
            'total_investors': len(results),
            'investors': results
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Results saved to: {filepath}")
