"""Clean synthetic sales data and create reproducible KPI tables and charts."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "retail_sales_raw.csv"
PROCESSED = ROOT / "data" / "processed" / "retail_sales_clean.csv"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
REQUIRED = ["order_id", "order_date", "customer_id", "city", "sales_channel",
            "customer_segment", "category", "product", "quantity", "unit_price_pkr",
            "unit_cost_pkr", "discount_pct"]


def load_and_clean() -> pd.DataFrame:
    df = pd.read_csv(RAW)
    missing_columns = sorted(set(REQUIRED) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    df = df.drop_duplicates().copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    numeric = ["quantity", "unit_price_pkr", "unit_cost_pkr", "discount_pct"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=REQUIRED).copy()
    df = df[(df["quantity"] > 0) & (df["unit_price_pkr"] >= 0) &
            (df["unit_cost_pkr"] >= 0) & df["discount_pct"].between(0, 1)].copy()
    df["gross_revenue_pkr"] = df["quantity"] * df["unit_price_pkr"]
    df["discount_amount_pkr"] = df["gross_revenue_pkr"] * df["discount_pct"]
    df["net_revenue_pkr"] = df["gross_revenue_pkr"] - df["discount_amount_pkr"]
    df["cost_pkr"] = df["quantity"] * df["unit_cost_pkr"]
    df["profit_pkr"] = df["net_revenue_pkr"] - df["cost_pkr"]
    df["profit_margin_pct"] = df["profit_pkr"].div(df["net_revenue_pkr"].where(df["net_revenue_pkr"] != 0))
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    df["year"] = df["order_date"].dt.year
    df["month_number"] = df["order_date"].dt.month
    return df.sort_values(["order_date", "order_id", "product"]).reset_index(drop=True)


def save_tables(df: pd.DataFrame) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED, index=False, date_format="%Y-%m-%d")
    total_revenue = df["net_revenue_pkr"].sum()
    total_profit = df["profit_pkr"].sum()
    orders = df["order_id"].nunique()
    kpis = pd.DataFrame([{
        "line_items": len(df),
        "orders": orders,
        "customers": df["customer_id"].nunique(),
        "units_sold": int(df["quantity"].sum()),
        "gross_revenue_pkr": round(df["gross_revenue_pkr"].sum(), 2),
        "discount_amount_pkr": round(df["discount_amount_pkr"].sum(), 2),
        "net_revenue_pkr": round(total_revenue, 2),
        "cost_pkr": round(df["cost_pkr"].sum(), 2),
        "profit_pkr": round(total_profit, 2),
        "profit_margin_pct": round(total_profit / total_revenue, 4) if total_revenue else None,
        "average_order_value_pkr": round(total_revenue / orders, 2) if orders else None,
        "discount_rate_pct": round(df["discount_amount_pkr"].sum() / df["gross_revenue_pkr"].sum(), 4) if df["gross_revenue_pkr"].sum() else None,
    }])
    kpis.to_csv(OUT / "kpi_summary.csv", index=False)
    monthly = df.groupby("month", as_index=False).agg(
        net_revenue_pkr=("net_revenue_pkr", "sum"), profit_pkr=("profit_pkr", "sum"),
        orders=("order_id", "nunique"), units_sold=("quantity", "sum"))
    monthly.to_csv(OUT / "monthly_trends.csv", index=False)
    category = df.groupby("category", as_index=False).agg(
        net_revenue_pkr=("net_revenue_pkr", "sum"), profit_pkr=("profit_pkr", "sum"),
        units_sold=("quantity", "sum"), orders=("order_id", "nunique"),
        discount_amount_pkr=("discount_amount_pkr", "sum"), gross_revenue_pkr=("gross_revenue_pkr", "sum"))
    category["profit_margin_pct"] = category["profit_pkr"] / category["net_revenue_pkr"]
    category["discount_rate_pct"] = category["discount_amount_pkr"] / category["gross_revenue_pkr"]
    category.to_csv(OUT / "category_performance.csv", index=False)
    channel = df.groupby("sales_channel", as_index=False).agg(
        net_revenue_pkr=("net_revenue_pkr", "sum"), profit_pkr=("profit_pkr", "sum"),
        orders=("order_id", "nunique"), discount_amount_pkr=("discount_amount_pkr", "sum"),
        gross_revenue_pkr=("gross_revenue_pkr", "sum"))
    channel["profit_margin_pct"] = channel["profit_pkr"] / channel["net_revenue_pkr"]
    channel["discount_rate_pct"] = channel["discount_amount_pkr"] / channel["gross_revenue_pkr"]
    channel.to_csv(OUT / "channel_performance.csv", index=False)
    city = df.groupby("city", as_index=False).agg(
        net_revenue_pkr=("net_revenue_pkr", "sum"), profit_pkr=("profit_pkr", "sum"),
        orders=("order_id", "nunique"))
    city["profit_margin_pct"] = city["profit_pkr"] / city["net_revenue_pkr"]
    city.to_csv(OUT / "city_performance.csv", index=False)
    insights = build_insights(df, kpis.iloc[0], monthly, category, channel)
    (OUT / "illustrative_findings.md").write_text(insights, encoding="utf-8")
    create_charts(monthly, category, channel, df)
    return {"kpis": kpis, "monthly": monthly, "category": category, "channel": channel}


def build_insights(df, kpi, monthly, category, channel) -> str:
    best_month = monthly.loc[monthly["net_revenue_pkr"].idxmax()]
    best_category = category.loc[category["net_revenue_pkr"].idxmax()]
    best_profit_cat = category.loc[category["profit_pkr"].idxmax()]
    best_channel_margin = channel.loc[channel["profit_margin_pct"].idxmax()]
    worst_channel_margin = channel.loc[channel["profit_margin_pct"].idxmin()]
    channel_margin_gap = (best_channel_margin["profit_margin_pct"] - worst_channel_margin["profit_margin_pct"]) * 100
    return f"""# Illustrative findings (synthetic data only)\n\n> These are calculations from a fictional, generated dataset. They are practice findings, not evidence about a real retailer or client. Amounts are in Pakistani rupees (PKR).\n\n- **Net revenue:** PKR {kpi['net_revenue_pkr']:,.0f} across {int(kpi['orders']):,} distinct orders.\n- **Profit and margin:** PKR {kpi['profit_pkr']:,.0f} profit at a {kpi['profit_margin_pct']:.1%} modeled margin.\n- **Average order value:** PKR {kpi['average_order_value_pkr']:,.0f}.\n- **Highest-revenue month:** {best_month['month']} with PKR {best_month['net_revenue_pkr']:,.0f} net revenue.\n- **Highest-revenue category:** {best_category['category']} with PKR {best_category['net_revenue_pkr']:,.0f} net revenue.\n- **Highest-profit category:** {best_profit_cat['category']} with PKR {best_profit_cat['profit_pkr']:,.0f} profit.\n- **Channel margin spread:** {best_channel_margin['sales_channel']} has the highest modeled channel margin ({best_channel_margin['profit_margin_pct']:.1%}); {worst_channel_margin['sales_channel']} has the lowest ({worst_channel_margin['profit_margin_pct']:.1%}), a difference of {channel_margin_gap:.1f} percentage points.\n\n## Questions a real business should investigate\n\n1. Does higher discounting increase order volume enough to offset the reduction in unit margin?\n2. Are the differences in channel profitability driven by discounting, product mix, or fulfillment costs? (Fulfillment costs are not included in this exercise.)\n3. Which categories produce both revenue and profit, rather than revenue alone?\n4. Would repeat-customer and cohort analysis change the interpretation?\n\n## Limitations\n\nThe dataset is synthetic and contains intentionally simplified costs. It omits taxes, shipping, returns, inventory, marketing spend, payment fees, and actual customer behaviour. No causal or client-impact claims should be made from these results.\n"""


