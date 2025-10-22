# Fundable API Examples

This directory contains example scripts demonstrating various use cases for the Fundable API.

## Investor Analysis

### `investor_analyzer.py`

A generalized module for analyzing investor activity across deals with flexible filtering.

**Key Features:**
- Find top N most active investors based on any deal criteria
- Automatic pagination handling for large datasets
- Detailed investor information retrieval
- Sample deal extraction for each investor
- Pretty printing and JSON export

**Main Function:**
```python
InvestorAnalyzer.analyze_top_investors(
    top_n=25,           # Number of top investors to return
    months_back=2,      # Time period to analyze
    **deal_filters      # Any valid deal filter parameters
)
```

**Supported Deal Filters:**
- `financing_types` - e.g., `['SEED', 'SERIES_A', 'SERIES_B']`
- `locations` - e.g., `['san-francisco-california', 'new-york']`
- `industries` - e.g., `['artificial-intelligence', 'fintech']`
- `super_categories` - e.g., `['artificial-intelligence-e551']`
- `deal_size_min` / `deal_size_max` - Deal size range in $M
- `employee_count` - e.g., `['1-10', '11-50']`
- `ipo_status` - e.g., `['private', 'public']`
- Any other parameters supported by `FundableClient.get_deals()`

### `top_seed_investors.py`

Main example script with 5 different use cases demonstrating the flexibility of the analyzer.

**Examples Included:**

1. **Top Seed Investors** - Most active seed-stage investors in last 2 months
2. **Top Series A Investors (SF)** - Series A investors in San Francisco
3. **Top AI Investors** - Investors focused on AI startups
4. **Large Round Investors** - Investors in $50M+ rounds
5. **Combined Filters** - Multiple filters combined (round type + industry + location + size)

## Running the Examples

### Quick Start

```bash
# Run the primary example (Top Seed Investors)
cd examples
python3 top_seed_investors.py
```

### Run Specific Examples

Edit `top_seed_investors.py` and uncomment the example functions you want to run:

```python
def main():
    example_1_top_seed_investors()      # Default - always runs
    # example_2_top_series_a_sf()       # Uncomment to run
    # example_3_top_ai_investors()      # Uncomment to run
    # example_4_large_round_investors() # Uncomment to run
    # example_5_combined_filters()      # Uncomment to run
```

### Using the Analyzer in Your Own Code

```python
from fundableClient import FundableClient
from investor_analyzer import InvestorAnalyzer

# Initialize
client = FundableClient()
analyzer = InvestorAnalyzer(client)

# Find top investors with any filter combination
results = analyzer.analyze_top_investors(
    top_n=25,
    months_back=3,
    financing_types=['SEED', 'SERIES_A'],
    locations=['san-francisco-california'],
    deal_size_min=1,
    deal_size_max=10
)

# Display results
analyzer.print_results(results)

# Save to JSON
analyzer.save_results(results, 'output/my_analysis.json')
```

## Output Format

Results are saved as JSON files in the `output/` directory with the following structure:

```json
{
  "generated_at": "2024-01-15T10:30:00",
  "total_investors": 25,
  "investors": [
    {
      "rank": 1,
      "investor_id": "uuid-here",
      "name": "Acme Ventures",
      "domain": "acmeventures.com",
      "website": "https://acmeventures.com",
      "deal_count": 15,
      "location": "San Francisco, United States",
      "description": "Early-stage VC focused on AI...",
      "investment_stage": "Series A",
      "total_investments": 247,
      "lead_investments": 89,
      "top_industries": [...],
      "sample_deals": [...]
    },
    ...
  ]
}
```

## Creating Custom Analyses

The `InvestorAnalyzer` is designed to be flexible. You can create custom analyses by:

1. **Combining multiple filters:**
   ```python
   results = analyzer.analyze_top_investors(
       top_n=20,
       months_back=6,
       financing_types=['SERIES_B', 'SERIES_C'],
       super_categories=['healthcare', 'biotech'],
       locations=['boston', 'cambridge-massachusetts'],
       deal_size_min=20
   )
   ```

2. **Analyzing different time periods:**
   ```python
   # Last quarter
   q4_results = analyzer.analyze_top_investors(top_n=15, months_back=3)
   
   # Last year
   yearly_results = analyzer.analyze_top_investors(top_n=50, months_back=12)
   ```

