# Fundable API Example

This repository contains a Python client for interacting with the Fundable API, along with examples demonstrating how to fetch and process deal data.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your API key:**
   ```bash
   export FUNDABLE_API_KEY="your_api_key_here"
   ```

3. **Run the example:**
   ```bash
   python apiTest.py
   ```

## Files

- `fundableClient.py` - Main client library with `FundableClient` and `DataExtractor` classes
- `apiTest.py` - Example usage demonstrating various API parameters and filters
- `output/` - Directory where sample output files are saved

## API Documentation

For complete API documentation, including all available endpoints, parameters, and response formats, please reference the full documentation at:

**https://fundable-api-docs.readme.io/reference/**

## Requirements

- Python 3.6+
- Valid Fundable API key

See `requirements.txt` for Python package dependencies.