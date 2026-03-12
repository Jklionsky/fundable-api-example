# Fundable API Example

This repository contains a Python client for interacting with the Fundable API, along with examples demonstrating how to fetch and process deal data.

## Setup

1. **Create a Python virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # Or on Windows: venv\Scripts\activate
   ```

2. **Install the package:**
   ```bash
   pip install -e .
   ```
   This installs the `fundable` package in editable mode, allowing clean imports across all examples.

3. **Set your API key:**

   Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your Fundable API key
   ```

   Or set it directly in your shell:
   ```bash
   export FUNDABLE_API_KEY="your_api_key_here"
   ```

4. **Run examples:**

   **Get Recent Deals:**
   ```bash
   python3 examples/get_recent_deals/get_recent_deals.py
   ```

   **Top Investors Analysis:**
   ```bash
   python3 examples/top_investors/top_investors.py
   ```

   **Get Companies:**
   ```bash
   python3 examples/get_companies/get_companies.py
   python3 examples/get_companies/get_recent_raises.py
   ```

   **Get Investors:**
   ```bash
   python3 examples/get_investors/get_investors.py
   ```

   **Search (Companies, Investors, Industries, Locations):**
   ```bash
   python3 examples/search/search_examples.py
   ```

   See README files in each example directory for detailed documentation.

## Project Structure

- `src/fundable/` - Main Python package
  - `client.py` - FundableClient and DataExtractor classes
  - `analyzers/` - Analysis modules (InvestorAnalyzer, etc.)
- `examples/` - Example scripts demonstrating API usage
  - `get_recent_deals/` - Basic deal fetching examples
  - `top_investors/` - Advanced investor analysis
  - `get_companies/` - Company lookup and filtering examples
  - `get_investors/` - Investor lookup and filtering examples
  - `get_alerts/` - Alert fetching examples
  - `search/` - Search examples (companies, investors, industries, locations)
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

### Get Companies

```python
from fundable import FundableClient

client = FundableClient()

# Search companies with filters
companies = client.get_companies(
    financing_types=['SEED', 'SERIES_A'],
    locations=['san-francisco-california'],
    deal_start_date='2024-01-01',
    deal_end_date='2024-12-31',
    page_size=10
)

for company in companies:
    print(f"{company['name']} ({company.get('domain', 'N/A')})")

# Batch lookup by domain
companies = client.get_companies(
    domains=['openai.com', 'anthropic.com'],
    page_size=100
)

# Batch lookup by Crunchbase slug
companies = client.get_companies(
    crunchbases=['stripe', 'airbnb', 'notion-so'],
    page_size=100
)
```

### Get Investors

```python
from fundable import FundableClient

client = FundableClient()

# Find investors by portfolio filters
investors = client.get_investors(
    financing_types=['SEED'],
    locations=['san-francisco-california'],
    deal_start_date='2024-01-01',
    deal_end_date='2024-12-31',
    page_size=10,
    sort_by='Matching Deals'
)

for inv in investors:
    print(f"{inv['name']} — {inv.get('total_deal_count', 0)} deals")

# Batch lookup by investor domain
investors = client.get_investors(
    investor_domains=['sequoiacap.com', 'a16z.com'],
    page_size=100
)

# Batch lookup by investor Crunchbase slug
investors = client.get_investors(
    investor_crunchbases=['sequoia-capital', 'andreessen-horowitz'],
    page_size=100
)
```

### Search

```python
from fundable import FundableClient

client = FundableClient()

# Search companies by name
companies = client.search_companies(q="stripe")

# Search investors by name
investors = client.search_investors(q="sequoia")

# Search industries (optionally filter by type: INDUSTRY or SUPER_CATEGORY)
industries = client.search_industries(q="artificial intelligence")
super_cats = client.search_industries(q="fintech", type="INDUSTRY")

# Search locations (optionally filter by type: CITY, STATE, REGION, COUNTRY)
locations = client.search_locations(q="san francisco")
states = client.search_locations(q="california", type="STATE")
```

### Working with Alerts

The Fundable API allows you to fetch deals from your configured alerts. First, list your alert configurations to find your alert IDs:

```python
from fundable import FundableClient
from datetime import datetime, timedelta

client = FundableClient()

# List all your alert configurations
configs = client.get_alert_configurations()
for config in configs:
    print(f"{config['configuration_name']}: {config['configuration_id']}")

# Fetch deals from a specific alert
today = datetime.now()
week_ago = today - timedelta(days=7)

result = client.get_alerts(
    alert_ids=['your-alert-id'],
    start_date=week_ago.strftime("%Y-%m-%dT00:00:00.000Z"),
    end_date=today.strftime("%Y-%m-%dT23:59:59.999Z")
)

# Access alert deals
for alert in result['alerts']:
    print(f"{alert['alertName']}: {alert['totalDealCount']} deals")
    for deal in alert['deals']:
        print(f"  - {deal['company_name']}")
```

For complete examples including enriching alerts with company and investor data, see:
```bash
python3 examples/get_alerts/get_alerts.py
```

See README files in `examples/` directories for more detailed examples.

## API Documentation

For complete API documentation, including all available endpoints, parameters, and response formats, please reference the full documentation at:

**https://fundable-api-docs.readme.io/reference/**

## Requirements

- Python 3.6+
- Valid Fundable API key

See `requirements.txt` for Python package dependencies.