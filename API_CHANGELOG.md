# Fundable API — Changelog for Existing Consumers

> **Read this once.** It covers every change between the previous published OpenAPI specs and the current ones in `openapi/`. It is written so that a human can scan the top, then hand the rest to an AI / engineer to do the actual integration work — every field, type, and required-ness is called out explicitly.

---

## Executive summary

1. **People are now a first-class resource.** Four new endpoints (`POST /people`, `GET /person`, `GET /person/deals`, `GET /person/search`) let you search, resolve, and pull deal history for individual humans (founders, partners, angels, key personnel).
2. **Angel investors are now surfaced everywhere a deal is returned.** Every deal-shaped object now carries a new required `angel_investor_ids` array, and `investor_ids` is now **firms-only** (it used to be a mix).
3. **`GET /deals/{id}/investors` response shape has changed.** Firms and angels are returned in two separate arrays (`investors` + `angel_investors`). The old `angel_investor: true` flag is gone.
4. **`DealInvestor.personnel` shape has changed.** It used to be an array of strings (names). It is now an array of objects with `id`, `name`, `linkedin`, `crunchbase`, `twitter`.
5. **You can now filter Deals and Companies by people.** `investors.people_ids` was added to both `POST /deals` and `POST /companies`.
6. **Server host moved to `www.tryfundable.ai`.** Old bare-domain may still redirect; update hardcoded base URLs to be safe.
7. **`page_size` cap raised from 100 → 500** on every list endpoint. Default is still 10.
8. **Slug / URL handling on search endpoints is more forgiving and better documented** (notably `GET /company/search?domain=` now accepts full URLs).

### Impact at a glance

| Endpoint | Impact | Type |
|---|---|---|
| `POST /people` | NEW | Net-new |
| `GET /person` | NEW | Net-new |
| `GET /person/deals` | NEW | Net-new |
| `GET /person/search` | NEW | Net-new |
| `GET /deals/{id}/investors` | **BREAKING** | Response split into two arrays; `personnel` shape changed; `angel_investor` flag removed |
| `POST /deals` | ADDITIVE (semantically breaking) | New `angel_investor_ids` required field; `investor_ids` is now firms-only; new `investors.people_ids` filter |
| `POST /companies` | ADDITIVE (semantically breaking) | `CompanyDeal.angel_investor_ids` required; `LatestDeal.angel_investor_ids` required; new `investors.people_ids` filter |
| `GET /investor/deals` | ADDITIVE | `InvestorDeal.angel_investor_ids` required |
| `POST /investors` | MINOR | `InvestorsPostBody` now fully expanded inline (docs fidelity); new `filtered_*` clarifications |
| `GET /company/search` | MINOR | `domain` accepts full URL; same for `linkedin`/`crunchbase` |
| `GET /location/search`, `GET /industry/search` | MINOR | Description + alias params (`location_type`, `industry_type`) documented |
| All endpoints | MINOR | Host → `www.tryfundable.ai`; `page_size` max → 500 |

---

## 1. Breaking changes — action required

### 1.1 `GET /deals/{id}/investors` — response now splits firms vs angels

**What changed.** The response used to return a single `data.investors[]` containing both firm and angel investors, with angels distinguished by `angel_investor: true`. It now returns two arrays — `data.investors[]` (firms only) and `data.angel_investors[]` (people) — and the `angel_investor` boolean has been removed from the firm-investor schema.

**Before**

```json
{
  "success": true,
  "data": {
    "investors": [
      {
        "id": "c5a3f6ac-f6c9-4686-aa6e-12aeb7419b82",
        "name": "Sequoia Capital",
        "lead_investor": true,
        "angel_investor": false,
        "personnel": ["John Smith"],
        "financing_type": "SERIES_A",
        "domain": "sequoiacap.com",
        "linkedin": "https://linkedin.com/company/sequoia-capital",
        "crunchbase": "https://crunchbase.com/organization/sequoia-capital",
        "is_debt_investor": false
      },
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "name": "Jane Angel",
        "lead_investor": false,
        "angel_investor": true,
        "personnel": [],
        "financing_type": "SEED"
      }
    ]
  }
}
```

**After**

