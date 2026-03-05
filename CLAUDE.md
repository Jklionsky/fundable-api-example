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
python3 examples/top_investors/top_investors.py
python3 examples/get_alerts/get_alerts.py
python3 examples/company_viz/agent_analysis.py

# Dev tools (install with: pip install -e ".[dev]")
black src/ examples/
flake8 src/ examples/
pytest
```

## Architecture

**Layered design in `src/fundable/`:**

- **`client.py`** — `FundableClient` (API communication) and `DataExtractor` (data parsing/formatting). Client authenticates via `FUNDABLE_API_KEY` env var. Base URL defaults to `https://www.tryfundable.ai/api/v1`. List params are auto-converted to comma-separated strings. Default pagination: 100 items/page.
- **`analyzers/investor.py`** — `InvestorAnalyzer` wraps the client to find top investors across deals with flexible filtering. Handles pagination internally.
- **`visualization/charts.py`** — `BaseGraphGenerator` (logo caching/downloading, circular crop, plot styling), `InvestorBarChart`, `IndustryChart`. Logos cached in `.logo_cache/`. Output at 300 DPI.

**`examples/`** — Each subdirectory is a self-contained script with its own `output/` folder. Pattern: create client → call API with filters → extract/analyze → save JSON or PNG.

**`openapi/`** — Per-endpoint OpenAPI specs (deals, investors, companies, alerts, people, other) plus industry filter docs. The API uses strict parameter validation (unknown params → 422 error).

## Key API Conventions

- Date format: ISO 8601 (`2024-01-01` or `2024-01-01T00:00:00.000Z` for alerts)
- Financing types are enums: `SEED`, `SERIES_A`, `SERIES_B`, etc.
- Deal sizes in millions USD; max $100B, date range max 10 years
- Pagination cap: 50,000 items
- Package imports: `from fundable import FundableClient, DataExtractor, InvestorAnalyzer`
- Visualization imports: `from fundable.visualization import InvestorBarChart`
