# Methodology and limitations

## Pipeline

1. Generate fictional transaction-line data with a deterministic NumPy random seed.
2. Validate expected fields, parse dates, coerce numeric types, remove duplicate rows, remove incomplete records, and filter out invalid quantities, prices, costs, and discounts.
3. Calculate revenue, discounts, cost, profit, and row-level margin.
4. Aggregate order-level, monthly, category, channel, and city KPIs.
5. Export tables and exploratory plots, then compare the same core measures in Power BI.

## Metric definitions

- **Gross revenue:** units × unit price before discounts.
- **Discount amount:** gross revenue × discount rate.
- **Net revenue:** gross revenue less discount amount.
- **Modeled profit:** net revenue less modeled product cost.
- **Profit margin:** total modeled profit divided by total net revenue. In aggregated reporting, calculate the ratio from summed amounts instead of averaging line-level margin percentages.
- **Average order value:** total net revenue divided by distinct order count.

## Limitations and ethical reporting

Synthetic data is valuable for demonstrating a workflow, but it does not prove business impact or real-world customer behaviour. The pattern-generating assumptions influence the findings. The project excludes several cost types and operational variables, so its “profit” metric is a simplified product contribution measure. Findings should be described as **illustrative**. Recommendations should be phrased as hypotheses that a real business would validate against its own data.
