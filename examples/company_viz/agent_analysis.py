#!/usr/bin/env python3
"""
Example: Analyze and visualize companies with 'agent' in their description.

This script fetches all deals from the last 6 months and compares:
- Companies with 'agent' in their description
- Companies without 'agent' in their description

Creates a bar chart visualization showing the distribution.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from fundable import FundableClient

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    print("⚠️  matplotlib not installed. Install with: pip install matplotlib")
    exit(1)


def fetch_all_deals_last_6_months(client: FundableClient) -> List[Dict[str, Any]]:
    """
    Fetch all deals from the last 6 months using pagination.
    
    Args:
        client: FundableClient instance
        
    Returns:
        List of all deals from the last 6 months
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # 6 months = ~180 days
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"\n📅 Fetching deals from {start_date_str} to {end_date_str}")
    print("=" * 60)
    
    all_deals = []
    page = 0
    page_size = 100
    
    while True:
        print(f"📦 Fetching page {page + 1} (page_size={page_size})...", end=" ")
        
        deals = client.get_deals(
            deal_start_date=start_date_str,
            deal_end_date=end_date_str,
            page=page,
            page_size=page_size,
            sort_by='Most Recent'
        )
        
        if not deals:
            print("(no more deals)")
            break
        
        print(f"({len(deals)} deals)")
        all_deals.extend(deals)
        
        # If we got fewer deals than page_size, we've reached the end
        if len(deals) < page_size:
            break
        
        page += 1
    
    print(f"\n✅ Total deals fetched: {len(all_deals)}")
    return all_deals


def has_agent_in_description(deal: Dict[str, Any]) -> bool:
    """
    Check if a deal has 'agent' in its short or long description.
    
    Args:
        deal: Deal object from API
        
    Returns:
        True if 'agent' is found (case-insensitive), False otherwise
    """
    descriptions = deal.get('deal_descriptions', {}) or {}
    
    short_desc = descriptions.get('short_description', '') or ''
    long_desc = descriptions.get('long_description', '') or ''
    
    # Combine both descriptions and search case-insensitively
    combined_text = (short_desc + ' ' + long_desc).lower()
    
    return 'agent' in combined_text


