---
name: fundable
description: Venture capital data — companies, investors, deals, funding rounds. Search and filter companies by industry, location, funding stage, and deal size. Look up investors, their portfolios, and deal history. AI-powered semantic company search.
---

# Fundable — VC Data API

Access venture capital data: companies, investors, and deals. Filter by industry, location, funding stage, deal size, and more. Includes AI-powered semantic search.

**Base URL:** `https://www.tryfundable.ai/api/v1`
**Auth:** `Authorization: Bearer $FUNDABLE_API_KEY`

## Capabilities

- **Company Search & Filter**: Find companies by funding stage, industry, location, size, and AI semantic search
- **Company Lookup**: Get detailed company info by domain, LinkedIn, or Crunchbase URL
- **Company Deal History**: Get all funding rounds for a company
- **Investor Search & Filter**: Find investors by portfolio, location, deal activity
- **Investor Lookup**: Get investor details by domain, LinkedIn, or Crunchbase URL
- **Investor Deal History**: Get all deals an investor participated in
- **Deal Search & Filter**: Find deals by financing type, size, date, company, and investor
- **Deal Details**: Get deal info including investors, valuations, and articles
- **Location & Industry Search**: Look up permalinks for filtering

---

## Companies

### List & Filter Companies (POST)

Search and filter companies with pagination, sorting, and optional AI semantic search.

```bash
curl -s -X POST https://www.tryfundable.ai/api/v1/companies/ \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company": {
      "industries": ["artificial-intelligence"],
      "ipo_status": ["private"]
    },
    "latest_deal": {
      "financing_types": [{"type": "SERIES_A"}],
      "date_start": "2025-01-01"
    },
    "sort_by": "most_recent_raise",
    "page_size": 25
  }'
```

**Filter sections:**
- **`identifiers`** — Lookup by `ids`, `domains`, `linkedin_urls`, `crunchbase_urls` (max 100 each)
- **`company`** — `search_query` (AI semantic search), `min_relevance` (0-1), `industries`, `super_categories`, `locations`, `employee_count`, `total_raised_min`/`max`, `ipo_status`
- **`latest_deal`** — `financing_types` (array of `{"type": "SEED"}` etc., with optional `pre`/`extension` modifiers), `size_min`/`max`, `date_start`/`end`, `investor_ids`
- **`investors`** — `investor_ids` (matches any round, not just latest)

**Pagination & sorting:**
- `page` (0-based), `page_size` (1-100, default 10)
- `sort_by`: `most_recent_raise`, `oldest_raise`, `most_recent_founded`, `oldest_founded`, `largest_valuation`, `smallest_valuation`, `largest_total_raise`, `smallest_total_raise`, `most_funding_rounds`, `most_investors`

**Financing types:** `SEED`, `SERIES_A` through `SERIES_M`, `SAFE`, `CONVERTIBLE_NOTE`, `EQUITY`, `PREFERRED`, `DEBT_FINANCING`, `GRANT`, `FUNDING_ROUND`, and more. Modifiers: `"pre": true`, `"extension": true`

**Employee count ranges:** `1-10`, `11-50`, `51-100`, `101-250`, `251-500`, `501-1000`, `1001-5000`, `5001-10000`, `10001+`

### Get Company (GET)

Look up a single company by identifier.

```bash
curl -s "https://www.tryfundable.ai/api/v1/company/?domain=stripe.com" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Parameters (provide ONE):
- `id` — Company UUID
- `domain` — Domain or full URL (e.g. `stripe.com`)
- `linkedin` — LinkedIn company URL
- `crunchbase` — Crunchbase organization URL

### Search Companies (GET)

Quick fuzzy search by name, or exact match by domain/LinkedIn/Crunchbase. Costs 0 credits.

```bash
curl -s "https://www.tryfundable.ai/api/v1/company/search/?name=stripe" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Parameters (provide ONE):
- `name` — Fuzzy name search with relevance scoring
- `domain` — Exact domain match
- `linkedin` — Full LinkedIn URL (required)
- `crunchbase` — Full Crunchbase URL (required)

**Response:**
```json
{
  "success": true,
  "data": {
    "companies": [
      {
        "id": "uuid",
        "guru_permalink": "stripe",
        "name": "Stripe",
        "short_description": "Stripe is an API-first global payments...",
        "image": "https://images.crunchbase.com/image/upload/...",
        "relevance_score": 120,
        "domain": "stripe.com",
        "website": "https://stripe.com/"
      }
    ]
  }
}
```

### Company Deals (GET)

Get all funding rounds for a company.

```bash
curl -s "https://www.tryfundable.ai/api/v1/company/deals/?domain=stripe.com" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Parameters (provide ONE identifier + optional pagination):
- `id`, `domain`, `linkedin`, `crunchbase`
- `page` (0-based), `page_size` (1-100)

---

## Investors

### List & Filter Investors (POST)

Search and filter investors with portfolio-based filtering.

```bash
curl -s -X POST https://www.tryfundable.ai/api/v1/investors/ \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company_investments": {
      "industries": ["artificial-intelligence"],
      "financing_types": [{"type": "SERIES_A"}],
      "deal_start_date": "2025-01-01"
    },
    "sort_by": "most_recent_deal",
    "page_size": 25
  }'