```json
{
  "success": true,
  "data": {
    "investors": [
      {
        "id": "c5a3f6ac-f6c9-4686-aa6e-12aeb7419b82",
        "name": "Sequoia Capital",
        "lead_investor": true,
        "personnel": [
          {
            "id": "f1a2b3c4-d5e6-7890-abcd-ef1234567890",
            "name": "John Smith",
            "linkedin": "https://linkedin.com/in/johnsmith",
            "crunchbase": "https://crunchbase.com/person/john-smith",
            "twitter": "https://x.com/johnsmith"
          }
        ],
        "financing_type": "SERIES_A",
        "domain": "sequoiacap.com",
        "linkedin": "https://linkedin.com/company/sequoia-capital",
        "crunchbase": "https://crunchbase.com/organization/sequoia-capital"
      }
    ],
    "angel_investors": [
      {
        "id": "b3e9c7d1-2f4a-4d5e-9c1b-7a8f3e2d1c6a",
        "name": "Jane Angel",
        "financing_type": "SEED",
        "linkedin": "https://linkedin.com/in/janeangel",
        "crunchbase": null,
        "twitter": "https://x.com/janeangel"
      }
    ]
  }
}
```

**Schema details**

- `data.investors` and `data.angel_investors` are **both required** in the response.
- `DealInvestor` (firm) — `required: [id, name]`. The `angel_investor` boolean is **removed**. `is_debt_investor` is no longer in the `required` set.
- `AngelInvestor` (new schema) — `required: [id]`. Fields: `id` (UUID, resolves via `/person`), `name`, `financing_type`, `linkedin`, `crunchbase`, `twitter`.
- `PersonnelMember` (new schema) — `required: [id]`. Fields: `id` (UUID, resolves via `/person`), `name`, `linkedin`, `crunchbase`, `twitter`.

**Migration**

- Read both `data.investors` and `data.angel_investors`. If your UI treated them as one list, concatenate them client-side.
- Replace any `if (investor.angel_investor)` branching with array-of-origin (the array the record came from).
- If you displayed personnel as a string list, switch to `personnel.map(p => p.name)` (and consider showing the new social links).

---

### 1.2 `DealInvestor.personnel` — array of strings → array of objects

Already covered by example above, but flagged separately because some integrations consume `DealInvestor` outside of `GET /deals/{id}/investors`.

**Before:** `personnel: ["John Smith", "Roelof Botha"]`

**After:**
```json
"personnel": [
  { "id": "f1a2b3c4-...", "name": "John Smith", "linkedin": "...", "crunchbase": "...", "twitter": "..." },
  { "id": "9d8c7b6a-...", "name": "Roelof Botha", "linkedin": "...", "crunchbase": null, "twitter": null }
]
```

Each `id` is a `Person` UUID and resolves via `GET /person?id=...`.

---

### 1.3 `investor_ids` is now firm-only; `angel_investor_ids` is the angel companion

This is **semantically breaking**: the field name and type didn't change, but its contents did. If you treated `investor_ids` as "everyone who invested," angels are no longer in there.

Affected schemas (all four are deal-shaped):

| Schema | Returned by |
|---|---|
| `Deal` | `POST /deals` |
| `CompanyDeal` | `POST /companies`, `GET /company/deals` |
| `LatestDeal` (nested on Company) | `POST /companies`, `GET /company` |
| `InvestorDeal` | `GET /investor/deals` |

All four now have:

```json
"investor_ids": ["c5a3f6ac-...", "..."],          // firms only
"angel_investor_ids": ["b3e9c7d1-..."]            // people; resolve via /person
```

`angel_investor_ids` is **required** (empty array `[]` when no angels) on `Deal`, `CompanyDeal`, `LatestDeal`, and `InvestorDeal`.

**Migration**

- If you cared about firm investors only, no change needed.
- If you cared about "all investors", do `[...investor_ids, ...angel_investor_ids]`.
- Resolve angel UUIDs via `GET /person?id=<uuid>` (see §2.3).

---

### 1.4 Server host moved to `www.tryfundable.ai`

```
- https://tryfundable.ai/api/v1
+ https://www.tryfundable.ai/api/v1
```

```bash
curl -H 'Authorization: Bearer vg_your_api_key_here' \
  https://www.tryfundable.ai/api/v1/deals
```

The bare domain may continue to redirect, but update hardcoded base URLs.

---

## 2. Net-new — People API

