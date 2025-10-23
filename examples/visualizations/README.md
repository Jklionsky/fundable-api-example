# Fundable API Visualizations

This directory contains examples of visualizing Fundable API data with professional charts and logos.

## Features

- 📊 **Bar charts** with investor logos
- 🎨 **Customizable styling** (colors, sizes, layouts)
- 💾 **Logo caching** for faster subsequent runs
- 📈 **Multiple chart types**: single metric, comparisons, industry distribution
- 🖼️ **Automatic logo handling** with graceful fallbacks

## Quick Start

### 1. Install Dependencies

```bash
pip install -r ../../requirements.txt
```

### 2. Run Examples

```bash
python visualize_top_investors.py
```

This will:
1. Fetch top seed investors from the last 2 months
2. Download their logos
3. Generate a chart with logos at `output/charts/top_seed_investors_with_logos.png`

## Available Examples

### Example 1: Seed Investors with Logos
Creates a horizontal bar chart of top seed investors with their logos displayed.

```python
example_1_seed_investors_with_logos()
```

### Example 2: Series A Investors
Simple bar chart without logos for a cleaner look.

```python
example_2_series_a_investors()
```

### Example 3: Multi-Metric Comparison
Compare multiple metrics (recent deals, total investments, lead investments) side-by-side.

```python
example_3_investor_comparison()
```

### Example 4: Industry Distribution
Visualize the industry focus of top investors.

```python
example_4_industry_distribution()
```

### Example 5: AI Investors with Logos
Filter by industry (AI) and show with logos.

```python
example_5_ai_investors_with_logos()
```

## Using the Graph Generator in Your Code

### Basic Usage

```python
from utils.graph_generator import InvestorBarChart
from top_investors.investor_analyzer import InvestorAnalyzer

# Analyze investors
analyzer = InvestorAnalyzer(client)
results = analyzer.analyze_top_investors(
    top_n=15,
    financing_types=['SEED']
)

# Create chart
chart = InvestorBarChart()
chart.plot_top_investors(
    results,
    title="Top Seed Investors",
    show_logos=True,
    output_path="my_chart.png"
)
```

### Customization Options

```python
chart.plot_top_investors(
    results,
    title="Custom Title",
    metric="total_investments",  # Change metric
    show_logos=True,              # Enable/disable logos
    logo_size=(80, 80),          # Custom logo size
    max_display=10,               # Limit number shown
    color="#FF5733",              # Custom bar color
    output_path="output.png"      # Save location
)
```

### Multiple Metrics Comparison

```python
chart.plot_investor_comparison(
    results,
    metrics=['deal_count', 'total_investments', 'lead_investments'],
    metric_labels=['Recent Deals', 'All Time', 'As Lead'],
    title="Investor Activity Overview",
    max_display=10,
    output_path="comparison.png"
)
```

## Chart Types

### InvestorBarChart
- `plot_top_investors()` - Horizontal bar chart with optional logos
- `plot_investor_comparison()` - Grouped bars for multiple metrics

### IndustryChart
- `plot_industry_distribution()` - Industry breakdown chart

## Logo Handling

- Logos are automatically downloaded from the Fundable API
- Cached in `.logo_cache/` directory to avoid re-downloading
- Gracefully handles missing/broken logo URLs
- Automatically resized and positioned

## Output

All charts are saved to `output/charts/` by default with:
- High resolution (300 DPI)
- Professional styling
- Transparent backgrounds for logos
- Grid lines and value labels

## Troubleshooting

**Issue**: Logos not appearing
- Check that the API is returning `image` field
- Verify internet connection for logo downloads
- Check `.logo_cache/` directory permissions

**Issue**: Charts look cramped
- Increase `max_display` parameter
- Adjust `figsize` in the generator class

**Issue**: Matplotlib style warning
- Update matplotlib: `pip install --upgrade matplotlib`
