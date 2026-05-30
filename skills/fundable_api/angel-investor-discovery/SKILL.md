---
name: angel-investor-discovery
description: Find angel investors using `POST /people` with `investment_type: "angel"`. Supports semantic search over their portfolio companies (e.g. "angels in GTM tooling") AND structured filters (industry permalinks, financing types, date windows, lead-only, portfolio location). Then enrich each hit with a full profile and on-thesis deal history. Use when asked "who angel invests in X?", "find angels for my space", "active angels in <industry>", "lead angels in <location>", "angels backing <thesis>", or any angel-investor discovery query.
---

# Angel Investor Discovery

Find angel investors via `POST /people` with `investor.deals.investment_type: "angel"`. The `investor.deals` block accepts both semantic search (`search_query`) and structured filters (industry, financing types, dates, sizes, lead-only, portfolio location). Mix and match.

Two-step workflow:

1. `POST /people` to find angels matching your criteria.
2. `GET /person?id=...` for each top hit to enrich with the full profile.
3. *(Optional, when `search_query` is set)* `POST /companies` with the same thesis + `investors.people_ids: [<person-uuid>]` to surface their on-thesis portfolio companies.

See **Recipes** below for ready-to-paste request bodies covering common patterns.

## When to Use

- "Who angel invests in GTM tooling?"
- "Find angels backing AI infrastructure startups"
- "Show me active angels in fintech with at least 3 recent investments"
- "Who would be a good angel for our developer-tools company?"
- Any thesis-first angel-discovery question (versus a known-firm portfolio lookup, which belongs in `investor-recent-investments`).

---

## Step 1: Semantic Angel Search

`POST /people` with the thesis as `investor.deals.search_query` and `investment_type: "angel"`. Setting any `investor.*` field implicitly requires the person to be an investor; `person_type: "investor"` makes that explicit.

```bash
curl -s -X POST https://www.tryfundable.ai/api/v1/people \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "person_type": "investor",
    "investor": {
      "deals": {
        "investment_type": "angel",
        "search_query": "gtm tooling",
        "min_relevance": 0.6,
        "min_matching_deals": 2,
        "date_start": "2024-01-01"
      }
    },
    "page_size": 10
  }'
```

When `search_query` is set, results are ordered by semantic relevance and `sort_by` is ignored. Each row carries `filtered_deal_count`, `filtered_lead_count`, and `filtered_most_recent_date` — populated only because `investor.deals.*` filters are present. To inspect the actual on-thesis deals for a hit, do the Step 3 `/companies` follow-up.

### Response shape (abridged)

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
          "deal_count_last_12_months": 5,
          "most_recent_deal_date": "2024-08-15",
          "top_industries":   [{ "name": "AI", "permalink": "artificial-intelligence", "count": 7 }],
          "top_locations":    [{ "name": "San Francisco", "permalink": "san-francisco-california", "type": "CITY", "count": 6 }],
          "top_round_types":  [{ "type": "SEED", "count": 18 }]
        },
        "filtered_deal_count": 6,
        "filtered_lead_count": 2,
        "filtered_most_recent_date": "2025-08-12"
      }
    ]
  },
  "meta": { "total_count": 38, "page": 0, "page_size": 10 }
}
```

Collect `id` values for Step 2.

---

## Step 2: Enrich Profile

`GET /person?id=<uuid>` returns the same row shape as search but with **full** (uncapped) `employment_history` and `education_history` — useful for mutual-connection or background context.

```bash
curl -s "https://www.tryfundable.ai/api/v1/person?id=<person-uuid>" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

You can also identify by URL — exactly one of `?id=`, `?linkedin=`, `?crunchbase=`, `?twitter=`:

```bash
curl -s "https://www.tryfundable.ai/api/v1/person?linkedin=https://linkedin.com/in/jane-doe" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY"
```

---

## Step 3: On-Thesis Portfolio Companies

To show the angel's actual *on-thesis* deals (not just any deals they've ever done), do a follow-up `POST /companies` with the **same** semantic thesis as Step 1, plus `investors.people_ids: [<person-uuid>]`. Each returned company carries an inline `latest_deal` — date, type, size, and a `description.short_description` ready to display.

```bash
curl -s -X POST https://www.tryfundable.ai/api/v1/companies \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company": {
      "search_query": "health tracking wearables",
      "min_relevance": 0.3
    },
    "investors": {
      "people_ids": ["<person-uuid>"]
    },
    "page_size": 5
  }'
```