Four endpoints. All are authenticated with the same `Authorization: Bearer vg_...` header as the rest of the API. All accept the same date format (`YYYY-MM-DD`) and currency (actual USD, not millions) as the rest of the API. All four return the standard pagination/credits envelope (`meta.total_count`, `meta.page`, `meta.page_size`, `meta.credits_used`, `meta.credit_source`, `meta.monthly_credits_remaining`, `meta.purchased_credits_remaining`).

### 2.1 `POST /people` — search/filter people

The most powerful of the four. Filters span four blocks: `identifiers`, `person`, `company` (current employer), `investor` (investor activity). Includes optional AI semantic search.

**Top-level body shape**

```jsonc
{
  "person_type": "any",          // "company" | "investor" | "any" (default)
  "identifiers": { ... },         // batch lookup
  "person": { ... },              // person-attribute filters
  "company": { ... },             // current-employer filters (implicitly requires current employer)
  "investor": { ... },            // investor filters (implicitly requires investor)
  "page": 0,
  "page_size": 10,                // 1..500
  "sort_by": "most_recent_deal_date"
}
```

**`identifiers` block** — all string arrays, max 100 each:
- `ids` (UUID[])
- `linkedin_urls` (full LinkedIn person URLs)
- `crunchbase_urls`
- `twitter_urls`

**`person` block:**
- `roles[]` — enum: `founder`, `ceo`, `key_person`
- `contact_types[]` — enum: `linkedin`, `email`, `phone`, `twitter`
- `job_titles[]` — normalized keys (e.g. `ceo`, `cto`, `vp-engineering`)
- `education_schools[]` — institution permalinks (e.g. `stanford-university`)
- `linkedin_companies[]` — past/current employer LinkedIn IDs

**`company` block** — current employer filters. Setting any field implicitly requires the person to have a current employer:
- `search_query` (string) — AI semantic search against employer description. **Overrides `sort_by`** when set.
- `min_relevance` (0–1) — only with `search_query`
- `ids` (UUID[]), `industries[]`, `super_categories[]`, `locations[]` (all permalinks)
- `employee_count[]` — `1-10`, `11-50`, `51-100`, `101-250`, `251-500`, `501-1000`, `1001-5000`, `5001-10000`, `10001+`
- `ipo_status[]` — `public`, `private`, `acquired`, `delisted`
- `total_raised_min`, `total_raised_max` (USD, actual dollars)
- `investor_people_ids` (UUID[]) — current employer raised from these people
- `latest_deal` (nested object) — `financing_types[]` (objects: `{type, pre?, extension?}`), `size_min`, `size_max`, `date_start`, `date_end`, `investor_ids[]`, `investor_locations[]`

**`investor` block** — investor identity & deal activity:
- `ids[]` (firm UUIDs), `domains[]` (max 100), `linkedin_urls[]`, `crunchbase_urls[]`, `permalinks[]`, `locations[]`, `employee_count[]`
- `deals` (nested) — `investment_type` (enum: `all` | `angel` | `institutional`), `min_matching_deals` (int), `only_lead_deals` (bool), `financing_types[]`, `size_min`/`size_max`, `date_start`/`date_end`, `search_query` (AI), `min_relevance`, `industries[]`, `super_categories[]`, `portfolio_locations[]`, `portfolio_employee_count[]`, `ipo_status[]`, `total_raised_min`/`total_raised_max`

**`sort_by` enum:** `most_recent_deal_date` (default), `total_raised`, `latest_deal_size`, `followers`, `connections`, `name`, `total_deal_count`, `recent_deal_count`, `lead_deal_count`, `lead_deal_count_last_12_months`, `filtered_deal_count`. Non-applicable values resolve to `0`/`null` and sort to the bottom (DESC). Ignored when semantic search is active.

**Sample request**

```json
POST /api/v1/people
{
  "person_type": "investor",
  "investor": {
    "deals": {
      "investment_type": "angel",
      "only_lead_deals": false,
      "financing_types": [{ "type": "SEED" }, { "type": "SERIES_A" }],
      "date_start": "2024-01-01",
      "industries": ["artificial-intelligence"],
      "min_matching_deals": 2
    }
  },
  "page_size": 25,
  "sort_by": "lead_deal_count_last_12_months"
}
```

**Sample response (truncated to one row, all field groups present)**

