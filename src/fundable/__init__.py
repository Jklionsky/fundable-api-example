"""Fundable API Client - Investor analysis and visualization tools.

This package provides a simple Python client for the Fundable API,
along with tools for analyzing investor data and creating visualizations.

Basic usage:
    >>> from fundable import FundableClient, InvestorAnalyzer
    >>> client = FundableClient()
    >>> analyzer = InvestorAnalyzer(client)
    >>> results = analyzer.analyze_top_investors(top_n=15, financing_types=['SEED'])
"""

__version__ = "0.1.0"

from fundable.client import FundableClient, DataExtractor
from fundable.analyzers.investor import InvestorAnalyzer
from fundable.visualization.charts import InvestorBarChart, IndustryChart

__all__ = [
    "FundableClient",
    "DataExtractor",
    "InvestorAnalyzer",
    "InvestorBarChart",
    "IndustryChart",
    "__version__",
]
