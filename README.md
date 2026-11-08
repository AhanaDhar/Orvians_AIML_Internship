# Orvians Technologies — Week 1: Data Cleaning & Preprocessing

**Project:** Invoice Payment Delay & Cash-Flow Intelligence Platform  
**Dataset:** Customer Invoices Dataset (Kaggle, pradumn203)  
**Task start:** 1 November 2026

## Deliverables
- `data/processed/cleaned_invoices.csv` — cleaned data
- `reports/data_dictionary_and_mapping.csv` — mapping, types, definitions
- `reports/cleaning_log.csv` — each issue, action, reason, count
- `clean_invoices.py` — reproducible cleaning pipeline
- `reports/summary.csv` — numeric checkpoint
- `weekly_writeup.md` — submission reflection

## Run
From the project directory:
```bash
pip install -r requirements.txt
python clean_invoices.py
```
Input: `data/raw/dataset.csv`. Outputs are overwritten deterministically.

## Key decisions and assumptions
- **Invoice date proxy:** `posting_date` is used as invoice date; confirm with mentor whether this is appropriate instead of a creation date.
- **Status:** `isOpen=1` is open, `isOpen=0` is paid. Missing payment dates for open invoices are expected and **not imputed**.
- **Invoice ID:** Six missing invoice IDs are filled with `DOC_` + `doc_id`, explicitly marked as fallbacks.
- **Duplicates:** Remove exact duplicate rows, keeping first; any future non-identical repeated invoice IDs are resolved by first occurrence, a rule to revisit with mentor.
- **Dates:** Source `due_in_date` is a numeric-looking YYYYMMDD date; parse strictly. Suspicious due-before-invoice records are flagged, not deleted.
- **Amounts:** No exchange-rate conversion; USD and CAD must not be aggregated as a single currency total.
- **Country:** Not present; do not infer it from currency or business codes.
- **Payment labels:** Derived only for paid, date-valid invoices. Open invoices retain missing labels; never use `payment_date`, `days_to_pay`, `delay_days`, or `paid_late_flag` as predictive features for a pre-payment prediction.



## Git suggestion
```bash
git init
git add .
git commit -m "Complete Week 1 invoice data cleaning and documentation"
```
Large raw/processed CSV files may be excluded from public GitHub if required by dataset licensing or repository size limits; document how to retrieve them.
