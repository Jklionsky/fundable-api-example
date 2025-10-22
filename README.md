# Fundable API Example

This repository contains a Python client for interacting with the Fundable API, along with examples demonstrating how to fetch and process deal data.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your API key:**
   ```bash
   export FUNDABLE_API_KEY="your_api_key_here"
   ```

3. **Run examples:**
   
   **Get Recent Deals (Basic):**
   ```bash
   cd examples/get_recent_deals
   python3 get_recent_deals.py
   ```
   
   **Top Investors Analysis (Advanced):**
   ```bash
   cd examples/top_investors
   python3 top_seed_investors.py
   ```
   
   See README files in each example directory for detailed documentation.

## Files

- `fundableClient.py` - Main client library with `FundableClient` and `DataExtractor` classes
- `examples/` - Example use cases and analysis tools
  - `get_recent_deals/` - Basic example: Fetch and display recent deals
    - `get_recent_deals.py` - Script with multiple filter examples
    - `README.md` - Documentation and usage guide
  - `top_investors/` - Advanced example: Investor activity analysis
    - `investor_analyzer.py` - Generalized investor analysis module
    - `top_seed_investors.py` - Script with 5 investor analysis examples
    - `README.md` - Comprehensive documentation
- `openapi/` - OpenAPI specifications for all API endpoints

## Quick Usage

### Get Recent Deals

```python
from fundableClient import FundableClient, DataExtractor

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
from fundableClient import FundableClient
from examples.top_investors.investor_analyzer import InvestorAnalyzer

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

### Combine Any Filters

```python
# Top AI investors in California with mid-size rounds
results = analyzer.analyze_top_investors(
    top_n=15,
    months_back=6,
    financing_types=['SERIES_A', 'SERIES_B'],
    super_categories=['artificial-intelligence-e551'],
    locations=['california'],
    deal_size_min=10,
    deal_size_max=50
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