```jsonc
{
  "success": true,
  "data": {
    "people": [
      {
        // identity
        "id": "b3e9c7d1-2f4a-4d5e-9c1b-7a8f3e2d1c6a",
        "name": "Jane Angel",
        "title": "Partner",
        "linkedin_url": "https://linkedin.com/in/janeangel",
        "crunchbase_url": "https://crunchbase.com/person/jane-angel",
        "location": "San Francisco, CA",
        "city": "San Francisco",
        "country_code": "US",
        "about": "Investor and former founder…",
        "twitter_url": "https://x.com/janeangel",

        // flags
        "is_founder": false,
        "is_ceo": false,
        "is_key_person": true,
        "is_current": true,
        "is_investor": true,
        "is_angel": true,
        "has_led_deal": true,

        // social
        "followers": 12345,
        "connections": 500,

        // employment & education (max 3 each in /people; full in /person)
        "current_company": {
          "id": "f1a2b3c4-...",
          "name": "Acme Capital",
          "permalink": "acme-capital",
          "domain": "acme.vc"
        },
        "employment_history": [ /* EmploymentRecord, ≤ 3 */ ],
        "education_history":  [ /* EducationRecord,  ≤ 3 */ ],

        // firms the person invests under (empty for pure angels)
        "investment_firms": [
          { "id": "...", "name": "Acme Capital", "permalink": "acme-capital",
            "domain": "acme.vc", "deal_count": 12, "last_deal_date": "2024-08-15" }
        ],

        // aggregated investor activity — null when is_investor is false
        "investor_highlights": {
          "deal_count": 24,
          "lead_deal_count": 8,
          "lead_deal_count_last_12_months": 3,
          "recent_deal_count": 5,
          "most_recent_deal_date": "2024-08-15",
          "top_industries":  [ { "name": "Artificial Intelligence", "permalink": "artificial-intelligence", "count": 7 } ],
          "top_locations":   [ { "name": "San Francisco", "full_name": "San Francisco, California, United States",
                                  "permalink": "san-francisco-california", "type": "CITY", "count": 6 } ],
          "top_round_types": [ { "type": "SEED", "count": 12 } ]
        },

        // populated only when investor.deals.* filters set
        "filtered_deal_count": 4,
        "filtered_lead_count": 2,
        "filtered_most_recent_date": "2024-08-15"
      }
    ]
  },
  "meta": {
    "total_count": 137,
    "page": 0,
    "page_size": 25,
    "credits_used": 25,
    "credit_source": "monthly",
    "monthly_credits_remaining": 9750,
    "purchased_credits_remaining": null
  }
}
```

**Key rules to encode in your client**

- The response shape is **constant** — every row has every field. Top-level discriminators (`is_investor`, `is_angel`, `has_led_deal`, `investment_firms`) stay top-level so you can branch without dereferencing.
- Investor aggregates live under `investor_highlights` (`deal_count`, `lead_deal_count`, `lead_deal_count_last_12_months`, `recent_deal_count`, `most_recent_deal_date`, `top_industries`, `top_locations`, `top_round_types`). The whole object is `null` when `is_investor` is `false` — null-check before reading.
- `employment_history` and `education_history` are **capped at 3 items** here. Use `GET /person` to get the full lists.
- `filtered_deal_count`, `filtered_lead_count`, `filtered_most_recent_date` are populated **only** when at least one `investor.deals.*` filter is set. Otherwise they're `null`.
- `search_query` (in `company` or `investor.deals`) **overrides `sort_by`**.

### 2.2 `GET /person` — full person detail

Pick **exactly one** of `id` / `linkedin` / `crunchbase` / `twitter`.

```
GET /api/v1/person?id=b3e9c7d1-2f4a-4d5e-9c1b-7a8f3e2d1c6a
GET /api/v1/person?linkedin=https://linkedin.com/in/janeangel
GET /api/v1/person?crunchbase=https://crunchbase.com/person/jane-angel
GET /api/v1/person?twitter=https://x.com/janeangel
```

**Response shape:** identical to a row of `POST /people`, except `employment_history` and `education_history` are **unbounded** (full history).

```json
{
  "success": true,
  "data": { "person": { /* PersonDetail — same as PersonSearchResult, full history */ } },
  "meta": { "page": 0, "page_size": 1, "credits_used": 1, "credit_source": "monthly",
            "monthly_credits_remaining": 9999, "purchased_credits_remaining": null }
}
```

Errors of note: `400 INVALID_IDENTIFIER`, `400 MISSING_IDENTIFIER`, `404 PERSON_NOT_FOUND`.

### 2.3 `GET /person/deals` — every deal a person was on