def create_charts(monthly, category, channel, df):
    plt.rcParams.update({"figure.dpi": 140, "savefig.dpi": 180, "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    # Monthly revenue/profit trend
    m = monthly.copy()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(m["month"], m["net_revenue_pkr"] / 1_000_000, marker="o", label="Net revenue")
    ax.plot(m["month"], m["profit_pkr"] / 1_000_000, marker="o", label="Profit")
    ax.set_title("Monthly sales and profit trend | synthetic 2025 data", loc="left", weight="bold")
    ax.set_ylabel("PKR millions")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False, ncol=2)
    ax.grid(axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(CHARTS / "monthly_trend.png", bbox_inches="tight")
    plt.close(fig)

    # Category comparison
    c = category.sort_values("net_revenue_pkr", ascending=True)
    fig, ax = plt.subplots(figsize=(8.5, 4.7))
    ax.barh(c["category"], c["net_revenue_pkr"] / 1_000_000, label="Net revenue")
    ax.set_title("Net revenue by product category", loc="left", weight="bold")
    ax.set_xlabel("PKR millions")
    ax.grid(axis="x", alpha=.25)
    fig.tight_layout()
    fig.savefig(CHARTS / "category_revenue.png", bbox_inches="tight")
    plt.close(fig)

    # Channel revenue and margin
    ch = channel.sort_values("net_revenue_pkr", ascending=False)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars = ax.bar(ch["sales_channel"], ch["net_revenue_pkr"] / 1_000_000)
    ax.set_title("Net revenue by sales channel", loc="left", weight="bold")
    ax.set_ylabel("PKR millions")
    ax.grid(axis="y", alpha=.25)
    for bar, margin in zip(bars, ch["profit_margin_pct"]):
        ax.annotate(f"{margin:.0%} margin", (bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(CHARTS / "channel_revenue_margin.png", bbox_inches="tight")
    plt.close(fig)

    # Discount vs margin by transaction line, with a sampled population to keep chart readable.
    sample = df.sample(min(len(df), 1200), random_state=18)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.scatter(sample["discount_pct"] * 100, sample["profit_margin_pct"] * 100, alpha=.25, s=12)
    ax.set_title("Discount rate vs line-item profit margin", loc="left", weight="bold")
    ax.set_xlabel("Discount (%)")
    ax.set_ylabel("Profit margin (%)")
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(CHARTS / "discount_margin_scatter.png", bbox_inches="tight")
    plt.close(fig)

    # A dashboard-style preview using Python-generated charts, explicitly not a Power BI screenshot.
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    axes[0, 0].plot(m["month"], m["net_revenue_pkr"] / 1_000_000, marker="o", label="Net revenue")
    axes[0, 0].plot(m["month"], m["profit_pkr"] / 1_000_000, marker="o", label="Profit")
    axes[0, 0].set_title("Monthly trend")
    axes[0, 0].tick_params(axis="x", rotation=45)
    axes[0, 0].legend(frameon=False)
    axes[0, 0].grid(axis="y", alpha=.2)
    c2 = category.sort_values("net_revenue_pkr", ascending=True)
    axes[0, 1].barh(c2["category"], c2["net_revenue_pkr"] / 1_000_000)
    axes[0, 1].set_title("Revenue by category (PKR M)")
    axes[0, 1].grid(axis="x", alpha=.2)
    axes[1, 0].bar(ch["sales_channel"], ch["net_revenue_pkr"] / 1_000_000)
    axes[1, 0].set_title("Revenue by channel (PKR M)")
    axes[1, 0].tick_params(axis="x", rotation=15)
    axes[1, 0].grid(axis="y", alpha=.2)
    axes[1, 1].scatter(sample["discount_pct"] * 100, sample["profit_margin_pct"] * 100, alpha=.22, s=8)
    axes[1, 1].set_title("Discount vs margin")
    axes[1, 1].set_xlabel("Discount (%)")
    axes[1, 1].set_ylabel("Margin (%)")
    axes[1, 1].grid(alpha=.2)
    fig.suptitle("Stratax | Retail sales analytics preview\nPython-generated concept, not a Power BI dashboard", x=.05, ha="left", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, .93])
    fig.savefig(CHARTS / "dashboard_preview_python_not_powerbi.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    if not RAW.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW}. Run generate_synthetic_data.py first.")
    df = load_and_clean()
    tables = save_tables(df)
    kpi = tables["kpis"].iloc[0]
    print(f"Cleaned {len(df):,} rows across {int(kpi['orders']):,} orders")
    print(f"Net revenue PKR {kpi['net_revenue_pkr']:,.0f} | Profit PKR {kpi['profit_pkr']:,.0f} | Margin {kpi['profit_margin_pct']:.1%}")
    print(f"Outputs saved under {OUT}")


if __name__ == "__main__":
    main()
