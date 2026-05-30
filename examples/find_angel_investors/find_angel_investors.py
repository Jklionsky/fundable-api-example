#!/usr/bin/env python3
"""
Example: Find people via POST /people, then enrich the top hits with full
profiles. The default scenario is angel-investor discovery for a thesis,
but the request body is fully editable — see PEOPLE_QUERY below for
alternative recipes (industry filters, lead-only, cross-type, batch lookup).

Workflow:
  1. POST /people with whatever filter combo PEOPLE_QUERY contains.
  2. For the top N hits, GET /person for the full profile.
  3. If PEOPLE_QUERY uses `investor.deals.search_query`, also run a
     follow-up POST /companies with the same thesis + each person_id to
     surface their on-thesis portfolio companies.
"""

import json
import os

from fundable import FundableClient, format_usd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

# ============================================================================
# Configure your query here. This dict is splatted into client.search_people
# as kwargs (person_type, identifiers, person, company, investor, page,
# page_size, sort_by). Edit freely.
# ============================================================================

PEOPLE_QUERY = {
    "person_type": "investor",
    "investor": {
        "deals": {
            "investment_type": "angel",
            "search_query": "sales and marketing tools",
            "min_relevance": 0.1,
            "min_matching_deals": 1,
        }
    },
    "page_size": 50,
}

# ----- Alternative scenarios — uncomment one to swap in -----

# # 1) Active angels with ≥2 fintech deals in the last 12 months (no semantic search).
# PEOPLE_QUERY = {
#     "person_type": "investor",
#     "investor": {
#         "deals": {
#             "investment_type": "angel",
#             "industries": ["fintech"],
#             "date_start": "2024-05-01",
#             "min_matching_deals": 2,
#         }
#     },
#     "page_size": 50,
#     "sort_by": "lead_deal_count_last_12_months",
# }

# # 2) Lead-only angels backing AI startups in San Francisco.
# PEOPLE_QUERY = {
#     "person_type": "investor",
#     "investor": {
#         "deals": {
#             "investment_type": "angel",
#             "only_lead_deals": True,
#             "industries": ["artificial-intelligence"],
#             "portfolio_locations": ["san-francisco-california"],
#         }
#     },
#     "page_size": 50,
# }

# # 3) Cross-type: founders at fintech companies who also angel-invested in AI infra.
# PEOPLE_QUERY = {
#     "person": {"roles": ["founder"]},
#     "company": {"industries": ["fintech"]},
#     "investor": {
#         "deals": {
#             "investment_type": "angel",
#             "search_query": "AI infrastructure",
#             "min_relevance": 0.1,
#             "min_matching_deals": 1,
#         }
#     },
#     "page_size": 50,
# }

# # 4) Batch lookup specific people by LinkedIn URL.
# PEOPLE_QUERY = {
#     "identifiers": {
#         "linkedin_urls": [
#             "https://linkedin.com/in/jane-doe-12345",
#             "https://linkedin.com/in/john-smith-67890",
#         ]
#     },
# }

TOP_N_TO_ENRICH = 3
STEP3_MIN_RELEVANCE = 0.1


def get_thesis(query):
    """Return the investor.deals.search_query if present, else None."""
    return (query.get("investor") or {}).get("deals", {}).get("search_query")


def query_slug(query):
    """Filename-friendly slug describing the query (thesis if present, else hash)."""
    thesis = get_thesis(query)
    if thesis:
        return thesis.lower().replace(' ', '_').replace('/', '_')
    return f"query_{abs(hash(json.dumps(query, sort_keys=True))) % 100000}"


def print_person_summary(idx, person):
    """One-line summary of a /people search hit (works for any query)."""
    name = person.get('name') or 'Unknown'
    title = person.get('title') or '—'
    cur = person.get('current_company') or {}
    firm = cur.get('name') or '—'
    matched = person.get('filtered_deal_count')
    highlights = person.get('investor_highlights') or {}
    total = highlights.get('total_deal_count', 0)
    leads = highlights.get('lead_deal_count', 0)
    is_angel = person.get('is_angel', False)
    has_led = person.get('has_led_deal', False)

    flags = []
    if is_angel:
        flags.append('angel')
    if has_led:
        flags.append('has-led')
    flag_str = f" [{', '.join(flags)}]" if flags else ''

    matched_str = f"{matched} matching" if matched is not None else 'n/a'
    print(f"  {idx}. {name} — {title} @ {firm}")
    print(f"     {matched_str} | {total} all-time | {leads} led{flag_str}")