**Why `/companies` and not `/deals`?** `/deals` does **not** support semantic `search_query`. `/companies` supports both `company.search_query` and `investors.people_ids` in the same request. Each company response carries `relevance_score` (0–1) and an inline `latest_deal` block, so one call gives you everything you need to render an on-thesis deal line.

**Batching tip.** To amortize the second semantic call across many angels, pass *all* top-N person UUIDs in a single `investors.people_ids` array. You'll get the union of their on-thesis portfolios in one call. Re-attribute by joining each returned company's deal `investor_ids` / `angel_investor_ids` back to the original person list. Trade-off: loses per-person attribution unless you do the join client-side.

**Alternative — all-time deal history (no thesis filter).** `GET /person/deals?id=<uuid>` returns *every* deal the person participated in (angel + firm-lead), paginated. Use this for a profile-page deal feed, not for thesis-aligned examples. Each row matches the `/company/deals` shape — top-level `round_type`, `total_round_raised` (USD), `date`, `company_id`, `investor_ids`, `angel_investor_ids`, `deal_descriptions.short_description`.

---

## Tuning the Search

Step 1 is a semantic search with several compounding filters. Three knobs disproportionately shape the result quality. Touch them in this order.

### 1. Phrasing of `search_query` (biggest lever)

The embedding picks up implicit market context, audience, and stage from the words you choose. Small phrasing changes reshape the result population entirely — not just rank.

| Vague / ambiguous | Sharper alternative | Why it works |
|---|---|---|
| `"gtm tooling"` | `"gtm tooling for sales"` | "for sales" anchors the embedding to B2B SaaS sales-tech, surfacing SaaS-GTM-focused operators (Mark Goldberg, Naomi Pilosof Ionita, Alok Goyal) instead of generic Indian-SaaS angels. |
| `"physical hardware for health tracking"` | `"health tracking wearables"` | Cleaner noun phrase. The first returned 0 at `min_relevance=0.4`; the second returned 10. |
| `"AI"` | `"AI infrastructure"` or `"AI dev tools"` | Bare `"AI"` matches everything. Add the application area. |

Rules of thumb:
- 3–5 words; one clean noun phrase, no filler ("for", "that", "in" are okay if they anchor context).
- Include **audience or buyer** when relevant ("for sales", "for developers", "for hospitals").
- Avoid generic mega-categories alone (`"AI"`, `"SaaS"`, `"hardware"`).
- If a query returns 0 at `min_relevance=0.4`, rephrase before lowering the threshold.

### 2. `investment_type` — default to `"angel"` for thesis discovery

`investment_type` filters at the **deal level** — it constrains which of the person's deals are allowed to satisfy the `search_query` and `min_matching_deals` checks.

- `"angel"` — the matching deal must be an angel investment (no firm attached). Every result is guaranteed to have backed the thesis *as an angel*. This is the strongest personal-conviction signal and is the right default for thesis-driven angel discovery.
- `"institutional"` — the matching deal must be a firm-attached lead-partner deal. Use when you want firm-led signal, not personal angel checks.
- `"all"` — either counts. Use when you want the union — e.g. "show me anyone who has touched this thesis, whether as an angel or as a firm partner." Pair with a client-side `is_angel: true` filter on the response to keep only people who do *some* angel investing somewhere (even if their thesis-relevant deal was firm-attached).

Empirical comparison for `"sales and marketing tools"` (no date floor, page_size=50):

| Config | Hits |
|---|---|
| `"angel"` | **50** (all are angels by definition) |
| `"all"` + client-side `is_angel` filter | 30 |

`"angel"` returns *more* angels here, not fewer — because `"all"` lets institutional-typed deals consume the relevance ranking, displacing weaker semantic-match-but-still-genuine angel deals. Default to `"angel"` unless you specifically want firm-attached signal.

### 3. `min_relevance` thresholds

The OpenAPI examples ship with `0.5`–`0.6`. In practice the right value depends on dataset density for your thesis and on which endpoint you're hitting.

| Threshold | Behavior | When to use |
|---|---|---|
| `0.6+` | Strict, high precision; drops borderline matches | Well-phrased thesis in a dense space ("AI infrastructure", "fintech"). Short, tight list. |
| `0.4`–`0.5` | Balanced default. Matches the OpenAPI examples. | Most Step 1 thesis searches. Good starting point. |
| `0.2`–`0.3` | Recall-mode. Expect noise. | Niche / sparse spaces, or the Step 3 cross-filter (`/companies` with `search_query` + `people_ids`) where two semantic conditions compound. |
| Below `0.2` | Effectively off; pure embedding rank | Diagnostic only. |

