#!/usr/bin/env python3
"""
Simple example demonstrating the clean new import structure.

This shows how easy it is to use the fundable package now that
it's properly structured.
"""

from fundable import FundableClient, InvestorAnalyzer
from fundable.visualization import InvestorBarChart


def main():
    """Simple example of analyzing and visualizing top investors."""
    
    print("🚀 Fundable API - Simple Example")
    print("="*60)
    
    # Initialize client
    print("\n1️⃣  Initializing client...")
    client = FundableClient()
    
    # Create analyzer
    print("2️⃣  Creating analyzer...")
    analyzer = InvestorAnalyzer(client)
    
    # Analyze top seed investors
    print("3️⃣  Fetching top 10 seed investors...")
    results = analyzer.analyze_top_investors(
        top_n=10,
        months_back=2,
        financing_types=['SEED']
    )
    
    if not results:
        print("⚠️  No results found. Check your API key.")
        return
    
    # Print results
    print("\n4️⃣  Analysis Results:")
    analyzer.print_results(results, "Top 10 Seed Investors")
    
    # Create visualization
    print("\n5️⃣  Creating visualization with logos...")
    import os
    os.makedirs('output/charts', exist_ok=True)
    
    chart = InvestorBarChart()
    chart.plot_top_investors(
        results,
        title="Top 10 Seed Investors",
        show_logos=True,
        output_path="output/charts/simple_example.png"
    )
    
    print("\n✅ Complete! Chart saved to: output/charts/simple_example.png")
    print("\n" + "="*60)
    print("💡 Notice how clean the imports are:")
    print("   from fundable import FundableClient, InvestorAnalyzer")
    print("   from fundable.visualization import InvestorBarChart")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
