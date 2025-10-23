# Fundable API Example

This repository contains a Python client for interacting with the Fundable API, along with examples demonstrating how to fetch and process deal data.

## Setup

1. **Install the package:**
   ```bash
   pip install -e .
   ```
   This installs the `fundable` package in editable mode, allowing clean imports across all examples.

2. **Set your API key:**
   ```bash
   export FUNDABLE_API_KEY="your_api_key_here"
   ```

3. **Run examples:**

   **Simple Example:**
   ```bash
   python3 examples/simple_example.py
   ```

   **Get Recent Deals:**
   ```bash
   python3 examples/get_recent_deals/get_recent_deals.py
   ```

   **Top Investors Analysis:**
   ```bash
   python3 examples/top_investors/top_seed_investors.py
   ```

   See README files in each example directory for detailed documentation.

## Project Structure

- `src/fundable/` - Main Python package
  - `client.py` - FundableClient and DataExtractor classes
  - `analyzers/` - Analysis modules (InvestorAnalyzer, etc.)
  - `visualization/` - Charting and visualization tools
- `examples/` - Example scripts demonstrating API usage
  - `simple_example.py` - Quick start example
  - `analyze_top_investors.py` - Investor analysis examples
  - `visualize_investors.py` - Visualization examples
  - `get_recent_deals/` - Basic deal fetching examples
  - `top_investors/` - Advanced investor analysis
  - `visualizations/` - Chart generation examples
- `openapi/` - OpenAPI specifications for all API endpoints
- `pyproject.toml` - Package configuration

## Quick Usage

### Get Recent Deals

```python
from fundable import FundableClient, DataExtractor

client = FundableClient()

# Fetch recent deals with filters
deals = client.get_deals(
    financing_types=['SEED', 'SERIES_A'],
    locations=['san-francisco-california'],
    deal_size_min=1,
    deal_size_max=10,
    deal_start_date='2024-01-01',
    deal_end_date='2024-12-31'
)

# Extract and display
extracted = [DataExtractor.extract_deal(deal) for deal in deals]
DataExtractor.print_deals(extracted, "Recent Deals")
```

### Find Top Investors by Any Criteria

```python
from fundable import FundableClient, InvestorAnalyzer

client = FundableClient()
analyzer = InvestorAnalyzer(client)

# Find top seed investors in last 2 months
results = analyzer.analyze_top_investors(
    top_n=25,
    months_back=2,
    financing_types=['SEED']
)

# Print and save results
analyzer.print_results(results)
analyzer.save_results(results, 'output/top_investors.json')
```

### Visualize Results

```python
from fundable import FundableClient, InvestorAnalyzer
from fundable.visualization import InvestorBarChart

client = FundableClient()
analyzer = InvestorAnalyzer(client)

results = analyzer.analyze_top_investors(
    top_n=15,
    months_back=2,
    financing_types=['SEED']
)

# Create chart with logos
chart = InvestorBarChart()
chart.plot_top_investors(
    results,
    title="Top Seed Investors",
    show_logos=True,
    output_path="output/chart.png"
)
```

See README files in `examples/` directories for more detailed examples.

## API Documentation

For complete API documentation, including all available endpoints, parameters, and response formats, please reference the full documentation at:

**https://fundable-api-docs.readme.io/reference/**

## Requirements

- Python 3.6+
- Valid Fundable API key

See `requirements.txt` for Python package dependencies.