Important: Step 3 is **stricter** than Step 1 even at the same threshold. Step 1's `investor.deals.search_query` matches at the deal-history level; Step 3's `company.search_query` matches at the company-embedding level. A person can have `filtered_deal_count: 1` in Step 1 yet 0 on-thesis companies in Step 3 at the same `min_relevance`. Default Step 1 to `0.4`–`0.5` and Step 3 to `0.2`–`0.3`.

### 4. Other compounding filters — add last

`min_matching_deals`, `date_start/end`, `only_lead_deals`, `financing_types`, and `industries` all compound multiplicatively with the semantic filter. Each one further narrows the result set. Add them only after the search_query + investment_type + min_relevance combo is producing the right *kind* of people.

- `min_matching_deals: 1` (default) is right for thesis-discovery. Ramp to `2`–`3` only when you have lots of candidates and want conviction signal.
- `only_lead_deals: true` is a *strong* filter — most angels never lead. Use only when you specifically need lead capacity.

---

## Recipes

Five ready-to-use `POST /people` request bodies. Pick the one that matches the question, edit the values, send.

### Recipe 1 — Thesis-driven angel discovery (semantic)

> "Find angels backing companies like X."

```json
{
  "person_type": "investor",
  "investor": {
    "deals": {
      "investment_type": "angel",
      "search_query": "sales and marketing tools",
      "min_relevance": 0.1,
      "min_matching_deals": 1
    }
  },
  "page_size": 50
}
```

Pair with the Step 3 `/companies` cross-filter to show each angel's on-thesis portfolio.

### Recipe 2 — Active angels in an industry (no semantic)

> "Who's been actively angel-investing in fintech in the last 12 months?"

```json
{
  "person_type": "investor",
  "investor": {
    "deals": {
      "investment_type": "angel",
      "industries": ["fintech"],
      "date_start": "2024-05-01",
      "min_matching_deals": 2
    }
  },
  "page_size": 50,
  "sort_by": "lead_deal_count_last_12_months"
}
```

No `search_query` → no semantic-search quota cost. Sort by recent lead count to surface the most active.

### Recipe 3 — Lead-only angels by location + industry

> "Angels in San Francisco who've actually led a Series A in AI."

```json
{
  "person_type": "investor",
  "investor": {
    "deals": {
      "investment_type": "angel",
      "only_lead_deals": true,
      "industries": ["artificial-intelligence"],
      "portfolio_locations": ["san-francisco-california"],
      "financing_types": [{"type": "SERIES_A"}]
    }
  },
  "page_size": 50
}
```

`only_lead_deals: true` is strong — most angels never lead. Use sparingly.

### Recipe 4 — Cross-type: founders who also angel-invest

> "Founders at fintech companies who also angel-invested in AI infrastructure."

```json
{
  "person": {"roles": ["founder"]},
  "company": {"industries": ["fintech"]},
  "investor": {
    "deals": {
      "investment_type": "angel",
      "search_query": "AI infrastructure",
      "min_relevance": 0.1,
      "min_matching_deals": 1
    }
  },
  "page_size": 50
}
```

Setting any field under `company.*` requires the person to have a current employer; any field under `investor.*` requires them to be an investor. Both → genuine cross-type query.

### Recipe 5 — Batch lookup by LinkedIn URL

> "Pull these specific people."

```json
{
  "identifiers": {
    "linkedin_urls": [
      "https://linkedin.com/in/jane-doe-12345",
      "https://linkedin.com/in/john-smith-67890"
    ]
  }
}
```

Resolves up to 100 people per call. Useful for hydrating known UUIDs/handles into the constant unified shape.

---

## Parameters — Step 1 (`investor.deals.*`)

