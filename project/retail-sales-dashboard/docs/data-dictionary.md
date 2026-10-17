# Data dictionary

The source rows are synthetic order-line records created with a fixed random seed. Identifiers are fictional IDs, not personal information. Currency fields are in PKR.

## Raw dataset: `data/raw/retail_sales_raw.csv`

| Field | Definition |
|---|---|
| `order_id` | Fictional order identifier. One order may contain multiple product rows. |
| `order_date` | Order date in ISO format (`YYYY-MM-DD`), generated within 2025. |
| `customer_id` | Fictional customer identifier. |
| `city` | Fictional sales location among six Pakistani cities. |
| `sales_channel` | Online Store, Retail Store, or Marketplace. |
| `customer_segment` | Consumer, Small Business, or Corporate, assigned to each fictional customer. |
| `category` | Product category. |
| `product` | Fictional product name. |
| `quantity` | Units on the line. |
| `unit_price_pkr` | List price per unit, in PKR. |
| `unit_cost_pkr` | Simplified modeled cost per unit, in PKR. Does not include delivery, taxes, fees, overhead, or marketing. |
| `discount_pct` | Discount as a decimal between 0 and 1. For example, `0.10` means 10%. |
| `source_row_id` | Synthetic source row number, useful for tracing generated rows. |

## Processed dataset: `data/processed/retail_sales_clean.csv`

All raw columns are retained, plus the following derived fields.

| Field | Definition |
|---|---|
| `gross_revenue_pkr` | `quantity × unit_price_pkr` before discount. |
| `discount_amount_pkr` | `gross_revenue_pkr × discount_pct`. |
| `net_revenue_pkr` | `gross_revenue_pkr − discount_amount_pkr`. |
| `cost_pkr` | `quantity × unit_cost_pkr`. |
| `profit_pkr` | `net_revenue_pkr − cost_pkr`; a simplified contribution measure, not audited accounting profit. |
| `profit_margin_pct` | `profit_pkr ÷ net_revenue_pkr`. Stored as a decimal ratio. |
| `month` | Year and month label in `YYYY-MM` format. |
| `year` | Calendar year derived from order date. |
| `month_number` | Numeric month (1-12), used for date ordering. |

## Important limitations

There are no real customers, sales, or business records. The cost model is simplified. Returns, shipping/fulfillment costs, taxes, marketing spend, payment fees, inventory, and overhead are omitted. Do not describe the modeled profit figure as audited profit or use these outputs to make claims about a real company.