def categorize_deals(deals: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
    """
    Categorize deals into those with 'agent' and those without.
    
    Args:
        deals: List of deal objects
        
    Returns:
        Tuple of (agent_deals, non_agent_deals)
    """
    agent_deals = []
    non_agent_deals = []
    
    print("\n🔍 Categorizing deals by 'agent' keyword...")
    
    for deal in deals:
        if has_agent_in_description(deal):
            agent_deals.append(deal)
        else:
            non_agent_deals.append(deal)
    
    print(f"✅ Found {len(agent_deals)} deals with 'agent'")
    print(f"✅ Found {len(non_agent_deals)} deals without 'agent'")
    
    return agent_deals, non_agent_deals


def print_sample_companies(deals: List[Dict[str, Any]], category: str, max_samples: int = 10):
    """
    Print sample companies from a category.
    
    Args:
        deals: List of deals
        category: Category name (e.g., "With 'agent'")
        max_samples: Maximum number of samples to display
    """
    print(f"\n📋 Sample Companies {category}:")
    print("=" * 60)
    
    for i, deal in enumerate(deals[:max_samples], 1):
        company_name = deal.get('company', {}).get('name', 'Unknown')
        round_type = deal.get('round_type', 'Unknown')
        amount = deal.get('total_round_raised')
        amount_str = f"${amount}M" if amount else 'Undisclosed'
        
        descriptions = deal.get('deal_descriptions', {}) or {}
        short_desc = descriptions.get('short_description', '') or ''
        long_desc = descriptions.get('long_description', '') or ''
        desc = long_desc or short_desc or 'No description'
        
        # Truncate description
        if len(desc) > 120:
            desc = desc[:120] + "..."
        
        print(f"\n{i}. {company_name}")
        print(f"   💰 {amount_str} ({round_type})")
        print(f"   📝 {desc}")


def create_visualization(agent_count: int, non_agent_count: int, output_path: str):
    """
    Create a bar chart comparing agent vs non-agent deals.
    
    Args:
        agent_count: Number of deals with 'agent'
        non_agent_count: Number of deals without 'agent'
        output_path: Path to save the chart
    """
    print(f"\n📊 Creating visualization...")
    
    # Calculate percentages
    total = agent_count + non_agent_count
    agent_pct = (agent_count / total * 100) if total > 0 else 0
    non_agent_pct = (non_agent_count / total * 100) if total > 0 else 0
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ["With 'agent'\nin description", "Without 'agent'\nin description"]
    counts = [agent_count, non_agent_count]
    colors = ['#4A90E2', '#E94B3C']
    
    bars = ax.bar(categories, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on top of bars
    for bar, count, pct in zip(bars, counts, [agent_pct, non_agent_pct]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{count:,}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Styling
    ax.set_ylabel('Number of Deals', fontsize=12, fontweight='bold')
    ax.set_title("Companies with 'Agent' in Description\n(Last Month)", 
                 fontsize=14, fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add total count at bottom
    fig.text(0.5, 0.02, f'Total Deals Analyzed: {total:,}', 
             ha='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Chart saved to: {output_path}")


def save_detailed_results(agent_deals: List[Dict], non_agent_deals: List[Dict], output_dir: str):
    """
    Save detailed results to JSON files for further analysis.
    
    Args:
        agent_deals: Deals with 'agent' in description
        non_agent_deals: Deals without 'agent' in description
        output_dir: Directory to save JSON files
    """
    print(f"\n💾 Saving detailed results...")
    
    # Extract key info for readability
    def extract_key_info(deal):
        return {
            'company_name': deal.get('company', {}).get('name', 'Unknown'),
            'round_type': deal.get('round_type', 'Unknown'),
            'deal_date': deal.get('date', ''),
            'amount': deal.get('total_round_raised'),
            'description': (deal.get('deal_descriptions', {}) or {}).get('long_description') or 
                          (deal.get('deal_descriptions', {}) or {}).get('short_description', ''),
            'domain': deal.get('company', {}).get('domain', ''),
        }
    
    agent_summary = [extract_key_info(d) for d in agent_deals]
    non_agent_summary = [extract_key_info(d) for d in non_agent_deals]
    
    # Save summaries
    with open(f"{output_dir}/agent_deals_summary.json", 'w') as f:
        json.dump(agent_summary, f, indent=2)
    
    with open(f"{output_dir}/non_agent_deals_summary.json", 'w') as f:
        json.dump(non_agent_summary, f, indent=2)
    
    print(f"✅ Saved agent deals to: {output_dir}/agent_deals_summary.json")
    print(f"✅ Saved non-agent deals to: {output_dir}/non_agent_deals_summary.json")


def main():
    """Main execution function."""
    
    print("\n🚀 Agent Companies Analysis")
    print("=" * 60)
    print("Analyzing deals from the last 6 months to compare companies")
    print("with 'agent' in their description vs. those without.\n")
    
    # Initialize client
    client = FundableClient()
    
    # Fetch all deals from last 6 months
    all_deals = fetch_all_deals_last_6_months(client)
    
    if not all_deals:
        print("⚠️  No deals found. Check your API key or date range.")
        return
    
    # Categorize deals
    agent_deals, non_agent_deals = categorize_deals(all_deals)
    
    # Print statistics
    total = len(all_deals)
    agent_pct = (len(agent_deals) / total * 100) if total > 0 else 0
    non_agent_pct = (len(non_agent_deals) / total * 100) if total > 0 else 0
    
    print(f"\n📊 Summary Statistics:")
    print("=" * 60)
    print(f"Total Deals:          {total:,}")
    print(f"With 'agent':         {len(agent_deals):,} ({agent_pct:.1f}%)")
    print(f"Without 'agent':      {len(non_agent_deals):,} ({non_agent_pct:.1f}%)")
    
    # Print sample companies
    if agent_deals:
        print_sample_companies(agent_deals, "With 'agent'", max_samples=5)
    
    if non_agent_deals:
        print_sample_companies(non_agent_deals, "Without 'agent'", max_samples=5)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create visualization
    chart_path = os.path.join(output_dir, 'agent_companies_comparison.png')
    create_visualization(len(agent_deals), len(non_agent_deals), chart_path)
    
    # Save detailed results
    save_detailed_results(agent_deals, non_agent_deals, output_dir)
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")
    print("=" * 60)
    print(f"📊 Chart:      {chart_path}")
    print(f"📁 Data:       {output_dir}/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
