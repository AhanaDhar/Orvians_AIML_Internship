# Week 2 — Data Visualization & Exploratory Data Analysis

This folder contains the Week 2 EDA notebook for the Invoice Payment Delay & Cash-Flow Intelligence Platform.

## Files
- `week2_invoice_eda.ipynb` — reproducible Jupyter notebook covering data quality, univariate and bivariate analysis, monthly trends, customer and payment-term analysis, and open-invoice aging.

## Run
Install the dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Open the notebook from this folder. It reads the cleaned dataset from:

`../data/processed/cleaned_invoices.csv`

## Analysis notes
- Paid invoices are analyzed separately from open invoices.
- USD and CAD monetary values should be reported separately unless converted using an explicit FX rate.
- Customer grouping uses `customer_id`, not free-text customer names.
- Post-payment columns such as `payment_date`, `days_to_pay`, and `delay_days` must not be used as predictors in a model intended to predict late payment at invoice creation.