3. **Focusing on specific deal characteristics:**
   ```python
   # Large late-stage rounds in tech hubs
   results = analyzer.analyze_top_investors(
       top_n=10,
       months_back=12,
       financing_types=['SERIES_D', 'SERIES_E'],
       locations=['san-francisco', 'new-york', 'london'],
       deal_size_min=100
   )
   ```

## Common Use Case Examples

### By Round Type
```python
# Seed investors only
results = analyzer.analyze_top_investors(
    top_n=25, months_back=2, financing_types=['SEED']
)

# Multiple rounds
results = analyzer.analyze_top_investors(
    top_n=30, months_back=3, financing_types=['SEED', 'SERIES_A', 'SERIES_B']
)
```

### By Location
```python
# San Francisco
results = analyzer.analyze_top_investors(
    top_n=15, months_back=6, locations=['san-francisco-california']
)

# State level
results = analyzer.analyze_top_investors(
    top_n=25, months_back=12, locations=['california']
)
```

### By Industry
```python
# AI/ML investors
results = analyzer.analyze_top_investors(
    top_n=20, months_back=3, super_categories=['artificial-intelligence-e551']
)
```

### By Deal Size
```python
# Large rounds ($50M+)
results = analyzer.analyze_top_investors(
    top_n=15, months_back=12, deal_size_min=50
)

# Specific range ($1M - $10M)
results = analyzer.analyze_top_investors(
    top_n=25, months_back=6, deal_size_min=1, deal_size_max=10
)
```

### Combined Filters
```python
# Early-stage AI investors in Bay Area
results = analyzer.analyze_top_investors(
    top_n=20, months_back=6,
    financing_types=['SEED', 'SERIES_A'],
    super_categories=['artificial-intelligence-e551'],
    locations=['san-francisco', 'palo-alto'],
    deal_size_min=1, deal_size_max=15
)
```

## Available Filter Parameters

All parameters from `FundableClient.get_deals()` are supported:

### Date Filters
- `months_back` - Number of months to look back (sets date range automatically)
- `deal_start_date` / `deal_end_date` - Custom date range (YYYY-MM-DD)
- `company_founded_start` / `company_founded_end` - Company founding date filters

### Company Filters
- `company_ids` - List of company UUIDs
- `industries` - Industry permalinks
- `super_categories` - Super category permalinks
- `locations` - Location permalinks (cities, states, countries)
- `employee_count` - Employee ranges: `['1-10', '11-50', '51-100', '101-250', '251-500', '501-1000', '1001-5000', '5001-10000', '10001+']`
- `ipo_status` - `['public', 'private']`

### Deal Filters
- `financing_types` - Financing types: `['SEED', 'SERIES_A', 'SERIES_B', 'SERIES_C', ...]`
- `deal_size_min` / `deal_size_max` - Deal size range (USD $M)

### Investor Filters
- `investor_ids` - List of investor UUIDs

## Result Data Structure

Each investor result contains:
```python
{
    'rank': 1,
    'investor_id': 'uuid',
    'name': 'Investor Name',
    'domain': 'domain.com',
    'website': 'https://domain.com',
    'deal_count': 15,  # Deals in the filtered period
    'location': 'San Francisco, United States',
    'description': 'Description...',
    'investment_stage': 'Series A',
    'total_investments': 247,  # All-time
    'lead_investments': 89,
    'top_industries': [{'industry_name': 'AI', 'count': 45}, ...],
    'sample_deals': [{'company_name': '...', 'round_type': '...', ...}, ...],
    'linkedin': 'https://...',
    'crunchbase': 'https://...'
}
```

## Tips

- **Performance:** The analyzer automatically handles pagination to fetch all matching deals
- **Rate Limits:** Be mindful of API rate limits when analyzing large datasets
- **Date Ranges:** Larger time periods provide more data but take longer to process
- **Filter Combinations:** All deal filter parameters can be combined for precise targeting
- **Output Directory:** Results are saved to `output/` directory (created automatically)
- **Find Valid Values:** Check OpenAPI specs in `../../openapi/` for valid enum values

## Need Help?

- Check the main README for API setup and authentication
- Review the OpenAPI specifications in `../../openapi/` directory
- See API documentation: https://fundable-api-docs.readme.io/reference/
