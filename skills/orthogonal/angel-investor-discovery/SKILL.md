---
name: angel-investor-discovery
description: Find angel investors via `POST /people` with `investor.deals.investment_type: "angel"` — supports semantic thesis search, structured filters (industry, financing types, dates, lead-only, portfolio location), then enriches top hits with full profile and on-thesis portfolio companies. Use when asked "who angel invests in X?", "find angels for my space", "active angels in <industry>", "lead angels in <location>", or any angel-investor discovery query.
---

# Angel Investor Discovery

Find angel investors with the Fundable API. Three-step workflow:
1. `POST /people` with `investor.deals.investment_type: "angel"` to find angels matching a thesis or filters
2. `GET /person?id=...` to enrich top hits with full profiles
3. (When `search_query` is set) `POST /companies` with the same thesis + `investors.people_ids` to surface each angel's on-thesis portfolio

## When to Use

- User asks "who angel invests in X?" or "find angels backing <thesis>"
- User wants active angels in an industry, location, or financing stage
- User asks for lead-capable angels for a specific round
- Thesis-first angel discovery (vs. a known-firm portfolio lookup, which belongs in `investor-recent-investments`)

---

## Step 1: Search for Angels

```bash
curl -s -X POST https://www.tryfundable.ai/api/v1/people \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "person_type": "investor",
    "investor": {
      "deals": {
        "investment_type": "angel",
        "search_query": "gtm tooling for sales",
        "min_relevance": 0.5,
        "min_matching_deals": 1
      }
    },
    "page_size": 50
  }'
```

Setting any `investor.*` field implicitly requires the person to be an investor; `person_type: "investor"` makes that explicit. When `search_query` is set, results are ordered by semantic relevance and `sort_by` is ignored.

**Response (abridged):**

```json
{
  "success": true,
  "data": {
    "people": [
      {
        "id": "uuid",
        "name": "Jane Doe",
        "title": "Founder & CEO",
        "linkedin_url": "https://linkedin.com/in/jane-doe",
        "current_company": { "id": "...", "name": "Acme", "permalink": "acme", "domain": "acme.com" },
        "is_investor": true,
        "is_angel": true,
        "has_led_deal": true,
        "investment_firms": [
          { "id": "...", "name": "Acme Capital", "permalink": "acme-capital",
            "domain": "acme.vc", "deal_count": 12, "last_deal_date": "2024-08-15" }
        ],
        "investor_highlights": {
          "total_deal_count": 47,
          "lead_deal_count": 12,
          "lead_deal_count_last_12_months": 3,
          "most_recent_deal_date": "2024-08-15",
          "top_industries":  [{ "name": "AI", "permalink": "artificial-intelligence", "count": 7 }],
          "top_locations":   [{ "name": "San Francisco", "permalink": "san-francisco-california", "count": 6 }],
          "top_round_types": [{ "type": "SEED", "count": 18 }]
        },
        "filtered_deal_count": 6,
        "filtered_lead_count": 2,
        "filtered_most_recent_date": "2025-08-12"
      }
    ]
  },
  "meta": { "total_count": 38, "page": 0, "page_size": 50 }
}
```

Collect `id` values for Step 2.

---

## Step 2: Enrich Profile

`GET /person` returns the same row shape as Step 1 with **full** (uncapped) `employment_history` and `education_history`.

```bash
curl -s "https://www.tryfundable.ai/api/v1/person?id=<person-uuid>" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

Identify by exactly one of `?id=`, `?linkedin=`, `?crunchbase=`, `?twitter=`:

```bash
curl -s "https://www.tryfundable.ai/api/v1/person?linkedin=https://linkedin.com/in/jane-doe" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

---

## Step 3: On-Thesis Portfolio Companies

When Step 1 used `search_query`, follow up with `POST /companies` using the **same** thesis plus `investors.people_ids` to surface each angel's actual on-thesis deals. Each returned company carries an inline `latest_deal` (date, type, size, short description).

```bash
curl -s -X POST https://www.tryfundable.ai/api/v1/companies \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company": {
      "search_query": "gtm tooling for sales",
      "min_relevance": 0.3
    },
    "investors": {
      "people_ids": ["<person-uuid>"]
    },
    "page_size": 5
  }'
```

---

## Parameters

