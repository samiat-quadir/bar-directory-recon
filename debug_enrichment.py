#!/usr/bin/env python3
"""
Debug script to test enrichment on raw CSV data
"""

import sys

sys.path.append("src")

import pandas as pd

from property_enrichment import PropertyEnrichment

# Load the raw CSV and inspect it
try:
    df = pd.read_csv("outputs/hallandale/hallandale_properties_raw.csv")
    print("Raw CSV loaded successfully")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nFirst few rows:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)

    print("\nNull values:")
    print(df.isnull().sum())

    # Test enrichment on first row
    print("\nTesting enrichment on first row:")
    first_row = df.iloc[0].to_dict()
    print(f"First row: {first_row}")

    enricher = PropertyEnrichment()
    enriched_row = enricher._enrich_single_property(first_row)
    print(f"Enriched row: {enriched_row}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
