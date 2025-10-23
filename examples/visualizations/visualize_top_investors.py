#!/usr/bin/env python3
"""
Example: Visualize top investors with logos.

This script demonstrates how to use the graph generator to create
visual charts of investor analysis data with integrated logos.
"""

import sys
import os

# Add repo root to path
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, repo_root)

# Add parent directories for imports
examples_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, examples_dir)
sys.path.insert(0, os.path.join(examples_dir, 'top_investors'))

from fundableClient import FundableClient
from top_investors.investor_analyzer import InvestorAnalyzer
from utils.graph_generator import InvestorBarChart, IndustryChart


def example_1_seed_investors_with_logos():
    """
    Example 1: Top Seed investors with logos displayed.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Top Seed Investors with Logos")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    # Analyze top seed investors
    results = analyzer.analyze_top_investors(
        top_n=15,
        months_back=2,
        financing_types=['SEED']
    )
    
    if not results:
        print("⚠️  No results to visualize")
        return
    
    # Print text results
    analyzer.print_results(results, "Top 15 Seed Investors")
    
    # Create output directory
    os.makedirs('output/charts', exist_ok=True)
    
    # Create visualization with logos
    chart = InvestorBarChart()
    chart.plot_top_investors(
        results,
        title="Top Seed Investors (Last 2 Months)",
        metric="deal_count",
        show_logos=True,
        output_path="output/charts/top_seed_investors_with_logos.png"
    )
    
    print("\n✅ Chart generated successfully!")


def example_2_series_a_investors():
    """
    Example 2: Top Series A investors without logos (simpler view).
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Top Series A Investors")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    results = analyzer.analyze_top_investors(
        top_n=12,
        months_back=3,
        financing_types=['SERIES_A']
    )
    
    if not results:
        print("⚠️  No results to visualize")
        return
    
    os.makedirs('output/charts', exist_ok=True)
    
    # Create visualization without logos
    chart = InvestorBarChart()
    chart.plot_top_investors(
        results,
        title="Top Series A Investors (Last 3 Months)",
        metric="deal_count",
        show_logos=False,
        output_path="output/charts/top_series_a_investors.png",
        color="#A23B72"
    )
    
    print("\n✅ Chart generated successfully!")


def example_3_investor_comparison():
    """
    Example 3: Compare multiple metrics for top investors.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Multi-Metric Investor Comparison")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    results = analyzer.analyze_top_investors(
        top_n=10,
        months_back=3,
        financing_types=['SEED', 'SERIES_A']
    )
    
    if not results:
        print("⚠️  No results to visualize")
        return
    
    os.makedirs('output/charts', exist_ok=True)
    
    # Create comparison chart
    chart = InvestorBarChart()
    chart.plot_investor_comparison(
        results,
        metrics=['deal_count', 'total_investments', 'lead_investments'],
        metric_labels=['Recent Deals', 'Total Investments', 'Lead Investments'],
        title="Investor Activity Comparison",
        max_display=10,
        output_path="output/charts/investor_comparison.png"
    )
    
    print("\n✅ Comparison chart generated successfully!")


def example_4_industry_distribution():
    """
    Example 4: Visualize industry distribution from top investor.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Industry Distribution for Top Investor")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    results = analyzer.analyze_top_investors(
        top_n=1,
        months_back=6
    )
    
    if not results or not results[0].get('top_industries'):
        print("⚠️  No industry data to visualize")
        return
    
    top_investor = results[0]
    print(f"\n📊 Analyzing industries for: {top_investor['name']}")
    
    os.makedirs('output/charts', exist_ok=True)
    
    # Create industry distribution chart
    chart = IndustryChart()
    chart.plot_industry_distribution(
        top_investor['top_industries'],
        title=f"Industry Focus: {top_investor['name']}",
        max_display=10,
        output_path="output/charts/top_investor_industries.png"
    )
    
    print("\n✅ Industry chart generated successfully!")


def example_5_ai_investors_with_logos():
    """
    Example 5: Top AI investors with logos.
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Top AI Investors with Logos")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    results = analyzer.analyze_top_investors(
        top_n=12,
        months_back=3,
        super_categories=['artificial-intelligence-e551']
    )
    
    if not results:
        print("⚠️  No results to visualize")
        return
    
    os.makedirs('output/charts', exist_ok=True)
    
    # Create visualization with logos
    chart = InvestorBarChart()
    chart.plot_top_investors(
        results,
        title="Top AI Investors (Last 3 Months)",
        metric="deal_count",
        show_logos=True,
        output_path="output/charts/top_ai_investors_with_logos.png",
        color="#06A77D"
    )
    
    print("\n✅ AI investor chart generated successfully!")


def main():
    """Run visualization examples."""
    
    print("\n🎨 Fundable Investor Visualization Examples")
    print("="*80)
    print("\nThis script demonstrates how to create visual charts from")
    print("investor analysis data, including logo integration.\n")
    
    # Run examples - uncomment the ones you want to run
    example_1_seed_investors_with_logos()
    # example_2_series_a_investors()
    # example_3_investor_comparison()
    # example_4_industry_distribution()
    # example_5_ai_investors_with_logos()
    
    print("\n" + "="*80)
    print("✅ Visualization complete!")
    print("="*80)
    print("\n💡 Charts saved to: output/charts/")
    print("💡 To run other examples, edit visualize_top_investors.py")
    print("   and uncomment the example functions in main().\n")


if __name__ == "__main__":
    main()
