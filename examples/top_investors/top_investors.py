#!/usr/bin/env python3
"""
Example: Find top investors across various deal criteria.

This script demonstrates how to use the InvestorAnalyzer to find
the most active investors based on different filtering criteria.
"""

import os

from fundable import FundableClient, InvestorAnalyzer


def example_1_top_seed_investors():
    """
    Example 1: Top 25 investors in Seed rounds over last 2 months.
    
    This is the primary use case requested - find most active early-stage investors.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Top Seed/Pre-Seed Investors (Last 2 Months)")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    results = analyzer.analyze_top_investors(
        top_n=25,
        months_back=2,
        financing_types=['SEED'] 
    )
    
    analyzer.print_results(results, "Top 25 Seed Investors")
    analyzer.save_results(results, 'output/top_seed_investors.json')


def example_2_top_series_a_sf():
    """
    Example 2: Top Series A investors in San Francisco over last 6 months.
    Demonstrates filtering by round type + location.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Top Series A Investors in SF (Last 6 Months)")
    print("="*80)
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    results = analyzer.analyze_top_investors(
        top_n=15,
        months_back=6,
        financing_types=['SERIES_A'],
        locations=['san-francisco-california']
    )
    analyzer.print_results(results, "Top 15 Series A Investors (SF)")
    analyzer.save_results(results, 'output/top_series_a_sf.json')


def example_3_top_ai_investors():
    """
    Example 3: Top investors in AI startups over last 3 months.
    
    Demonstrates filtering by industry.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Top AI Investors (Last 3 Months)")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    results = analyzer.analyze_top_investors(
        top_n=20,
        months_back=3,
        super_categories=['artificial-intelligence-e551']
    )
    
    analyzer.print_results(results, "Top 20 AI Investors")
    analyzer.save_results(results, 'output/top_ai_investors.json')


def example_4_large_round_investors():
    """
    Example 4: Top investors in large rounds ($50M+) over last year.
    
    Demonstrates filtering by deal size.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Top Large Round Investors (Last Year)")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    results = analyzer.analyze_top_investors(
        top_n=20,
        months_back=12,
        deal_size_min=50
    )
    
    analyzer.print_results(results, "Top 20 Large Round Investors ($50M+)")
    analyzer.save_results(results, 'output/top_large_round_investors.json')


def example_5_combined_filters():
    """
    Example 5: Top investors with multiple combined filters.
    
    Demonstrates combining multiple filter types:
    - Round types: Seed + Series A
    - Industries: AI + Fintech
    - Location: California
    - Deal size: $1M - $25M
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Top Early-Stage Tech Investors in CA (Combined Filters)")
    print("="*80)
    
    client = FundableClient()
    analyzer = InvestorAnalyzer(client)
    
    results = analyzer.analyze_top_investors(
        top_n=15,
        months_back=6,
        financing_types=['SEED', 'SERIES_A'],
        super_categories=['artificial-intelligence-e551', 'fintech'],
        deal_size_min=1,
        deal_size_max=25
    )
    
    analyzer.print_results(results, "Top 15 Early-Stage Tech Investors (CA)")
    analyzer.save_results(results, 'output/top_early_stage_tech_ca.json')


def main():
    """Run examples."""
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    print("\n🚀 Fundable Investor Analysis Examples")
    print("="*80)
    print("\nThis script demonstrates various ways to analyze top investors")
    print("using different filtering criteria.\n")
    
    # Run the primary example
    # example_1_top_seed_investors()
    
    # Uncomment to run additional examples:
    # example_2_top_series_a_sf()
    example_3_top_ai_investors()
    # example_4_large_round_investors()
    # example_5_combined_filters()
    
    print("\n" + "="*80)
    print("✅ Analysis complete!")
    print("="*80)
    print("\n💡 To run other examples, edit top_seed_investors.py and uncomment")
    print("   the example functions in main().\n")


if __name__ == "__main__":
    main()