### Step 1: `investor.deals.*`
- **`investment_type`** — `"angel"` (recommended for thesis discovery), `"institutional"`, or `"all"`. Filters at the deal level.
- **`search_query`** — Natural-language thesis. Orders by relevance. 3–5 words, one clean noun phrase, include audience when relevant (e.g. `"gtm tooling for sales"`).
- **`min_relevance`** — 0..1. Default `0.4`–`0.5` for Step 1; `0.2`–`0.3` for Step 3 (it's stricter at the same threshold).
- **`min_matching_deals`** — Require ≥ N deals matching the deal filters. Default `1`.
- **`only_lead_deals`** — Strong filter; most angels never lead. Use only when lead capacity matters.
- **`date_start` / `date_end`** — ISO 8601 deal window
- **`financing_types`** — `[{"type": "SEED"}, {"type": "SERIES_A"}]`. Optional `"pre"`, `"extension"` booleans.
- **`size_min` / `size_max`** — Deal size in actual USD (not millions)
- **`industries` / `super_categories`** — Portfolio-company industry permalinks
- **`portfolio_locations`** — Location permalinks where the portfolio company is HQ'd
- **`total_raised_min` / `total_raised_max`** — Portfolio company total raised (USD)

### Top-level
- **`person_type`** — `"investor"` to force investor-only
- **`person.roles`** — e.g. `["founder"]` for cross-type queries
- **`company.*`** — current-employer filters (industries, locations, etc.); requires the person to have a current employer
- **`identifiers.linkedin_urls`** — batch resolve up to 100 known people in one call
- **`page` / `page_size`** — pagination (max 500)
- **`sort_by`** — ignored when `search_query` is set

---

## Usage Examples

| Use Case | Key Parameters |
|---|---|
| Thesis-driven angel discovery | `investor.deals.investment_type: "angel"`, `search_query`, `min_relevance: 0.4` |
| Active angels in fintech (last 12 mo) | + `industries: ["fintech"]`, `date_start`, `min_matching_deals: 2`, `sort_by: "lead_deal_count_last_12_months"` |
| Lead-only angels in SF backing AI Series A | + `only_lead_deals: true`, `industries: ["artificial-intelligence"]`, `portfolio_locations: ["san-francisco-california"]`, `financing_types: [{"type": "SERIES_A"}]` |
| Cross-type: founders who also angel-invest | `person.roles: ["founder"]` + `company.industries` + `investor.deals` block |
| Batch lookup specific people | `identifiers.linkedin_urls: [...]` (up to 100) |

Paste-ready JSON bodies for each row live as commented `PEOPLE_QUERY` blocks in `examples/find_angel_investors/find_angel_investors.py`.

---

## Error Handling

- **400** — Validation error (bad enum, bad date, empty `search_query`)
- **401** — Invalid or missing API key
- **402** — Insufficient credits
- **404** — Person not found (Steps 2–3)
- **422** — Unknown parameter (per-block whitelist — don't put `industries` outside `investor.deals` or `company`)
- **429** — `RATE_LIMIT_EXCEEDED` (per-minute) or `USAGE_LIMIT_EXCEEDED` (monthly semantic-search quota — only with `search_query`)
- **504** — `TIMEOUT` on semantic search; simplify the query or add stricter filters
- Empty arrays are not allowed — omit the field instead of sending `[]`

---

## Tips

- **Phrasing of `search_query` is the biggest lever.** Small wording changes reshape the result population, not just rank. Prefer 3–5-word noun phrases with audience context (`"gtm tooling for sales"` ≫ `"gtm tooling"`). If a query returns 0 at `min_relevance: 0.4`, rephrase before lowering the threshold.
- **Default `investment_type` to `"angel"`** for thesis discovery — it guarantees every hit backed the thesis as an angel. Use `"all"` only when you want firm-attached signal too.
- **`filtered_deal_count`, `filtered_lead_count`, `filtered_most_recent_date`** are populated only when `investor.deals.*` filters are set; otherwise null. Use them to rank/qualify hits.
- Pure angels return `investment_firms: []`. `is_angel: true` just means the person has *some* angel activity — they may also operate a fund.
- All dollar values in requests and responses are **actual USD** (not millions): `size_min: 500000` = $500k.
- `/person/search?name=...` exists for fuzzy name lookup; use `/person?id=...` for full detail.