| Parameter | Purpose | Example |
|---|---|---|
| `investment_type` | `"angel"` (recommended for thesis discovery), `"institutional"`, or `"all"` (API default). See Tuning. | `"angel"` |
| `search_query` | Natural-language thesis. Orders results by relevance. Phrasing matters — see Tuning. | `"gtm tooling for sales"` |
| `min_relevance` | 0..1 — drop weak semantic matches. Default to `0.4`–`0.5` for Step 1. | `0.5` |
| `min_matching_deals` | Require ≥ N deals matching the deal filters | `1` |
| `only_lead_deals` | Only count deals where the person/firm led | `true` |
| `date_start` / `date_end` | Restrict deal window (ISO date) | `"2024-01-01"` |
| `financing_types` | `[{ "type": "SEED" }, ...]` | seed-only filter |
| `size_min` / `size_max` | Deal size range (USD, actual not millions) | `500000` |
| `industries` / `super_categories` | Portfolio company industry filters | `["fintech"]` |
| `portfolio_locations` | Where the portfolio company is HQ'd | `["san-francisco-california"]` |
| `total_raised_min/max` | Portfolio company total raised (USD) | `1000000` |

Top-level: `page`, `page_size` (max 500), `person_type` (`"investor"` to force investor-only).

---

## Tips

- See **Tuning the Search** above for the three biggest levers (phrasing, `investment_type`, `min_relevance`). Read it before tweaking other parameters.
- Semantic search hits monthly usage limits — a `429` with code `USAGE_LIMIT_EXCEEDED` (or a `504 TIMEOUT`) only happens when `search_query` is set. Fall back to non-semantic filters (industry permalinks, financing types) if you hit the limit.
- `filtered_deal_count`, `filtered_lead_count`, and `filtered_most_recent_date` are populated **only** when any `investor.deals.*` filter is set; otherwise they're `null`. Use them to rank/qualify hits — e.g. require `filtered_lead_count >= 1` for angels who actually led. For the actual on-thesis deals, do the Step 3 `/companies` follow-up.
- Pure angels return `investment_firms: []` and have `current_company` but no firm affiliations. Investors who operate under a fund have `investment_firms: [...]` populated. `is_angel: true` can be true for either — it just means the person has *some* angel activity.
- `investor_highlights` is `null` for non-investors. Aggregates (`total_deal_count`, `lead_deal_count`, `deal_count_last_12_months`, `lead_deal_count_last_12_months`, `top_industries`, `top_locations`, `top_round_types`, `most_recent_deal_date`) all live under it. Top-level discriminators (`is_investor`, `is_angel`, `has_led_deal`, `investment_firms`) stay top-level so you can branch without dereferencing.
- All dollar values in requests and responses are **actual USD** (not millions): `size_min: 500000` = $500k.
- The `/person/search?name=...` endpoint exists for fuzzy name lookup if you already know who you're looking for; it returns lightweight rows. Use `/person?id=...` for full detail.

---

## Error Handling

- **400** — Validation error (bad enum, bad date, empty `search_query`)
- **401** — Invalid or missing API key
- **402** — Insufficient credits
- **404** — Person not found (Steps 2–3)
- **422** — Unknown parameter (per-block whitelist enforced — don't put `industries` outside `investor.deals` or `company`)
- **429** — Either `RATE_LIMIT_EXCEEDED` (per-minute) or `USAGE_LIMIT_EXCEEDED` (monthly semantic-search quota — only with `search_query`)
- **504** — `TIMEOUT` on semantic search; simplify the query or add stricter filters
- Empty arrays are not allowed — omit the field instead of sending `[]`

---

## Example: Full Pipeline (curl)

```bash
# Step 1 — find angels for a thesis
curl -s -X POST https://www.tryfundable.ai/api/v1/people \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "person_type": "investor",
    "investor": {
      "deals": {
        "investment_type": "angel",
        "search_query": "gtm tooling",
        "min_relevance": 0.6,
        "min_matching_deals": 2
      }
    },
    "page_size": 10
  }' | jq '.data.people[] | {id, name, title, filtered_deal_count}'

# Step 2 — full profile
curl -s "https://www.tryfundable.ai/api/v1/person?id=<uuid>" \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" | jq '.data.person'

# Step 3 — on-thesis portfolio (same thesis as Step 1 + person filter)
curl -s -X POST https://www.tryfundable.ai/api/v1/companies \
  -H "Authorization: Bearer $FUNDABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company": { "search_query": "gtm tooling", "min_relevance": 0.3 },
    "investors": { "people_ids": ["<uuid>"] },
    "page_size": 5
  }' | jq '.data.companies[] | {name, domain, relevance_score, latest_deal: {type: .latest_deal.type, size: .latest_deal.size_usd, date: .latest_deal.date}}'
```