Use this to resolve `angel_investor_ids` (or `personnel[].id`) into the deals that person participated in — both as an angel and as a partner of a firm.

```
GET /api/v1/person/deals?id=<uuid>&page=0&page_size=50
```

- Same identifier rules as `/person` (`id`, `linkedin`, `crunchbase`, `twitter` — exactly one).
- `page_size` 1–500, default 10.
- Each deal in the response has the same shape as `/company/deals` items.

```json
{
  "success": true,
  "data": { "deals": [ /* same shape as /company/deals items */ ] },
  "meta": { "total_count": 24, "page": 0, "page_size": 50 }
}
```

### 2.4 `GET /person/search` — fuzzy lookup

Lightweight finder — use it to resolve a name or identifier to a UUID, then call `/person` for full details.

```
GET /api/v1/person/search?name=jane%20angel
GET /api/v1/person/search?id=<uuid>
GET /api/v1/person/search?linkedin=https://linkedin.com/in/janeangel
GET /api/v1/person/search?crunchbase=https://crunchbase.com/person/jane-angel
GET /api/v1/person/search?twitter=https://x.com/janeangel
```

Exactly one parameter is required. `name=` returns up to ~10 fuzzy matches across both investor and non-investor pools (founders, employees). The other forms return 0 or 1 row.

The response is intentionally lightweight — just enough to disambiguate and follow up with `GET /person?id=...` for full detail.

```json
{
  "success": true,
  "data": {
    "people": [
      {
        "id": "b3e9c7d1-...",
        "name": "Jane Angel",
        "linkedin_url": "https://linkedin.com/in/janeangel",
        "crunchbase_url": "https://crunchbase.com/person/jane-angel",
        "twitter_url": "https://x.com/janeangel",
        "person_type": "investor"           // "investor" | "company"
      }
    ]
  },
  "meta": { "total_count": 1 }
}
```

`person_type` indicates which pool the row came from (`investor` wins when a person is in both). Mirrors the `person_type` discriminator on `POST /people`.

Error codes specific to this endpoint: `400 MISSING_SEARCH_PARAMS`, `400 MULTIPLE_SEARCH_PARAMS`, `400 INVALID_ID`.

---

## 3. Angel investor additions to existing routes

These are technically additive on the response (new fields only) but **semantically breaking** for any code that read `investor_ids` as "all investors" — see §1.3.

### 3.1 New filter: `investors.people_ids`

Both `POST /deals` and `POST /companies` accept a new array under their `investors` filter block:

```json
{
  "investors": {
    "people_ids": ["b3e9c7d1-2f4a-4d5e-9c1b-7a8f3e2d1c6a"]
  }
}
```

Matches deals/companies where any of these people participated **either** as an angel investor **or** as a lead partner of an investing firm.

### 3.2 New required field: `angel_investor_ids`

**`Deal` (POST /deals) — before**
```json
{
  "id": "...", "company_id": "...",
  "investor_ids": ["c5a3f6ac-...", "b3e9c7d1-..."],
  "financings": [ ... ]
}
```

**`Deal` — after**
```json
{
  "id": "...", "company_id": "...",
  "investor_ids":       ["c5a3f6ac-..."],            // firms only
  "angel_investor_ids": ["b3e9c7d1-..."],            // required, [] if none
  "financings": [ ... ]
}
```

**`CompanyDeal` (POST /companies, GET /company/deals) — after**
```json
{
  "id": "...", "company_id": "...",
  "investor_ids":       ["c5a3f6ac-..."],
  "angel_investor_ids": ["b3e9c7d1-..."],
  "financings": [ ... ]
}
```
`required: [id, company_id, investor_ids, angel_investor_ids, financings]`.

**`LatestDeal` (nested on Company)** — same addition. `angel_investor_ids` is `[]` when no angels participated in the company's most recent round.

**`InvestorDeal` (GET /investor/deals)** — same addition. `angel_investor_ids` is required.

---

## 4. Minor / quality-of-life

### 4.1 `page_size` cap raised 100 → 500

Affects: `POST /deals`, `POST /companies`, `POST /investors`, `GET /company/deals`, `GET /investor/deals`, all `/people` and `/person/*` endpoints. Default still 10. No action required; raise as needed.

### 4.2 Slug / URL handling

