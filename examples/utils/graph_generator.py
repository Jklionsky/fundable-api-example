#!/usr/bin/env python3
"""
Reusable graph generator with logo support for Fundable API visualizations.
"""

import os
import io
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image


class BaseGraphGenerator:
    """Base class for generating charts with logo support."""
    
    def __init__(self, cache_dir: str = ".logo_cache"):
        """
        Initialize the graph generator.
        
        Args:
            cache_dir: Directory to cache downloaded logos
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Default styling
        self.default_colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'success': '#06A77D',
            'neutral': '#5F6368'
        }
        
    def download_logo(self, url: str, timeout: int = 10) -> Optional[Image.Image]:
        """
        Download and cache a logo from URL.
        
        Args:
            url: URL of the logo image
            timeout: Request timeout in seconds
            
        Returns:
            PIL Image object or None if download fails
        """
        if not url:
            return None
            
        try:
            # Create cache filename from URL
            parsed = urlparse(url)
            filename = f"{parsed.netloc}_{parsed.path.replace('/', '_')}"
            cache_path = self.cache_dir / filename
            
            # Return cached image if exists
            if cache_path.exists():
                return Image.open(cache_path).convert('RGBA')
            
            # Download image
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Open and save to cache
            img = Image.open(io.BytesIO(response.content)).convert('RGBA')
            img.save(cache_path, 'PNG')
            
            return img
            
        except Exception as e:
            print(f"⚠️  Failed to download logo from {url}: {e}")
            return None
    
    def resize_logo(self, img: Image.Image, max_size: Tuple[int, int] = (60, 60)) -> Image.Image:
        """
        Resize logo maintaining aspect ratio.
        
        Args:
            img: PIL Image object
            max_size: Maximum (width, height) in pixels
            
        Returns:
            Resized PIL Image
        """
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return img
    
    def make_circular_logo(self, img: Image.Image) -> Image.Image:
        """
        Convert square logo to circular logo with transparent background.
        
        Args:
            img: PIL Image object (RGBA)
            
        Returns:
            Circular PIL Image with transparency
        """
        from PIL import ImageDraw
        
        # Create a square image
        size = min(img.size)
        img = img.crop(((img.width - size) // 2, (img.height - size) // 2,
                       (img.width + size) // 2, (img.height + size) // 2))
        
        # Create circular mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask
        result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        result.paste(img, (0, 0))
        result.putalpha(mask)
        
        return result
    
    def setup_plot_style(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Setup common plot styling.
        
        Args:
            figsize: Figure size (width, height) in inches
            
        Returns:
            Figure and axis objects
        """
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=figsize)
        
        # Clean up spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return fig, ax
    
    def save_or_show(self, output_path: Optional[str] = None, dpi: int = 300):
        """
        Save plot to file or display it.
        
        Args:
            output_path: Path to save the figure, or None to display
            dpi: Resolution for saved image
        """
        plt.tight_layout()
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
            print(f"📊 Chart saved to: {output_path}")
        else:
            plt.show()
        
        plt.close()


