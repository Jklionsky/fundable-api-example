# Get Recent Deals Example

Basic example demonstrating how to fetch recent deals using the Fundable API with various filter combinations.

## Overview

This example shows simple usage of the `FundableClient` to:
- Fetch deals from recent time periods
- Apply filters (financing types, locations, industries, deal sizes)
- Extract and display deal information
- Save results to JSON files

## Running the Example

```bash
python3 examples/get_recent_deals/get_recent_deals.py
```

## What It Does

The script demonstrates 4 different query patterns:

1. **Basic Pagination** - Fetch recent deals with pagination
2. **Financing Types Filter** - Filter by round types (Series A, Seed, etc.)
3. **Company Filters** - Filter by location and industry
4. **Deal Size Range** - Filter by deal amount ranges

Results are displayed in the console and saved to `output/sample_deals.json`.

## Example Output

```
Testing updated get_deals function with all OpenAPI parameters...
Using date range: 2024-10-15 to 2024-10-22
✓ Basic pagination (last 7 days): 5 deals
✓ Financing types filter (last 7 days): 3 deals
✓ Company filters (last 30 days): 3 deals
✓ Deal size range (last 30 days): 3 deals

============================================================
SAMPLE DEALS OUTPUT:
============================================================

🚀 Recent Large Deals (2 deals)
============================================================

1. Acme Corporation
   💰 $125M (SERIES_C)
   📅 2024-10-20T00:00:00Z
   🌍 San Francisco, California, United States
   🌐 acme.com
   📝 AI-powered platform for...
   💼 Sequoia Capital, Andreessen Horowitz (+3 more)
   🎯 Lead: Sequoia Capital
```

## Key Functions Used

### FundableClient.get_deals()

Fetches deals with optional filters:

```python
from fundable import FundableClient

client = FundableClient()

# Basic query
deals = client.get_deals(
    page=0,
    page_size=10,
    deal_start_date="2024-10-01",
    deal_end_date="2024-10-22"
)

# With filters
deals = client.get_deals(
    financing_types=['SEED', 'SERIES_A'],
    locations=['san-francisco-california'],
    deal_size_min=1,
    deal_size_max=10
)
```

### DataExtractor.extract_deal()

Extracts key information from raw deal data:

```python
from fundable import DataExtractor

for deal in deals:
    extracted = DataExtractor.extract_deal(deal)
    print(f"{extracted['company_name']}: {extracted['deal_amount']}")
```

### DataExtractor.print_deals()

Pretty prints deal information to console:

```python
extracted_deals = [DataExtractor.extract_deal(deal) for deal in deals]
DataExtractor.print_deals(extracted_deals, "My Deals")
```

## Common Filters

### By Date Range
```python
deals = client.get_deals(
    deal_start_date="2024-01-01",
    deal_end_date="2024-12-31"
)
```

### By Financing Type
```python
deals = client.get_deals(
    financing_types=['SEED', 'SERIES_A', 'SERIES_B']
)
```

### By Location
```python
deals = client.get_deals(
    locations=['san-francisco-california', 'new-york']
)
```

### By Industry
```python
deals = client.get_deals(
    super_categories=['artificial-intelligence-e551'],
    industries=['fintech', 'healthcare']
)
```

### By Deal Size
```python
deals = client.get_deals(
    deal_size_min=10,   # $10M minimum
    deal_size_max=100   # $100M maximum
)
```

### Combined Filters
```python
deals = client.get_deals(
    financing_types=['SERIES_A'],
    locations=['california'],
    super_categories=['artificial-intelligence-e551'],
    deal_size_min=5,
    deal_size_max=50,
    deal_start_date="2024-01-01",
    deal_end_date="2024-12-31"
)
```

## Output Files

- `output/sample_deals.json` - Full deal objects in JSON format for inspection

## Next Steps

For more advanced analysis (finding top investors, aggregating data, etc.), see:
- `../top_investors/` - Investor analysis examples

## API Documentation

For complete parameter reference, see:
- OpenAPI specs: `../../openapi/openapi-deals.yaml`
- Full docs: https://fundable-api-docs.readme.io/reference/
