"""Generate reproducible synthetic retail transaction data for portfolio practice.

This dataset is entirely fictional. It contains no real customer or business data.
Run from the repository root:
    python project/retail-sales-dashboard/src/generate_synthetic_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20261017
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "retail_sales_raw.csv"


def main() -> None:
    rng = np.random.default_rng(SEED)
    n_orders = 4200
    start = pd.Timestamp("2025-01-01")
    end = pd.Timestamp("2025-12-31")
    dates = pd.date_range(start, end, freq="D")
    # Fictional seasonality: stronger year-end and mid-year demand.
    monthly_weights = np.array([0.075, 0.070, 0.078, 0.077, 0.080, 0.085,
                                0.090, 0.080, 0.078, 0.085, 0.095, 0.107])
    day_weights = np.array([monthly_weights[d.month - 1] / sum(1 for x in dates if x.month == d.month) for d in dates])
    day_weights = day_weights / day_weights.sum()

    cities = np.array(["Lahore", "Karachi", "Islamabad", "Faisalabad", "Multan", "Peshawar"])
    city_probs = np.array([0.28, 0.27, 0.16, 0.12, 0.09, 0.08])
    channels = np.array(["Online Store", "Retail Store", "Marketplace"])
    channel_probs = np.array([0.43, 0.35, 0.22])
    segments = np.array(["Consumer", "Small Business", "Corporate"])
    segment_probs = np.array([0.68, 0.24, 0.08])

    catalog = {
        "Electronics": [("Wireless Earbuds", 6500, 0.70), ("Power Bank", 4200, 0.67),
                        ("Bluetooth Speaker", 8200, 0.68), ("USB-C Hub", 5700, 0.63)],
        "Home & Kitchen": [("Electric Kettle", 5200, 0.61), ("Blender", 8900, 0.64),
                           ("Storage Set", 3100, 0.55), ("Desk Lamp", 4600, 0.58)],
        "Apparel": [("Basic T-Shirt", 1800, 0.48), ("Hoodie", 4200, 0.52),
                    ("Everyday Backpack", 5600, 0.57), ("Casual Cap", 1200, 0.45)],
        "Beauty & Personal Care": [("Skin Care Set", 3900, 0.53), ("Hair Dryer", 6800, 0.61),
                                   ("Body Care Pack", 2400, 0.50), ("Travel Grooming Kit", 3200, 0.54)],
        "Office Supplies": [("Notebook Bundle", 1100, 0.44), ("Wireless Mouse", 2600, 0.56),
                            ("Keyboard", 3900, 0.58), ("Monitor Stand", 4700, 0.55)],
    }
    category_names = np.array(list(catalog.keys()))
    category_probs = np.array([0.25, 0.22, 0.19, 0.18, 0.16])

    customer_ids = np.array([f"C{i:05d}" for i in range(1, 1501)])
    customer_segment = dict(zip(customer_ids, rng.choice(segments, size=len(customer_ids), p=segment_probs)))
    orders = []
    row_number = 1
    for order_num in range(1, n_orders + 1):
        order_id = f"ORD{order_num:06d}"
        order_date = pd.Timestamp(rng.choice(dates, p=day_weights))
        customer_id = str(rng.choice(customer_ids))
        city = str(rng.choice(cities, p=city_probs))
        channel = str(rng.choice(channels, p=channel_probs))
        segment = customer_segment[customer_id]
        n_lines = int(rng.choice([1, 2, 3, 4], p=[0.22, 0.43, 0.26, 0.09]))
        used_products = set()
        for _ in range(n_lines):
            category = str(rng.choice(category_names, p=category_probs))
            product, base_price, cost_ratio = catalog[category][int(rng.integers(0, len(catalog[category])))]
            # A given order can contain multiple lines, but avoid duplicate exact products.
            if product in used_products:
                product, base_price, cost_ratio = catalog[category][int(rng.integers(0, len(catalog[category])))]
            used_products.add(product)
            quantity = int(rng.choice([1, 2, 3, 4, 5], p=[0.54, 0.25, 0.13, 0.06, 0.02]))
            price = int(round(base_price * rng.uniform(0.92, 1.08) / 50) * 50)
            unit_cost = int(round(price * cost_ratio * rng.uniform(0.94, 1.06) / 10) * 10)
            # Promotions vary by channel and month, intentionally creating a margin-analysis question.
            discount_base = {"Online Store": 0.07, "Retail Store": 0.04, "Marketplace": 0.11}[channel]
            if order_date.month in (6, 7, 11, 12):
                discount_base += 0.035
            discount = float(np.clip(rng.normal(discount_base, 0.035), 0, 0.28))
            orders.append({
                "order_id": order_id,
                "order_date": order_date.strftime("%Y-%m-%d"),
                "customer_id": customer_id,
                "city": city,
                "sales_channel": channel,
                "customer_segment": segment,
                "category": category,
                "product": product,
                "quantity": quantity,
                "unit_price_pkr": price,
                "unit_cost_pkr": unit_cost,
                "discount_pct": round(discount, 4),
                "source_row_id": row_number,
            })
            row_number += 1
    df = pd.DataFrame(orders).sort_values(["order_date", "order_id", "source_row_id"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df):,} synthetic order lines across {df['order_id'].nunique():,} orders to {OUT}")


if __name__ == "__main__":
    main()