class InvestorBarChart(BaseGraphGenerator):
    """Generate bar charts for investor analysis with logo support."""
    
    def plot_top_investors(
        self,
        investors: List[Dict[str, Any]],
        title: str = "Top Investors by Deal Count",
        metric: str = "deal_count",
        show_logos: bool = True,
        logo_size: Tuple[int, int] = (40, 40),
        max_display: int = None,
        output_path: Optional[str] = None,
        color: str = None
    ):
        """
        Create a vertical bar chart of top investors with optional circular logos.
        
        Args:
            investors: List of investor dicts (from InvestorAnalyzer)
            title: Chart title
            metric: Field to plot (e.g., 'deal_count', 'total_investments')
            show_logos: Whether to display investor logos
            logo_size: Size for logos (width, height) in pixels
            max_display: Maximum number of investors to display
            output_path: Path to save chart, or None to display
            color: Bar color (hex), or None for default
        """
        if not investors:
            print("⚠️  No investor data to plot")
            return
        
        # Limit display if requested
        if max_display:
            investors = investors[:max_display]
        
        # Extract data (no reversal needed for vertical bars)
        names = [inv.get('name', 'Unknown') for inv in investors]
        values = [inv.get(metric, 0) for inv in investors]
        logos = [inv.get('image') for inv in investors] if show_logos else []
        
        # Create plot with adjusted size for vertical bars
        fig, ax = self.setup_plot_style(figsize=(max(12, len(names) * 0.8), 8))
        
        # Plot vertical bars
        bar_color = color or self.default_colors['primary']
        x_positions = range(len(names))
        bars = ax.bar(x_positions, values, color=bar_color, alpha=0.8, width=0.7)
        
        # Add value labels on top of bars
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + max(values) * 0.01,
                   f'{int(value)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add circular logos above bars if requested
        if show_logos and logos:
            self._add_logos_to_vertical_bars(ax, logos, x_positions, values, logo_size)
        
        # Styling
        ax.set_xticks(x_positions)
        ax.set_xticklabels(names, fontsize=10, rotation=45, ha='right')
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Add grid
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adjust layout to prevent label cutoff
        plt.subplots_adjust(bottom=0.2, top=0.85)
        
        # Save or show
        self.save_or_show(output_path)
    
    def _add_logos_to_vertical_bars(
        self,
        ax,
        logo_urls: List[str],
        x_positions: List[int],
        bar_heights: List[float],
        logo_size: Tuple[int, int]
    ):
        """
        Add circular logos above vertical bars.
        
        Args:
            ax: Matplotlib axis
            logo_urls: List of logo URLs
            x_positions: X-axis positions for each logo
            bar_heights: Heights of bars to position logos above them
            logo_size: Size for logos (width, height)
        """
        max_height = max(bar_heights) if bar_heights else 0
        
        for url, x_pos, height in zip(logo_urls, x_positions, bar_heights):
            if not url:
                continue
            
            # Download and resize logo
            img = self.download_logo(url)
            if img is None:
                continue
            
            # Resize and make circular
            img = self.resize_logo(img, logo_size)
            img = self.make_circular_logo(img)
            
            # Add logo to plot above the bar
            imagebox = OffsetImage(img, zoom=0.7)
            
            # Position logo above the bar (at ~110% of max height)
            y_offset = max_height * 1.15
            ab = AnnotationBbox(
                imagebox,
                (x_pos, y_offset),
                xycoords='data',
                frameon=False,
                box_alignment=(0.5, 0.5)
            )
            ax.add_artist(ab)
        
        # Adjust top margin to accommodate logos
        y_limits = ax.get_ylim()
        ax.set_ylim(y_limits[0], max_height * 1.35)
    
    def plot_investor_comparison(
        self,
        investors: List[Dict[str, Any]],
        metrics: List[str] = ['deal_count', 'total_investments', 'lead_investments'],
        metric_labels: List[str] = None,
        title: str = "Investor Comparison",
        max_display: int = 10,
        output_path: Optional[str] = None
    ):
        """
        Create a grouped bar chart comparing multiple metrics across investors.
        
        Args:
            investors: List of investor dicts
            metrics: List of metric fields to compare
            metric_labels: Custom labels for metrics (or None for auto)
            title: Chart title
            max_display: Maximum number of investors to display
            output_path: Path to save chart, or None to display
        """
        if not investors:
            print("⚠️  No investor data to plot")
            return
        
        # Limit display
        investors = investors[:max_display]
        
        # Extract data
        names = [inv.get('name', 'Unknown') for inv in investors]
        metric_data = {
            metric: [inv.get(metric, 0) or 0 for inv in investors]
            for metric in metrics
        }
        
        # Reverse for display
        names = names[::-1]
        for metric in metrics:
            metric_data[metric] = metric_data[metric][::-1]
        
        # Create plot
        fig, ax = self.setup_plot_style(figsize=(14, max(8, len(names) * 0.6)))
        
        # Plot grouped bars
        bar_height = 0.8 / len(metrics)
        colors = [self.default_colors['primary'], self.default_colors['accent'], 
                 self.default_colors['success']]
        
        for i, (metric, color) in enumerate(zip(metrics, colors)):
            y_positions = [y + (i - len(metrics)/2 + 0.5) * bar_height 
                          for y in range(len(names))]
            ax.barh(y_positions, metric_data[metric], bar_height, 
                   label=metric_labels[i] if metric_labels else metric.replace('_', ' ').title(),
                   color=color, alpha=0.8)
        
        # Styling
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=11)
        ax.set_xlabel('Count', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Save or show
        self.save_or_show(output_path)


class IndustryChart(BaseGraphGenerator):
    """Generate charts for industry analysis."""
    
    def plot_industry_distribution(
        self,
        industry_data: List[Dict[str, Any]],
        title: str = "Investment by Industry",
        max_display: int = 15,
        output_path: Optional[str] = None
    ):
        """
        Create a horizontal bar chart of industry distribution.
        
        Args:
            industry_data: List of dicts with 'industry_name' and 'count' keys
            title: Chart title
            max_display: Maximum industries to display
            output_path: Path to save chart, or None to display
        """
        if not industry_data:
            print("⚠️  No industry data to plot")
            return
        
        # Limit and extract data
        industry_data = industry_data[:max_display]
        names = [ind.get('industry_name', 'Unknown') for ind in industry_data]
        counts = [ind.get('count', 0) for ind in industry_data]
        
        # Reverse for display
        names = names[::-1]
        counts = counts[::-1]
        
        # Create plot
        fig, ax = self.setup_plot_style(figsize=(12, max(8, len(names) * 0.4)))
        
        # Create gradient colors
        colors = plt.cm.viridis([i/len(names) for i in range(len(names))])
        
        bars = ax.barh(range(len(names)), counts, color=colors, alpha=0.8)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            ax.text(width + max(counts) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'{int(count)}',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        # Styling
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=11)
        ax.set_xlabel('Number of Investments', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Save or show
        self.save_or_show(output_path)