def print_profile(person):
    """Detailed profile block from /person."""
    name = person.get('name') or 'Unknown'
    title = person.get('title') or '—'
    location = person.get('location') or '—'
    highlights = person.get('investor_highlights') or {}
    most_recent = (highlights.get('most_recent_deal_date') or '—')[:10]

    print(f"  Name:            {name}")
    print(f"  Title:           {title}")
    print(f"  Location:        {location}")
    print(f"  Most recent deal: {most_recent}")

    about = person.get('about')
    if about:
        snippet = about.strip().replace('\n', ' ')
        if len(snippet) > 240:
            snippet = snippet[:237] + '...'
        print(f"  About:           {snippet}")

    top_inds = highlights.get('top_industries') or []
    if top_inds:
        ind_str = ', '.join(f"{i.get('name')} ({i.get('count')})" for i in top_inds[:5])
        print(f"  Top industries:  {ind_str}")

    top_locs = highlights.get('top_locations') or []
    if top_locs:
        loc_str = ', '.join(f"{l.get('name')} ({l.get('count')})" for l in top_locs[:5])
        print(f"  Top locations:   {loc_str}")

    top_rounds = highlights.get('top_round_types') or []
    if top_rounds:
        rt_str = ', '.join(f"{r.get('type')} ({r.get('count')})" for r in top_rounds[:5])
        print(f"  Top round types: {rt_str}")

    firms = person.get('investment_firms') or []
    if firms:
        firm_str = ', '.join(f"{f.get('name')} ({f.get('deal_count', 0)} deals)" for f in firms[:3])
        print(f"  Firms:           {firm_str}")

    employment = person.get('employment_history') or []
    if employment:
        print(f"  Employment ({len(employment)} records):")
        for e in employment[:3]:
            t = e.get('title') or '—'
            c = e.get('company_name') or '—'
            cur = ' (current)' if e.get('is_current') else ''
            print(f"    - {t} @ {c}{cur}")

    education = person.get('education_history') or []
    if education:
        print(f"  Education ({len(education)} records):")
        for ed in education[:3]:
            s = ed.get('school_name') or '—'
            d = ed.get('degree') or ''
            print(f"    - {s}{f' — {d}' if d else ''}")


def print_on_thesis_company(company):
    """Print one on-thesis portfolio company row from /companies (with inline latest_deal)."""
    name = company.get('name') or 'Unknown'
    domain = company.get('domain') or '—'
    short = company.get('short_description') or ''
    latest = company.get('latest_deal') or {}
    date = (latest.get('date') or 'n/a')[:10]
    ftype = latest.get('type') or '—'
    size = format_usd(latest.get('size_usd'))
    rel = company.get('relevance_score')
    rel_str = f" | rel {rel:.2f}" if isinstance(rel, (int, float)) else ''
    print(f"    {name} ({domain}){rel_str}")
    print(f"      latest: {date} | {ftype:<14} | {size}")
    if short:
        snippet = short.strip().replace('\n', ' ')
        if len(snippet) > 110:
            snippet = snippet[:107] + '...'
        print(f"      {snippet}")


def main():
    client = FundableClient()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    thesis = get_thesis(PEOPLE_QUERY)
    slug = query_slug(PEOPLE_QUERY)

    # --- Step 1: Run the configured /people query ---
    print("=" * 70)
    print(f"STEP 1: POST /people")
    print("=" * 70)
    print("  Request body:")
    for line in json.dumps(PEOPLE_QUERY, indent=2).splitlines():
        print(f"    {line}")
    print()

    people = client.search_people(**PEOPLE_QUERY)
    print(f"  Found {len(people)} people\n")
    for i, p in enumerate(people, 1):
        print_person_summary(i, p)

    raw_path = os.path.join(OUTPUT_DIR, f'people_{slug}.json')
    with open(raw_path, 'w') as f:
        json.dump(people, f, indent=2, default=str)
    print(f"\n  Saved raw results -> {raw_path}")

    if not people:
        print("\nNo results — relax filters or rephrase the search_query.")
        return

    # --- Step 2: Enrich top N with /person + (optional) on-thesis portfolio ---
    print(f"\n{'=' * 70}")
    if thesis:
        print(f"STEP 2: Enrich top {min(TOP_N_TO_ENRICH, len(people))} with /person + on-thesis portfolio")
    else:
        print(f"STEP 2: Enrich top {min(TOP_N_TO_ENRICH, len(people))} with /person")
    print("=" * 70)

    for i, hit in enumerate(people[:TOP_N_TO_ENRICH], 1):
        person_id = hit.get('id')
        if not person_id:
            continue

        print(f"\n--- #{i}: {hit.get('name', 'Unknown')} ({person_id}) ---")

        profile = client.get_person(person_id, identifier_type='id')
        if profile:
            print("\n  [Profile]")
            print_profile(profile)
        else:
            print("  (profile fetch failed)")

        on_thesis = []
        if thesis:
            # Cross-filter: companies the person backed that semantically rank against the thesis.
            on_thesis = client.get_companies(
                search_query=thesis,
                min_relevance=STEP3_MIN_RELEVANCE,
                people_ids=[person_id],
                page_size=5,
            )
            print(f"\n  [On-thesis portfolio companies — {len(on_thesis)} match]")
            if on_thesis:
                for co in on_thesis:
                    print_on_thesis_company(co)
            else:
                print(f"    (no portfolio companies ranked against '{thesis}' for this person)")

        # Persist the enriched bundle
        out = {'search_hit': hit, 'profile': profile, 'on_thesis_companies': on_thesis}
        out_path = os.path.join(OUTPUT_DIR, f'profile_{slug}_{i}.json')
        with open(out_path, 'w') as f:
            json.dump(out, f, indent=2, default=str)
        print(f"\n  Saved -> {out_path}")

    print(f"\n{'=' * 70}")
    label = f"'{thesis}'" if thesis else "the configured query"
    print(f"Done. Found {len(people)} people for {label}; "
          f"enriched top {min(TOP_N_TO_ENRICH, len(people))}.")
    print("=" * 70)


if __name__ == "__main__":
    main()