```

**Filter sections:**
- **`identifiers`** — `ids`, `domains`, `linkedin_urls`, `crunchbase_urls` (max 100 each)
- **`investor`** — `locations`, `employee_count`
- **`company_investments`** — Portfolio filters: `company_ids`, `industries`, `super_categories`, `locations`, `employee_count`, `ipo_status`, `total_raised_min`/`max`, `financing_types`, `deal_size_min`/`max`, `deal_start_date`/`end_date`, `only_lead_deals`, `min_matching_deals`

**Sort options:** `most_recent_deal`, `recent_deals`, `deals_led_ltm`, `total_deals`, `matching_deals`

### Get Investor (GET)

Look up a single investor by identifier.

```bash
curl -s "https://www.tryfundable.ai/api/v1/investor/?domain=sequoiacap.com" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Parameters (provide ONE):
- `id`, `domain`, `linkedin`, `crunchbase`

### Search Investors (GET)

Quick fuzzy search by name, or exact match by domain/LinkedIn/Crunchbase. Costs 0 credits.

```bash
curl -s "https://www.tryfundable.ai/api/v1/investor/search/?name=sequoia" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Parameters (provide ONE):
- `name` — Fuzzy name search
- `domain` — Exact domain match
- `linkedin` — Full LinkedIn URL (required)
- `crunchbase` — Full Crunchbase URL (required)

**Response:**
```json
{
  "success": true,
  "data": {
    "investors": [
      {
        "id": "uuid",
        "guru_permalink": "sequoia-capital",
        "name": "Sequoia Capital",
        "description": "Sequoia is a venture capital firm...",
        "image": "https://images.crunchbase.com/image/upload/...",
        "domain": "sequoiacap.com",
        "website": "https://www.sequoiacap.com/",
        "total_deal_count": 5211,
        "recent_deal_count": 849,
        "lead_deal_count": 1933,
        "latest_deal_date": "2025-12-10T17:10:06+00:00",
        "relevance_score": 99
      }
    ]
  }
}
```

### Investor Deals (GET)

Get all deals an investor participated in.

```bash
curl -s "https://www.tryfundable.ai/api/v1/investor/deals/?domain=sequoiacap.com" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Parameters (provide ONE identifier + optional pagination):
- `id`, `domain`, `linkedin`, `crunchbase`
- `page` (0-based), `page_size` (1-100)

---

## Deals

### List & Filter Deals (POST)

Search and filter funding rounds.

```bash
curl -s -X POST https://www.tryfundable.ai/api/v1/deals/ \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "deal": {
      "financing_types": [{"type": "SERIES_A"}, {"type": "SERIES_B"}],
      "date_start": "2025-01-01",
      "size_min": 5000000
    },
    "company": {
      "industries": ["artificial-intelligence"]
    },
    "sort_by": "most_recent_deal",
    "page_size": 25
  }'
```

**Filter sections:**
- **`identifiers`** — `deal_ids` (UUIDs)
- **`deal`** — `financing_types`, `size_min`/`max`, `date_start`/`end`, `created_start`/`end`
- **`company`** — `company_ids`, `locations`, `industries`, `super_categories`, `employee_count`, `total_raised_min`/`max`, `ipo_status`
- **`investors`** — `investor_ids`

**Sort options:** `most_recent_deal`, `oldest_deal`, `largest_raise`, `smallest_raise`

### Get Deal (GET)

Get a single deal by ID.

```bash
curl -s "https://www.tryfundable.ai/api/v1/deals/{id}/" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

### Get Deal Investors (GET)

Get detailed investor info for a deal, including lead status and personnel.

```bash
curl -s "https://www.tryfundable.ai/api/v1/deals/{id}/investors/" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

---

## Helpers

### Location Search (GET)

Find location permalinks for filtering. Costs 0 credits.

```bash
curl -s "https://www.tryfundable.ai/api/v1/location/search/?name=san+francisco" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Parameters:
- `name`* — Location name to search
- `type` — Filter by `CITY`, `STATE`, `REGION`, or `COUNTRY`

**Response:**
```json
{
  "success": true,
  "data": {
    "locations": [
      {"permalink": "san-francisco-california", "name": "San Francisco", "location_type": "CITY"},
      {"permalink": "san-francisco-bay-area", "name": "San Francisco Bay Area", "location_type": "REGION"}
    ]
  }
}
```

### Industry Search (GET)

Find industry permalinks for filtering. Costs 0 credits.

```bash
curl -s "https://www.tryfundable.ai/api/v1/industry/search/?name=artificial+intelligence" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Parameters:
- `name`* — Industry name to search
- `type` — Filter by `INDUSTRY` or `SUPER_CATEGORY`

**Response:**
```json
{
  "success": true,
  "data": {
    "industries": [
      {"permalink": "artificial-intelligence", "name": "Artificial Intelligence (AI)", "industry_type": "INDUSTRY"},
      {"permalink": "artificial-intelligence-e551", "name": "Artificial Intelligence (AI)", "industry_type": "SUPER_CATEGORY"}
    ]
  }
}
```

---

## Use Cases

1. **Deal Flow Monitoring**: Filter companies by recent funding date to track new rounds
2. **Investor Research**: Look up a VC firm's portfolio and recent deal activity
3. **Market Mapping**: Find all companies in an industry/location with specific funding stages
4. **Competitive Intelligence**: Look up a company's funding history and investors
5. **Lead Generation**: Find recently funded companies by stage, size, and industry
6. **LP Research**: Analyze investor deal patterns, lead rates, and portfolio focus

## Important Notes

- Empty arrays are not allowed — omit the field instead of sending `[]`
- `sort_by` is ignored when using `search_query` (results sort by relevance)
- Search endpoints (`/company/search`, `/investor/search`, `/location/search`, `/industry/search`) cost 0 credits
- LinkedIn and Crunchbase params require full URLs, not bare slugs
- Rate limit: 200 requests per minute
