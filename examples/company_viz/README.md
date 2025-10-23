# Agent Companies Visualization

This example analyzes and visualizes companies that raised funding in the last 6 months, comparing those with "agent" in their description versus those without.

## What It Does

1. **Fetches all deals from the last 6 months** using the Fundable API with pagination (page_size=100)
2. **Searches for the keyword "agent"** (case-insensitive) in both short and long descriptions
3. **Categorizes deals** into two groups:
   - Companies with "agent" in their description
   - Companies without "agent" in their description
4. **Creates a bar chart visualization** comparing the two categories
5. **Saves detailed results** to JSON files for further analysis

## Usage

```bash
# Run the analysis
python agent_analysis.py
```

Make sure you have your `FUNDABLE_API_KEY` set in your environment or `.env` file.

## Output

The script generates the following outputs in the `output/` directory:

1. **agent_companies_comparison.png** - Bar chart visualization showing the distribution
2. **agent_deals_summary.json** - Detailed information about deals with "agent" in description
3. **non_agent_deals_summary.json** - Detailed information about deals without "agent"

## Requirements

- `matplotlib` - for creating visualizations
- `fundable` package (already in this repo)

Install matplotlib if needed:
```bash
pip install matplotlib
```

## Example Output

```
🚀 Agent Companies Analysis
============================================================
Analyzing deals from the last 6 months to compare companies
with 'agent' in their description vs. those without.

📅 Fetching deals from 2025-04-23 to 2025-10-23
============================================================
📦 Fetching page 1 (page_size=100)... (100 deals)
📦 Fetching page 2 (page_size=100)... (87 deals)

✅ Total deals fetched: 187

🔍 Categorizing deals by 'agent' keyword...
✅ Found 23 deals with 'agent'
✅ Found 164 deals without 'agent'

📊 Summary Statistics:
============================================================
Total Deals:          187
With 'agent':         23 (12.3%)
Without 'agent':      164 (87.7%)
```

## How It Works

### Data Fetching
- Uses `FundableClient.get_deals()` with automatic pagination
- Fetches deals from exactly 6 months ago (180 days) to today
- Continues fetching pages until all deals are retrieved

### Keyword Search
- Searches both `deal_descriptions.short_description` and `deal_descriptions.long_description`
- Case-insensitive matching for the word "agent"
- Handles missing or null descriptions gracefully

### Visualization
- Creates a clean bar chart with two categories
- Shows absolute counts and percentages
- Color-coded for easy distinction
- Saves as high-resolution PNG (300 DPI)

## Customization

You can modify the script to:

- **Change the time range**: Edit the `timedelta(days=180)` in `fetch_all_deals_last_6_months()`
- **Search for different keywords**: Modify the `has_agent_in_description()` function
- **Add more filters**: Pass additional parameters to `client.get_deals()` (e.g., `industries`, `financing_types`)
- **Adjust visualization style**: Modify the `create_visualization()` function

## API Parameters Used

- `deal_start_date` - Start of date range (6 months ago)
- `deal_end_date` - End of date range (today)
- `page` - Page number for pagination
- `page_size` - Number of results per page (100)
- `sort_by` - Sort order ('Most Recent')
