# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python client library and examples for the Fundable venture capital deals API. Fetches, analyzes, and visualizes VC deal data including investor activity, deal discovery, and chart generation with investor logos.

API docs: https://fundable-api-docs.readme.io/reference/

## Setup & Commands

```bash
# Install (editable mode, from repo root)
python3 -m venv venv && source venv/bin/activate
pip install -e .

# Set API key
cp .env.example .env  # then edit .env with your FUNDABLE_API_KEY

# Run examples
python3 examples/get_recent_deals/get_recent_deals.py
python3 examples/get_alerts/get_alerts.py
python3 examples/company_viz/agent_analysis.py

# Dev tools (install with: pip install -e ".[dev]")
black src/ examples/
flake8 src/ examples/
pytest
```

## Architecture

**Layered design in `src/fundable/`:**

- **`client.py`** — `FundableClient` (API communication) and `DataExtractor` (data parsing/formatting). Client authenticates via `FUNDABLE_API_KEY` env var. Base URL defaults to `https://www.tryfundable.ai/api/v1`. `/deals`, `/companies`, `/investors` use POST with a nested JSON body (not GET query params). Default pagination: 100 items/page.
- **`visualization/charts.py`** — `BaseGraphGenerator` (logo caching/downloading, circular crop, plot styling), `InvestorBarChart`, `IndustryChart`. Logos cached in `.logo_cache/`. Output at 300 DPI.

**`examples/`** — Each subdirectory is a self-contained script with its own `output/` folder. Pattern: create client → call API with filters → extract/analyze → save JSON or PNG.

**`openapi_v2/`** — Current per-endpoint OpenAPI specs. The API uses strict parameter validation (unknown params → 422 error).

## Key API Conventions

- Date format: ISO 8601 (`2024-01-01` for deals/companies/investors; `2024-01-01T00:00:00.000Z` for alerts)
- Financing types are objects with `type` (required), `pre`, and `extension` (optional booleans):
  `[{"type": "SEED", "pre": true}, {"type": "SERIES_A"}]`
- Sort enums use snake_case: `most_recent_deal`, `matching_deals`, `recent_deals`, `total_deals`, `most_recent_raise`, etc.
- All monetary values (deal sizes, total raised, valuations) are in actual USD (not millions). Filter params (`size_min`, `size_max`, `total_raised_min`, `total_raised_max`) also expect actual USD. Date range max 10 years.
- Pagination: `page`/`page_size` (cap: 50,000 items)
- Deal response: contains `company_id` (UUID) and `investor_ids` (UUID array) — no inline company/investor objects. Use `get_company(id)` or `get_deal_investors(deal_id)` for full details.
- LinkedIn and Crunchbase params expect full URLs (e.g., `https://linkedin.com/company/stripe`, `https://crunchbase.com/organization/stripe`)
- `/company/search` and `/investor/search` accept `name=`, `domain=`, `linkedin=`, or `crunchbase=` (exactly one required)
- `/location/search` and `/industry/search` accept `name=` (required) and optional `type=` filter
- Company `latest_deal` uses `size_usd` / `size_native` (not `size`). Deal `valuation` uses `valuation_usd` / `valuation_native` (not `valuation_usd_millions`).
- `format_usd()` helper in `client.py` formats dollar amounts with commas (e.g., `$25,000,000`).
- Package imports: `from fundable import FundableClient, DataExtractor, format_usd`
- Visualization imports: `from fundable.visualization import InvestorBarChart`
