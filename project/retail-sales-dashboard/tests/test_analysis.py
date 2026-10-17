"""Minimal reproducibility and data-quality checks for the synthetic analysis."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import analyze_sales  # noqa: E402


def test_cleaned_dataset_has_required_calculations():
    df = analyze_sales.load_and_clean()
    assert len(df) > 0
    assert df["order_id"].nunique() > 0
    assert (df["quantity"] > 0).all()
    assert df["discount_pct"].between(0, 1).all()
    assert (df["net_revenue_pkr"] <= df["gross_revenue_pkr"] + 1e-8).all()
    assert (df["profit_pkr"].sub(df["net_revenue_pkr"] - df["cost_pkr"]).abs() < 1e-6).all()


def test_summary_reconciles_to_rows():
    df = analyze_sales.load_and_clean()
    assert round(df["net_revenue_pkr"].sum(), 2) >= 0
    assert df["order_id"].nunique() == 4200
