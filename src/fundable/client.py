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

    def get_investor(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed investor information by ID or permalink.
        
        Args:
            identifier: Investor UUID or permalink
            
        Returns:
            Investor details dict or None if not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/investor/{identifier}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                return data["data"]["investor"]
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching investor {identifier}: {e}")
            return None

    def get_deals(self,
                  # Pagination
                  page: int = None,
                  page_size: int = None,
                  # Sorting
                  sort_by: str = None,
                  # Date filters
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
                  # Deal filters
                  financing_types: List[str] = None,
                  deal_size_min: float = None,
                  deal_size_max: float = None,
                  # Investor filters
                  investor_ids: List[str] = None,
                  # Legacy support
                  start_date: str = None,
                  end_date: str = None,
                  **kwargs) -> List[Dict[str, Any]]:
        """
        Get deals with any combination of filters.

        All parameters are optional. Date strings should be in YYYY-MM-DD format.
        List parameters accept lists of strings that will be comma-separated.
        """
        # Handle legacy parameters
        if start_date and not deal_start_date:
            deal_start_date = start_date
        if end_date and not deal_end_date:
            deal_end_date = end_date

        # Set date defaults if not provided
        if not deal_end_date:
            deal_end_date = datetime.utcnow().strftime("%Y-%m-%d")
        if not deal_start_date:
            deal_start_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Build API parameters
        params = {}

        # Add pagination
        if page is not None:
            params['page'] = page
        if page_size is not None:
            params['pageSize'] = page_size
        else:
            params['pageSize'] = 100

        # Add sorting
        if sort_by:
            params['sortBy'] = sort_by
        else:
            params['sortBy'] = 'Most Recent'

        # Add date filters
        if deal_start_date:
            params['dealStartDate'] = f"{deal_start_date}T00:00:00Z"
        if deal_end_date:
            params['dealEndDate'] = f"{deal_end_date}T23:59:59Z"
        if company_founded_start:
            params['companyFoundedStart'] = f"{company_founded_start}T00:00:00Z"
        if company_founded_end:
            params['companyFoundedEnd'] = f"{company_founded_end}T23:59:59Z"

        # Add list filters (convert lists to comma-separated strings)
        if company_ids:
            params['companyIds'] = ','.join(company_ids)
        if industries:
            params['industries'] = ','.join(industries)
        if super_categories:
            params['superCategories'] = ','.join(super_categories)
        if locations:
            params['locations'] = ','.join(locations)
        if employee_count:
            params['employeeCount'] = ','.join(employee_count)
        if ipo_status:
            params['ipoStatus'] = ','.join(ipo_status)
        if financing_types:
            params['financingTypes'] = ','.join(financing_types)
        if investor_ids:
            params['investorIds'] = ','.join(investor_ids)

        # Add numeric filters
        if deal_size_min is not None:
            params['dealSizeMin'] = deal_size_min
        if deal_size_max is not None:
            params['dealSizeMax'] = deal_size_max

        # Make single API request
        try:
            response = requests.get(f"{self.base_url}/deals", headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data["data"]["deals"]
            else:
                return []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching deals: {e}")
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
            'alertIds': ','.join(alert_ids),
            'startDate': start_date,
            'endDate': end_date
        }

        try:
            response = requests.get(
                f"{self.base_url}/alerts/",
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data["data"]
            return {"alerts": [], "totalDealCount": 0}

        except requests.exceptions.RequestException as e:
            print(f"Error fetching alerts: {e}")
            return {"alerts": [], "totalDealCount": 0}

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
            response.raise_for_status()
            data = response.json()

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
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data["data"]["company"]
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching company {identifier}: {e}")
            return None


class DataExtractor:
    """Simple class to extract useful information from deal data."""

    @staticmethod
    def extract_deal(deal: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information from a deal."""
        # Basic info
        extracted = {
            'deal_id': deal.get('id', ''),
            'company_name': deal.get('company', {}).get('name', 'Unknown'),
            'round_type': deal.get('round_type', 'Unknown'),
            'deal_date': deal.get('date', ''),
            'deal_amount': f"${deal.get('total_round_raised')}M" if deal.get('total_round_raised') else 'Undisclosed'
        }

        # Company info
        company = deal.get('company', {}) or {}
        extracted['company_domain'] = company.get('domain', '')
        extracted['company_location'] = DataExtractor._extract_location(company.get('location', {}))

        # Description
        descriptions = deal.get('deal_descriptions', {}) or {}
        long_desc = descriptions.get('long_description', '')
        short_desc = descriptions.get('short_description', '')
        extracted['description'] = long_desc or short_desc or 'No description'

        # Articles
        articles = deal.get('articles', [])
        extracted['article_urls'] = [article['link'] for article in articles]

        # Investors
        investors = DataExtractor._extract_investors(deal.get('deal_investors', []))
        extracted.update(investors)

        return extracted

    @staticmethod
    def _extract_location(location: Dict[str, Any]) -> str:
        """Extract location string."""
        if not location:
            return 'Unknown'

        parts = []
        for loc_type in ['city', 'state', 'country']:
            loc_data = location.get(loc_type, {})
            if loc_data and loc_data.get('name'):
                parts.append(loc_data['name'])

        return ', '.join(parts) if parts else 'Unknown'

    @staticmethod
    def _extract_investors(deal_investors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract investor information."""
        all_investors = []
        lead_investors = []

        for investor in deal_investors:
            name = investor.get('name', 'Unknown')
            is_lead = investor.get('lead_investor', False)

            all_investors.append(name)
            if is_lead:
                lead_investors.append(name)

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
            print(f"\n{i}. {deal['company_name']}")
            print(f"   💰 {deal['deal_amount']} ({deal['round_type']})")
            print(f"   📅 {deal['deal_date']}")
            print(f"   🌍 {deal['company_location']}")

            if deal['company_domain']:
                print(f"   🌐 {deal['company_domain']}")

            # Description (truncated)
            desc = deal['description']
            if len(desc) > 150:
                desc = desc[:150] + "..."
            print(f"   📝 {desc}")

            # Investors
            if deal['investors']:
                investors_str = ', '.join(deal['investors'][:3])
                if len(deal['investors']) > 3:
                    investors_str += f" (+{len(deal['investors'])-3} more)"
                print(f"   💼 {investors_str}")

                if deal['lead_investors']:
                    print(f"   🎯 Lead: {', '.join(deal['lead_investors'])}")

            # Articles
            if deal['article_urls']:
                print(f"   📰 {len(deal['article_urls'])} articles")