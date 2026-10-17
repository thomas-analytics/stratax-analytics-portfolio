# Data dictionary

The dataset is synthetic. Monetary fields use Pakistani rupees (PKR); no real customer or business data is included.

| Column | Definition |
|---|---|
| `order_id` | Fictional order identifier; multiple product rows can belong to the same order. |
| `order_date` | Date the fictional order was placed. |
| `customer_id` | Fictional customer key. |
| `city` | Fictional buyer city in Pakistan. |
| `sales_channel` | Online Store, Retail Store, or Marketplace. |
| `customer_segment` | Consumer, Small Business, or Corporate. |
| `category` | Product category. |
| `product` | Fictional product name. |
| `quantity` | Units for the line item; positive integer. |
| `unit_price_pkr` | Unit sale price before discount. |
| `unit_cost_pkr` | Simplified fictional unit cost. Does not include delivery, overhead, returns, or taxes. |
| `discount_pct` | Line-level discount as a decimal between 0 and 1. |
| `gross_revenue_pkr` | `quantity × unit_price_pkr`. |
| `discount_amount_pkr` | `gross_revenue_pkr × discount_pct`. |
| `net_revenue_pkr` | `gross_revenue_pkr − discount_amount_pkr`. |
| `cost_pkr` | `quantity × unit_cost_pkr`. |
| `profit_pkr` | `net_revenue_pkr − cost_pkr`; not full accounting profit. |
| `profit_margin_pct` | Line-level `profit_pkr / net_revenue_pkr`; aggregate margin should be total profit divided by total net revenue. |
| `month` | Calendar month in YYYY-MM format, derived from order date. |
| `year` | Year derived from order date. |
| `month_number` | Month number 1-12, derived from order date. |

`source_row_id` is retained in the raw CSV to make generated rows traceable. The cleaned CSV includes calculated fields and is intended for downstream analysis.
