#!/usr/bin/env python3
"""
Simplified Fundable API client.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()


def format_usd(amount) -> str:
    """Format a dollar amount with commas. Returns 'Undisclosed' if None or 0."""
    if not amount:
        return 'Undisclosed'
    if isinstance(amount, (int, float)):
        if amount == int(amount):
            return f"${int(amount):,}"
        return f"${amount:,.2f}"
    return 'Undisclosed'


class FundableClient:
    """Simple client for fetching deals from Fundable API."""

    DEFAULT_BASE_URL = "https://www.tryfundable.ai/api/v1"

    def __init__(self, api_key: str = None, base_url: str = None):
        """Initialize client with API key and base URL."""
        self.api_key = api_key or os.getenv("FUNDABLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set FUNDABLE_API_KEY environment variable or pass api_key parameter.")

        self.base_url = base_url or os.getenv("FUNDABLE_API_URL", self.DEFAULT_BASE_URL)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _post(self, path: str, body: Dict[str, Any]) -> Any:
        """Make a POST request with a JSON body, returning the parsed response."""
        return requests.post(
            f"{self.base_url}{path}",
            headers=self.headers,
            json=body,
            timeout=30
        )

    def get_investor(self, identifier: str, identifier_type: str = 'id') -> Optional[Dict[str, Any]]:
        """
        Get detailed investor information by ID, permalink, domain, LinkedIn, or Crunchbase.

        Args:
            identifier: Investor UUID, permalink, domain, LinkedIn slug, or Crunchbase slug
            identifier_type: One of 'id', 'permalink', 'domain', 'linkedin', 'crunchbase', 'url'.
                Defaults to 'id'.

        Returns:
            Investor details dict or None if not found
        """
        valid_types = ['id', 'permalink', 'domain', 'linkedin', 'crunchbase', 'url']
        if identifier_type not in valid_types:
            raise ValueError(f"identifier_type must be one of: {valid_types}")

        params = {identifier_type: identifier}

        try:
            response = requests.get(
                f"{self.base_url}/investor",
                headers=self.headers,
                params=params,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching investor {identifier}: {error_msg}")
                return None

            if data.get("success"):
                return data["data"]["investor"]
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching investor {identifier}: {e}")
            return None

    def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed deal information by ID.

        Args:
            deal_id: Deal UUID

        Returns:
            Deal details dict or None if not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/deals/{deal_id}",
                headers=self.headers,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching deal {deal_id}: {error_msg}")
                return None

            if data.get("success"):
                return data["data"]["deal"]
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching deal {deal_id}: {e}")
            return None

    def get_deal_investors(self, deal_id: str) -> List[Dict[str, Any]]:
        """
        Get full investor details for a specific deal.

        Args:
            deal_id: Deal UUID

        Returns:
            List of DealInvestor dicts with name, lead_investor, domain, linkedin, crunchbase, etc.
        """
        try:
            response = requests.get(
                f"{self.base_url}/deals/{deal_id}/investors",
                headers=self.headers,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching investors for deal {deal_id}: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["investors"]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching investors for deal {deal_id}: {e}")
            return []

    def get_deals(self,
                  # Pagination
                  page: int = None,
                  page_size: int = None,
                  # Sorting
                  sort_by: str = None,
                  # Date filters
                  deal_start_date: str = None,
                  deal_end_date: str = None,
                  # Company filters
                  company_ids: List[str] = None,
                  industries: List[str] = None,
                  super_categories: List[str] = None,
                  locations: List[str] = None,
                  employee_count: List[str] = None,
                  ipo_status: List[str] = None,
                  total_raised_min: float = None,
                  total_raised_max: float = None,
                  # Deal filters
                  financing_types: List[Dict[str, Any]] = None,
                  deal_size_min: float = None,
                  deal_size_max: float = None,
                  # Investor filters
                  investor_ids: List[str] = None,
                  # Identifier lookup
                  deal_ids: List[str] = None,
                  # Legacy support
                  start_date: str = None,
                  end_date: str = None,
                  **kwargs) -> List[Dict[str, Any]]:
        """
        Get deals with any combination of filters. Sends a POST request with a JSON body.

        All parameters are optional. Date strings should be in YYYY-MM-DD format.
        """
        # Handle legacy parameters
        if start_date and not deal_start_date:
            deal_start_date = start_date
        if end_date and not deal_end_date:
            deal_end_date = end_date

        # No implicit date window: send exactly the filters the caller specified.
        # A date-less query is valid — the API returns most-recent deals, bounded by
        # page_size and sort_by (default 'most_recent_deal').

        # Build nested JSON body
        body = {}

        # Identifiers section
        identifiers = {}
        if deal_ids:
            identifiers['deal_ids'] = deal_ids
        if identifiers:
            body['identifiers'] = identifiers

        # Deal section
        deal_filters = {}
        if financing_types:
            deal_filters['financing_types'] = financing_types
        if deal_size_min is not None:
            deal_filters['size_min'] = deal_size_min
        if deal_size_max is not None:
            deal_filters['size_max'] = deal_size_max
        if deal_start_date:
            deal_filters['date_start'] = deal_start_date
        if deal_end_date:
            deal_filters['date_end'] = deal_end_date
        if deal_filters:
            body['deal'] = deal_filters

        # Company section
        company_filters = {}
        if locations:
            company_filters['locations'] = locations
        if industries:
            company_filters['industries'] = industries
        if super_categories:
            company_filters['super_categories'] = super_categories
        if employee_count:
            company_filters['employee_count'] = employee_count
        if ipo_status:
            company_filters['ipo_status'] = ipo_status
        if total_raised_min is not None:
            company_filters['total_raised_min'] = total_raised_min
        if total_raised_max is not None:
            company_filters['total_raised_max'] = total_raised_max
        if company_ids:
            company_filters['company_ids'] = company_ids
        if company_filters:
            body['company'] = company_filters

        # Investors section
        investors_filter = {}
        if investor_ids:
            investors_filter['investor_ids'] = investor_ids
        if investors_filter:
            body['investors'] = investors_filter

        # Pagination and sorting
        body['page_size'] = page_size if page_size is not None else 100
        if page is not None:
            body['page'] = page
        body['sort_by'] = sort_by if sort_by else 'most_recent_deal'

        try:
            response = self._post('/deals', body)
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching deals: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["deals"]
            else:
                return []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching deals: {e}")
            return []

    def get_companies(self,
                      # Pagination
                      page: int = None,
                      page_size: int = None,
                      # Sorting
                      sort_by: str = None,
                      # Semantic search
                      search_query: str = None,
                      min_relevance: float = None,
                      # Date filters (latest deal)
                      deal_start_date: str = None,
                      deal_end_date: str = None,
                      company_founded_start: str = None,
                      company_founded_end: str = None,
                      # Company filters
                      company_ids: List[str] = None,
                      industries: List[str] = None,
                      super_categories: List[str] = None,
                      locations: List[str] = None,
                      employee_count: List[str] = None,
                      ipo_status: List[str] = None,
                      total_raised_min: float = None,
                      total_raised_max: float = None,
                      # Deal filters (latest deal)
                      financing_types: List[Dict[str, Any]] = None,
                      deal_size_min: float = None,
                      deal_size_max: float = None,
                      # Investor filters (latest-deal scoped)
                      investor_ids: List[str] = None,
                      # Investor filters (any-round scoped — top-level `investors` block)
                      people_ids: List[str] = None,
                      any_round_investor_ids: List[str] = None,
                      # Batch identifier lookup
                      domains: List[str] = None,
                      linkedins: List[str] = None,
                      crunchbases: List[str] = None,
                      **kwargs) -> List[Dict[str, Any]]:
        """
        Get companies with any combination of filters. Sends a POST request with a JSON body.

        All parameters are optional. Date strings should be in YYYY-MM-DD format.

        Investor scoping:
        - `investor_ids` filters by firms participating in the company's *latest* round
          (lands under `latest_deal.investor_ids`).
        - `people_ids` filters by people (angels OR firm lead partners) who participated
          in *any* round of the company (lands under `investors.people_ids`).
        - `any_round_investor_ids` filters by firm UUIDs across any round
          (lands under `investors.investor_ids`).
        """
        has_batch_filter = domains or linkedins or crunchbases or company_ids
        # Free-form thesis search and per-person portfolio lookups should not be silently
        # narrowed to a 1-day window — treat them like batch lookups for date defaulting.
        skip_date_default = has_batch_filter or search_query or people_ids or any_round_investor_ids

        # Set date defaults if not provided (skip for batch lookups / thesis searches)
        if not skip_date_default:
            if not deal_end_date:
                deal_end_date = datetime.utcnow().strftime("%Y-%m-%d")
            if not deal_start_date:
                deal_start_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Build nested JSON body
        body = {}

        # Identifiers section
        identifiers = {}
        if company_ids:
            identifiers['ids'] = company_ids
        if domains:
            identifiers['domains'] = domains
        if linkedins:
            identifiers['linkedin_urls'] = linkedins
        if crunchbases:
            identifiers['crunchbase_urls'] = crunchbases
        if identifiers:
            body['identifiers'] = identifiers

        # Company section
        company_filters = {}
        if search_query:
            company_filters['search_query'] = search_query
        if min_relevance is not None:
            company_filters['min_relevance'] = min_relevance
        if locations:
            company_filters['locations'] = locations
        if industries:
            company_filters['industries'] = industries
        if super_categories:
            company_filters['super_categories'] = super_categories
        if employee_count:
            company_filters['employee_count'] = employee_count
        if ipo_status:
            company_filters['ipo_status'] = ipo_status
        if total_raised_min is not None:
            company_filters['total_raised_min'] = total_raised_min
        if total_raised_max is not None:
            company_filters['total_raised_max'] = total_raised_max
        if company_founded_start:
            company_filters['founded_start'] = company_founded_start
        if company_founded_end:
            company_filters['founded_end'] = company_founded_end
        if company_filters:
            body['company'] = company_filters

        # Latest deal section
        latest_deal_filters = {}
        if financing_types:
            latest_deal_filters['financing_types'] = financing_types
        if deal_size_min is not None:
            latest_deal_filters['size_min'] = deal_size_min
        if deal_size_max is not None:
            latest_deal_filters['size_max'] = deal_size_max
        if deal_start_date:
            latest_deal_filters['date_start'] = deal_start_date
        if deal_end_date:
            latest_deal_filters['date_end'] = deal_end_date
        if investor_ids:
            latest_deal_filters['investor_ids'] = investor_ids
        if latest_deal_filters:
            body['latest_deal'] = latest_deal_filters

        # Investors section (any-round scope)
        investors_block = {}
        if people_ids:
            investors_block['people_ids'] = people_ids
        if any_round_investor_ids:
            investors_block['investor_ids'] = any_round_investor_ids
        if investors_block:
            body['investors'] = investors_block

        # Pagination and sorting
        body['page_size'] = page_size if page_size is not None else 100
        if page is not None:
            body['page'] = page
        if sort_by:
            body['sort_by'] = sort_by
        elif not has_batch_filter:
            body['sort_by'] = 'most_recent_raise'

        try:
            response = self._post('/companies', body)
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching companies: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["companies"]
            else:
                return []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching companies: {e}")
            return []

    def get_investors(self,
                      # Pagination
                      page: int = None,
                      page_size: int = None,
                      # Sorting
                      sort_by: str = None,
                      # Investor filters
                      investor_locations: List[str] = None,
                      investor_employee_count: List[str] = None,
                      investor_domains: List[str] = None,
                      investor_linkedins: List[str] = None,
                      investor_crunchbases: List[str] = None,
                      investor_ids: List[str] = None,
                      # Portfolio filters - company attributes
                      industries: List[str] = None,
                      super_categories: List[str] = None,
                      locations: List[str] = None,
                      employee_count: List[str] = None,
                      ipo_status: List[str] = None,
                      # Portfolio filters - deal attributes
                      deal_size_min: float = None,
                      deal_size_max: float = None,
                      deal_start_date: str = None,
                      deal_end_date: str = None,
                      financing_types: List[Dict[str, Any]] = None,
                      # Portfolio filters - company identifiers
                      company_ids: List[str] = None,
                      # Portfolio filters - thresholds
                      min_matching_deals: int = None,
                      only_lead_deals: bool = None,
                      **kwargs) -> List[Dict[str, Any]]:
        """
        Get investors with any combination of filters. Sends a POST request with a JSON body.

        Filters are split into two categories:
        - Investor Filters: filter on the investor entity itself (location, size, domain)
        - Portfolio Filters (company_investments): filter by the companies they've invested in

        All parameters are optional. Date strings should be in YYYY-MM-DD format.
        """
        has_batch_filter = investor_domains or investor_linkedins or investor_crunchbases

        # Build nested JSON body
        body = {}

        # Identifiers section (investor batch lookup)
        identifiers = {}
        if investor_ids:
            identifiers['ids'] = investor_ids
        if investor_domains:
            identifiers['domains'] = investor_domains
        if investor_linkedins:
            identifiers['linkedin_urls'] = investor_linkedins
        if investor_crunchbases:
            identifiers['crunchbase_urls'] = investor_crunchbases
        if identifiers:
            body['identifiers'] = identifiers

        # Investor section
        investor_filters = {}
        if investor_locations:
            investor_filters['locations'] = investor_locations
        if investor_employee_count:
            investor_filters['employee_count'] = investor_employee_count
        if investor_filters:
            body['investor'] = investor_filters

        # Company investments section (portfolio filters)
        portfolio_filters = {}
        if deal_size_min is not None:
            portfolio_filters['deal_size_min'] = deal_size_min
        if deal_size_max is not None:
            portfolio_filters['deal_size_max'] = deal_size_max
        if deal_start_date:
            portfolio_filters['deal_start_date'] = deal_start_date
        if deal_end_date:
            portfolio_filters['deal_end_date'] = deal_end_date
        if financing_types:
            portfolio_filters['financing_types'] = financing_types
        if locations:
            portfolio_filters['locations'] = locations
        if industries:
            portfolio_filters['industries'] = industries
        if super_categories:
            portfolio_filters['super_categories'] = super_categories
        if employee_count:
            portfolio_filters['employee_count'] = employee_count
        if ipo_status:
            portfolio_filters['ipo_status'] = ipo_status
        if company_ids:
            portfolio_filters['company_ids'] = company_ids
        if min_matching_deals is not None:
            portfolio_filters['min_matching_deals'] = min_matching_deals
        if only_lead_deals is not None:
            portfolio_filters['only_lead_deals'] = only_lead_deals
        if portfolio_filters:
            body['company_investments'] = portfolio_filters

        # Pagination and sorting
        body['page_size'] = page_size if page_size is not None else 100
        if page is not None:
            body['page'] = page
        if sort_by:
            body['sort_by'] = sort_by
        elif not has_batch_filter:
            body['sort_by'] = 'most_recent_deal'

        try:
            response = self._post('/investors', body)
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching investors: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["investors"]
            else:
                return []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching investors: {e}")
            return []

    def get_alerts(self, alert_ids: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get alert data with deals for specified alert IDs and date range.

        Args:
            alert_ids: List of alert UUIDs (up to 10)
            start_date: Start date in ISO 8601 format (e.g., "2024-01-01T00:00:00.000Z")
            end_date: End date in ISO 8601 format (e.g., "2024-12-31T23:59:59.999Z")

        Returns:
            Dict with 'alerts' array containing alert data and deals
        """
        params = {
            'alert_ids': ','.join(alert_ids),
            'start_date': start_date,
            'end_date': end_date
        }

        try:
            response = requests.get(
                f"{self.base_url}/alerts/",
                headers=self.headers,
                params=params,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching alerts: {error_msg}")
                return {"alerts": [], "total_count": 0}

            if data.get("success"):
                return data["data"]
            return {"alerts": [], "total_count": 0}

        except requests.exceptions.RequestException as e:
            print(f"Error fetching alerts: {e}")
            return {"alerts": [], "total_count": 0}

    def get_alert_configurations(self) -> List[Dict[str, Any]]:
        """
        Get all alert configurations for the authenticated user.

        Returns:
            List of alert configuration dicts
        """
        try:
            response = requests.get(
                f"{self.base_url}/alerts/configurations",
                headers=self.headers,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching alert configurations: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["configurations"]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching alert configurations: {e}")
            return []

    def get_company(self, identifier: str, identifier_type: str = 'id') -> Optional[Dict[str, Any]]:
        """
        Get company details by various identifier types.

        Args:
            identifier: The company identifier value
            identifier_type: One of 'id', 'permalink', 'domain', 'url', 'linkedin', 'crunchbase'

        Returns:
            Company details dict or None if not found
        """
        valid_types = ['id', 'permalink', 'domain', 'url', 'linkedin', 'crunchbase']
        if identifier_type not in valid_types:
            raise ValueError(f"identifier_type must be one of: {valid_types}")

        params = {identifier_type: identifier}

        try:
            response = requests.get(
                f"{self.base_url}/company",
                headers=self.headers,
                params=params,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching company {identifier}: {error_msg}")
                return None

            if data.get("success"):
                return data["data"]["company"]
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching company {identifier}: {e}")
            return None

    def get_company_deals(self, id: str = None, domain: str = None,
                          linkedin: str = None, crunchbase: str = None,
                          page: int = None, page_size: int = None) -> Dict[str, Any]:
        """
        Get all deals for a company by ID, domain, LinkedIn URL, or Crunchbase URL.

        Exactly one identifier must be provided.

        Args:
            id: Company UUID
            domain: Company domain (e.g., "stripe.com")
            linkedin: LinkedIn company URL (e.g., "https://linkedin.com/company/stripe")
            crunchbase: Crunchbase organization URL (e.g., "https://crunchbase.com/organization/stripe")
            page: Page number (0-based)
            page_size: Results per page (1-100, default 10)

        Returns:
            Dict with 'deals' list and 'meta' dict (total_count, page, page_size)
        """
        provided = {k: v for k, v in {'id': id, 'domain': domain, 'linkedin': linkedin,
                                       'crunchbase': crunchbase}.items() if v}
        if len(provided) != 1:
            raise ValueError("Exactly one of id, domain, linkedin, or crunchbase must be provided")

        params = dict(provided)
        if page is not None:
            params['page'] = page
        if page_size is not None:
            params['page_size'] = page_size

        try:
            response = requests.get(
                f"{self.base_url}/company/deals",
                headers=self.headers,
                params=params,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching company deals: {error_msg}")
                return {"deals": [], "meta": {"total_count": 0}}

            if data.get("success"):
                return {"deals": data["data"]["deals"], "meta": data.get("meta", {})}
            return {"deals": [], "meta": {"total_count": 0}}

        except requests.exceptions.RequestException as e:
            print(f"Error fetching company deals: {e}")
            return {"deals": [], "meta": {"total_count": 0}}

    def search_companies(self, name: str = None, domain: str = None,
                         linkedin: str = None, crunchbase: str = None) -> List[Dict[str, Any]]:
        """
        Search companies by name, domain, LinkedIn URL, or Crunchbase URL.

        Exactly one parameter must be provided.

        Args:
            name: Search by company name (fuzzy match)
            domain: Search by company domain (exact match)
            linkedin: Search by LinkedIn company URL
            crunchbase: Search by Crunchbase organization URL

        Returns:
            List of matching company dicts with relevance scores
        """
        provided = {k: v for k, v in {'name': name, 'domain': domain,
                                       'linkedin': linkedin, 'crunchbase': crunchbase}.items() if v}
        if len(provided) != 1:
            raise ValueError("Exactly one of name, domain, linkedin, or crunchbase must be provided")

        try:
            response = requests.get(
                f"{self.base_url}/company/search",
                headers=self.headers,
                params=provided,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error searching companies: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["companies"]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error searching companies: {e}")
            return []

    def get_investor_deals(self, domain: str = None, linkedin: str = None,
                           crunchbase: str = None, page: int = None,
                           page_size: int = None) -> Dict[str, Any]:
        """
        Get all deals for an investor by domain, LinkedIn URL, or Crunchbase URL.

        Exactly one identifier must be provided.

        Args:
            domain: Investor domain (e.g., "sequoiacap.com")
            linkedin: LinkedIn company URL (e.g., "https://linkedin.com/company/sequoia-capital")
            crunchbase: Crunchbase organization URL (e.g., "https://crunchbase.com/organization/sequoia-capital")
            page: Page number (0-based)
            page_size: Results per page (1-100, default 10)

        Returns:
            Dict with 'deals' list and 'meta' dict (total_count, page, page_size)
        """
        provided = {k: v for k, v in {'domain': domain, 'linkedin': linkedin,
                                       'crunchbase': crunchbase}.items() if v}
        if len(provided) != 1:
            raise ValueError("Exactly one of domain, linkedin, or crunchbase must be provided")

        params = dict(provided)
        if page is not None:
            params['page'] = page
        if page_size is not None:
            params['page_size'] = page_size

        try:
            response = requests.get(
                f"{self.base_url}/investor/deals",
                headers=self.headers,
                params=params,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching investor deals: {error_msg}")
                return {"deals": [], "meta": {"total_count": 0}}

            if data.get("success"):
                return {"deals": data["data"]["deals"], "meta": data.get("meta", {})}
            return {"deals": [], "meta": {"total_count": 0}}

        except requests.exceptions.RequestException as e:
            print(f"Error fetching investor deals: {e}")
            return {"deals": [], "meta": {"total_count": 0}}

    def search_investors(self, name: str = None, domain: str = None,
                         linkedin: str = None, crunchbase: str = None) -> List[Dict[str, Any]]:
        """
        Search investors by name, domain, LinkedIn URL, or Crunchbase URL.

        Exactly one parameter must be provided.

        Args:
            name: Search by investor name (fuzzy match)
            domain: Search by investor domain (exact match)
            linkedin: Search by LinkedIn company URL
            crunchbase: Search by Crunchbase organization URL

        Returns:
            List of matching investor dicts with relevance scores
        """
        provided = {k: v for k, v in {'name': name, 'domain': domain,
                                       'linkedin': linkedin, 'crunchbase': crunchbase}.items() if v}
        if len(provided) != 1:
            raise ValueError("Exactly one of name, domain, linkedin, or crunchbase must be provided")

        try:
            response = requests.get(
                f"{self.base_url}/investor/search",
                headers=self.headers,
                params=provided,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error searching investors: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["investors"]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error searching investors: {e}")
            return []

    def search_industries(self, name: str, type: str = None) -> List[Dict[str, Any]]:
        """
        Search industries and super categories by name with fuzzy matching.

        Args:
            name: Search query for industry name
            type: Optional filter — 'INDUSTRY' or 'SUPER_CATEGORY'

        Returns:
            List of matching industry dicts with permalink and industry_type
        """
        if type is not None:
            valid_types = ['INDUSTRY', 'SUPER_CATEGORY']
            if type not in valid_types:
                raise ValueError(f"type must be one of: {valid_types}")

        params = {'name': name}
        if type:
            params['type'] = type

        try:
            response = requests.get(
                f"{self.base_url}/industry/search",
                headers=self.headers,
                params=params,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error searching industries: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["industries"]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error searching industries: {e}")
            return []

    def search_locations(self, name: str, type: str = None) -> List[Dict[str, Any]]:
        """
        Search locations by name with fuzzy matching.

        Args:
            name: Search query for location name
            type: Optional filter — 'CITY', 'STATE', 'REGION', or 'COUNTRY'

        Returns:
            List of matching location dicts with permalink and location_type
        """
        if type is not None:
            valid_types = ['CITY', 'STATE', 'REGION', 'COUNTRY']
            if type not in valid_types:
                raise ValueError(f"type must be one of: {valid_types}")

        params = {'name': name}
        if type:
            params['type'] = type

        try:
            response = requests.get(
                f"{self.base_url}/location/search",
                headers=self.headers,
                params=params,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error searching locations: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["locations"]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error searching locations: {e}")
            return []

    def _detect_person_identifier_type(self, identifier: str) -> str:
        """Auto-detect identifier type for /person endpoints. UUID -> 'id', URL -> linkedin/crunchbase/twitter."""
        import re
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', identifier, re.I):
            return 'id'
        lower = identifier.lower()
        if 'linkedin.com' in lower:
            return 'linkedin'
        if 'crunchbase.com' in lower:
            return 'crunchbase'
        if 'twitter.com' in lower or 'x.com' in lower:
            return 'twitter'
        raise ValueError(f"Could not auto-detect identifier type for {identifier!r}. Pass identifier_type explicitly.")

    def search_people(self,
                      person_type: str = None,
                      identifiers: Dict[str, Any] = None,
                      person: Dict[str, Any] = None,
                      company: Dict[str, Any] = None,
                      investor: Dict[str, Any] = None,
                      page: int = None,
                      page_size: int = None,
                      sort_by: str = None) -> List[Dict[str, Any]]:
        """
        Search people via POST /people with cross-type filters.

        Each filter section (`identifiers`, `person`, `company`, `investor`) is passed
        through as-is. Setting any field under `company.*` implicitly requires a current
        employer; any field under `investor.*` implicitly requires the person to be an
        investor. See openapi/openapi-people.yaml for the full schema.

        Args:
            person_type: 'company', 'investor', or 'any' (default 'any')
            identifiers: dict with optional ids / linkedin_urls / crunchbase_urls / twitter_urls
            person: person attribute filters (roles, contact_types, job_titles, ...)
            company: current-employer filters (incl. nested `latest_deal`)
            investor: investor-firm + deal-activity filters (incl. nested `deals`)
            page, page_size, sort_by: pagination + sort

        Returns:
            List of person result dicts (data.people).
        """
        body: Dict[str, Any] = {}
        if person_type:
            body['person_type'] = person_type
        if identifiers:
            body['identifiers'] = identifiers
        if person:
            body['person'] = person
        if company:
            body['company'] = company
        if investor:
            body['investor'] = investor
        if page is not None:
            body['page'] = page
        if page_size is not None:
            body['page_size'] = page_size
        if sort_by:
            body['sort_by'] = sort_by

        try:
            response = self._post('/people', body)
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error searching people: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["people"]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error searching people: {e}")
            return []

    def get_person(self, identifier: str, identifier_type: str = None) -> Optional[Dict[str, Any]]:
        """
        Get full person detail via GET /person.

        Args:
            identifier: Person UUID or LinkedIn / Crunchbase / Twitter URL
            identifier_type: One of 'id', 'linkedin', 'crunchbase', 'twitter'.
                If None, auto-detects from `identifier`.

        Returns:
            Person detail dict or None if not found.
        """
        if identifier_type is None:
            identifier_type = self._detect_person_identifier_type(identifier)

        valid_types = ['id', 'linkedin', 'crunchbase', 'twitter']
        if identifier_type not in valid_types:
            raise ValueError(f"identifier_type must be one of: {valid_types}")

        try:
            response = requests.get(
                f"{self.base_url}/person",
                headers=self.headers,
                params={identifier_type: identifier},
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching person {identifier}: {error_msg}")
                return None

            if data.get("success"):
                return data["data"]["person"]
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching person {identifier}: {e}")
            return None

    def get_person_deals(self, identifier: str, identifier_type: str = None,
                         page: int = 0, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Get the deals a person participated in as an investor (angel + lead/firm) via GET /person/deals.

        Args:
            identifier: Person UUID or LinkedIn / Crunchbase / Twitter URL
            identifier_type: 'id', 'linkedin', 'crunchbase', or 'twitter' (auto-detected if None)
            page, page_size: pagination

        Returns:
            List of deal dicts (data.deals).
        """
        if identifier_type is None:
            identifier_type = self._detect_person_identifier_type(identifier)

        valid_types = ['id', 'linkedin', 'crunchbase', 'twitter']
        if identifier_type not in valid_types:
            raise ValueError(f"identifier_type must be one of: {valid_types}")

        params = {identifier_type: identifier, 'page': page, 'page_size': page_size}

        try:
            response = requests.get(
                f"{self.base_url}/person/deals",
                headers=self.headers,
                params=params,
                timeout=30
            )
            data = response.json()

            if not response.ok:
                error_msg = data.get('error', {}).get('message', response.reason)
                print(f"Error fetching deals for person {identifier}: {error_msg}")
                return []

            if data.get("success"):
                return data["data"]["deals"]
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching deals for person {identifier}: {e}")
            return []


class DataExtractor:
    """Simple class to extract useful information from deal data."""

    @staticmethod
    def extract_deal(deal: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information from a deal.

        Note: In API v2 the deal response no longer includes inline company or investor
        objects. Use get_company(deal['company_id']) or get_deal_investors(deal['id'])
        to fetch those details separately.
        """
        # Basic info
        extracted = {
            'deal_id': deal.get('id', ''),
            'company_id': deal.get('company_id', ''),
            'round_type': deal.get('round_type', 'Unknown'),
            'deal_date': deal.get('date', ''),
            'deal_amount': format_usd(deal.get('total_round_raised'))
        }

        # Description
        descriptions = deal.get('deal_descriptions', {}) or {}
        long_desc = descriptions.get('long_description', '')
        short_desc = descriptions.get('short_description', '')
        extracted['description'] = long_desc or short_desc or 'No description'

        # Valuation (single nullable object in v2)
        valuation = deal.get('valuation')
        if valuation:
            extracted['valuation'] = valuation.get('valuation_usd')
        else:
            extracted['valuation'] = None

        # Investor IDs (full objects require get_deal_investors())
        investor_ids = deal.get('investor_ids', [])
        extracted['investor_ids'] = investor_ids
        extracted['investor_count'] = len(investor_ids)

        return extracted

    @staticmethod
    def _extract_investors(investors: List[Any]) -> Dict[str, Any]:
        """Extract investor information from a list of DealInvestor dicts or investor ID strings."""
        all_investors = []
        lead_investors = []

        for investor in investors:
            if isinstance(investor, dict):
                # Full DealInvestor object (from get_deal_investors())
                name = investor.get('name', 'Unknown')
                is_lead = investor.get('lead_investor', False)
                all_investors.append(name)
                if is_lead:
                    lead_investors.append(name)
            else:
                # Plain investor ID string (from deal['investor_ids'])
                all_investors.append(str(investor))

        return {
            'investors': all_investors,
            'lead_investors': lead_investors,
            'investor_count': len(all_investors)
        }

    @staticmethod
    def print_deals(deals: List[Dict[str, Any]], title: str = "Deals"):
        """Print deals in a nice format."""
        print(f"\n🚀 {title} ({len(deals)} deals)")
        print("=" * 60)

        for i, deal in enumerate(deals, 1):
            print(f"\n{i}. Company ID: {deal['company_id']}")
            print(f"   💰 {deal['deal_amount']} ({deal['round_type']})")
            print(f"   📅 {deal['deal_date']}")

            # Description (truncated)
            desc = deal['description']
            if len(desc) > 150:
                desc = desc[:150] + "..."
            print(f"   📝 {desc}")

            # Investors (IDs or names depending on enrichment)
            if deal.get('investors'):
                investors_str = ', '.join(str(i) for i in deal['investors'][:3])
                if len(deal['investors']) > 3:
                    investors_str += f" (+{len(deal['investors'])-3} more)"
                print(f"   💼 {investors_str}")

                if deal.get('lead_investors'):
                    print(f"   🎯 Lead: {', '.join(deal['lead_investors'])}")
            elif deal.get('investor_ids'):
                print(f"   💼 {len(deal['investor_ids'])} investor(s) — call get_deal_investors() for details")
