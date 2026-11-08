# Week 1 Submission Write-up

**Internship:** Orvians Technologies — Invoice Payment Delay & Cash-Flow Intelligence Platform  
**Topic:** Data Cleaning & Preprocessing

## What I did
I selected the Customer Invoices Dataset and audited 50,000 rows and 19 source columns using pandas. I checked missing values, duplicates, date consistency, invoice identifiers, payment status and invoice amounts. I standardized text and dates, removed 1,161 exact duplicate records, and generated a clean dataset of 48,839 records. I created `days_to_pay`, `delay_days`, `paid_late_flag` and `is_open` fields with missing labels for unpaid invoices.

## Main findings
- 9,681 open invoices and 39,158 paid invoices in the cleaned file.
- 39,048 valid observed delay labels, including 16,308 late-paid invoices.
- `area_business` was entirely empty and was removed.
- Six invoice IDs were missing and were replaced with explicitly flagged document-ID fallbacks.
- 137 remaining records had due dates earlier than invoice/posting dates; these were flagged, not silently corrected.
- Country is not available and remains missing. USD and CAD amounts are not combined into one total.

## What I learned
I practiced pandas data profiling, type conversion, YYYYMMDD date parsing, duplicate detection, missing-value handling, data quality flags and reproducible preprocessing. I learned why unpaid invoices should not be assigned invented payment dates and why future payment information must not be used as a predictive feature.

## Problems / limitations
The source has ambiguous invoice date fields and uses clearance date as the payment date proxy. I chose `posting_date` as the invoice date and kept original creation-date columns for review. Country is missing. Some records have inconsistent date chronology. These assumptions should be confirmed with my mentor before later modelling.

## Next week
Perform EDA on cleaned invoices: payment delays, paid-late frequency, currency-specific amounts, customer-level patterns and missingness.