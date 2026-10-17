# Power BI build guide

> This guide is part of a portfolio project using **synthetic data**. The Python charts are analytical previews, not screenshots of a finished Power BI report. Build and save your own `.pbix` file in Power BI Desktop before describing the Power BI dashboard as completed.

## 1. Load the data

1. Run the Python pipeline from the repository root (instructions in the project README).
2. Open Power BI Desktop and choose **Get data → Text/CSV**.
3. Load `data/processed/retail_sales_clean.csv`.
4. In Power Query, confirm `order_date` is Date, quantity is Whole number, `discount_pct` is Decimal number, and currency fields are Decimal number.
5. Confirm there are no blank order IDs and no negative quantities. The pipeline already applies basic cleaning, but validate the loaded table as part of the project.
6. Rename the table `Sales`.

## 2. Create a date table

Create a calculated table with **Modeling → New table**:

```DAX
Date =
ADDCOLUMNS (
    CALENDAR ( MIN ( Sales[order_date] ), MAX ( Sales[order_date] ) ),
    "Year", YEAR ( [Date] ),
    "Month Number", MONTH ( [Date] ),
    "Month", FORMAT ( [Date], "MMM" ),
    "Year-Month", FORMAT ( [Date], "YYYY-MM" )
)
```

Sort `Date[Month]` by `Date[Month Number]`, then create a one-to-many relationship from `Date[Date]` to `Sales[order_date]`. Mark the date table as a date table if your Power BI version supports it.

## 3. Add these DAX measures

```DAX
Gross Sales (PKR) = SUM ( Sales[gross_revenue_pkr] )

Discount Amount (PKR) = SUM ( Sales[discount_amount_pkr] )

Net Revenue (PKR) = SUM ( Sales[net_revenue_pkr] )

Total Cost (PKR) = SUM ( Sales[cost_pkr] )

Total Profit (PKR) = SUM ( Sales[profit_pkr] )

Profit Margin % = DIVIDE ( [Total Profit (PKR)], [Net Revenue (PKR)] )

Total Orders = DISTINCTCOUNT ( Sales[order_id] )

Unique Customers = DISTINCTCOUNT ( Sales[customer_id] )

Units Sold = SUM ( Sales[quantity] )

Average Order Value (PKR) = DIVIDE ( [Net Revenue (PKR)], [Total Orders] )

Discount Rate % = DIVIDE ( [Discount Amount (PKR)], [Gross Sales (PKR)] )
```

Format revenue, cost, and profit measures as currency/whole PKR with suitable thousands separators. Format `Profit Margin %` and `Discount Rate %` as percentages.

## 4. Suggested one-page executive dashboard

**Top row: five KPI cards**
- Net Revenue (PKR)
- Total Profit (PKR)
- Profit Margin %
- Total Orders
- Average Order Value (PKR)

**Middle row**
- Line chart: `Date[Year-Month]` by Net Revenue and Total Profit
- Bar chart: Category by Net Revenue, with Profit available in tooltip

**Bottom row**
- Bar chart: Sales Channel by Net Revenue; add Profit Margin % to tooltip
- Bar chart or matrix: City by Net Revenue, Total Orders, Profit Margin %
- Scatter plot: Discount Rate (or average line-level discount) vs Profit Margin, with category/channel in details or legend if helpful

**Slicers:** Date, City, Sales Channel, Category, Customer Segment.

## 5. Quality checks before publishing

- Does the report total reconcile with `outputs/kpi_summary.csv`?
- Do orders use `DISTINCTCOUNT(order_id)` rather than row count?
- Does profit equal Net Revenue minus Cost?
- Is profit margin calculated as total profit divided by total revenue, not an average of row-level margins?
- Are date labels sorted chronologically?
- Can a viewer filter by city and channel without breaking the report?
- Add a visible note: “Portfolio case study using synthetic data. No real business or customer data.”

## 6. What to export

Save the native file as `retail-sales-performance.pbix`. Export one clean report page to PDF or PNG for the GitHub README and LinkedIn project media. Do not call the Python-generated preview a Power BI screenshot.