- **`GET /company/search`** — `domain` now accepts either a bare domain (`stripe.com`) or a full URL (`https://stripe.com`); URLs are auto-parsed to the domain. `linkedin` and `crunchbase` parameter descriptions were simplified — full URLs are still expected.
- **`GET /location/search`** — description now documents both `type` and the alias `location_type`. Values: `CITY`, `STATE`, `REGION`, `COUNTRY`. Examples: `?name=san francisco`, `?name=california&type=STATE`.
- **`GET /industry/search`** — description now documents both `type` and the alias `industry_type`. Values: `INDUSTRY`, `SUPER_CATEGORY`. Examples: `?name=artificial intelligence`, `?name=fintech&type=INDUSTRY`.
- **`GET /investor/search`, `GET /investor`, `GET /investor/deals`** — `linkedin` and `crunchbase` parameter descriptions were simplified; full URLs are still expected.

No behavioral change beyond `/company/search` accepting URLs in `domain`.

### 4.3 `POST /investors` — request body fully expanded

`InvestorsPostBody` is now expanded inline in the spec. Sections:
- `identifiers` — `ids`, `domains`, `linkedin_urls`, `crunchbase_urls`, `permalinks` (max 100 each)
- `investor` — investor-attribute filters (locations, employee counts, ...)
- `company_investments` — portfolio filters: `financing_types[]` (object form: `{type, pre?, extension?}`), `deal_size_min`, `deal_size_max`, `deal_start_date`, `deal_end_date`, `only_lead_deals`, `min_matching_deals`
- `page`, `page_size` (max 500), `sort_by`

This is a **docs fidelity** upgrade — these filters were already supported. The endpoint description also clarifies that the response includes per-investor `filtered_deal_count` and `filtered_lead_count` when filters are applied.

### 4.4 Server host

Already covered in §1.4. Single-line summary:

```diff
- https://tryfundable.ai/api/v1
+ https://www.tryfundable.ai/api/v1
```

---

## 5. What did NOT change

Reassurance list — your existing code in these areas is fine:

- **Auth.** `Authorization: Bearer vg_<your_key>` on every request.
- **Error envelope.** `{ success: false, error: { code, message, details } }`.
- **Date formats.** `YYYY-MM-DD` for deals/companies/investors/people; `YYYY-MM-DDTHH:MM:SS.sssZ` for alerts.
- **Currency.** Actual USD (not millions). Filter params (`size_min`, `total_raised_min`, ...) and response amounts (`size_usd`, `valuation_usd`, `total_round_raised`, `latest_deal_size`) all in actual USD.
- **Financing-type object structure.** `{ "type": "SEED", "pre": true, "extension": false }` — `type` required, `pre`/`extension` optional booleans.
- **Pagination envelope.** `meta.total_count`, `meta.page`, `meta.page_size`, `meta.credits_used`, `meta.credit_source`, `meta.monthly_credits_remaining`, `meta.purchased_credits_remaining`.
- **422 strict validation.** Unknown parameters still reject with `422 UNKNOWN_PARAMETER`.
- **`format_usd()` and other helpers** in the example client library.

---

## 6. Migration checklist

Copy-paste into your tracker:

- [ ] Update API base URL to `https://www.tryfundable.ai/api/v1`.
- [ ] **`GET /deals/{id}/investors`** — read both `data.investors` and `data.angel_investors`. Drop any reads of `investor.angel_investor`.
- [ ] **`DealInvestor.personnel`** — switch from `string[]` to `PersonnelMember[]` (`{id, name, linkedin, crunchbase, twitter}`). Update display logic.
- [ ] **`Deal` / `CompanyDeal` / `LatestDeal` / `InvestorDeal`** — read the new `angel_investor_ids` field. Decide whether legacy "all investors" displays should union `investor_ids` + `angel_investor_ids`.
- [ ] (Optional) Raise `page_size` to take advantage of the new 500 cap on bulk pulls.
- [ ] (Optional) Onboard to the People API where useful — founder lookups (`POST /people` with `person.roles=["founder"]`), angel resolution (`GET /person?id=<angel_investor_id>`), partner attribution from `personnel[].id`.
- [ ] (Optional) Use the new `investors.people_ids` filter on `POST /deals` and `POST /companies` to slice by individual humans.

---

*Generated against `openapi/openapi-{alerts,companies,deals,investors,other,people}.yaml` vs `openapi_old/openapi-{alerts,companies,deals,investors,other}.yaml`. If a behavior here disagrees with the live spec, the live spec wins — please open an issue.*
