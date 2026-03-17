"""Fundable API Client - Python client and visualization tools.

This package provides a simple Python client for the Fundable API,
along with tools for creating visualizations.

Basic usage:
    >>> from fundable import FundableClient
    >>> client = FundableClient()
    >>> deals = client.get_deals(financing_types=['SEED'])
"""

__version__ = "0.1.0"

from fundable.client import FundableClient, DataExtractor, format_usd
from fundable.visualization.charts import InvestorBarChart, IndustryChart

__all__ = [
    "FundableClient",
    "DataExtractor",
    "format_usd",
    "InvestorBarChart",
    "IndustryChart",
    "__version__",
]
