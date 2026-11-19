"""
SubroRecover AI - Data Engineering Test Suite
Tests data ingestion, cleaning, transformation, validation, and database loading.
"""

import os
import sys
import pytest
import pandas as pd

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_engineering.ingestion import DataIngestion
from data_engineering.cleaning import DataCleaner
from data_engineering.transformation import DataTransformer
from data_engineering.validation import DataValidator
from data_engineering.database_loader import DatabaseLoader

def test_ingestion():
    ingestion = DataIngestion(data_dir="sample_data")
    datasets = ingestion.ingest_all()
    assert "customers" in datasets
    assert "policies" in datasets
    assert "claims" in datasets
    assert len(datasets["claims"]) >= 100

def test_cleaning():
    ingestion = DataIngestion(data_dir="sample_data")
    raw = ingestion.ingest_all()
    cleaner = DataCleaner()
    cleaned, stats = cleaner.clean_all(raw)
    
    # Check null imputation
    assert cleaned["claims"]["paid_amount"].isnull().sum() == 0
    assert cleaned["claims"]["claimed_amount"].isnull().sum() == 0
    assert (cleaned["claims"]["paid_amount"] >= 0).all()

def test_transformation():
    ingestion = DataIngestion(data_dir="sample_data")
    raw = ingestion.ingest_all()
    cleaner = DataCleaner()
    cleaned, _ = cleaner.clean_all(raw)
    transformer = DataTransformer()
    transformed, stats = transformer.transform_all(cleaned)
    
    assert "claims_enhanced" in transformed
    df_claims = transformed["claims_enhanced"]
    assert "days_to_report" in df_claims.columns
    assert "subro_indicator_score" in df_claims.columns
    assert (df_claims["subro_indicator_score"] >= 0).all()
    assert (df_claims["subro_indicator_score"] <= 1.0).all()

def test_validation():
    ingestion = DataIngestion(data_dir="sample_data")
    raw = ingestion.ingest_all()
    cleaner = DataCleaner()
    cleaned, _ = cleaner.clean_all(raw)
    validator = DataValidator()
    report = validator.validate_all(cleaned)
    
    assert report["is_valid"] is True
    assert report["quality_score_pct"] == 100.0
    assert len(report["errors"]) == 0
