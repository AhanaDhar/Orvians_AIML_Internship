"""Reproducible Week 1 preprocessing for the Customer Invoices Kaggle dataset.
Run: python clean_invoices.py (from the project directory).
No future payment information should be used as a model input at prediction time.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/dataset.csv'
OUT=ROOT/'data/processed'; REPORT=ROOT/'reports'
OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(RAW,dtype=str,low_memory=False)
original_rows=len(df)
log=[]
def record(issue,action,reason,count):
    log.append({'issue':issue,'action':action,'reason':reason,'rows_affected':int(count)})

def parse_compact(s):
    return pd.to_datetime(s.str.replace(r'\.0$','',regex=True),format='%Y%m%d',errors='coerce')

def id_clean(s):
    return s.astype('string').str.strip().str.replace(r'\.0$','',regex=True)

# Standardize whitespace/case without collapsing meaningful customer names.
for c in ['business_code','cust_number','name_customer','invoice_currency','document type','cust_payment_terms']:
    df[c]=df[c].astype('string').str.strip().str.replace(r'\s+',' ',regex=True).str.upper()
for c in ['invoice_id','doc_id']:
    df[c]=id_clean(df[c])

missing_area=df['area_business'].isna().sum()
df=df.drop(columns=['area_business'])
record('area_business entirely missing','Drop column','No usable values in any record',missing_area)

# Drop exact duplicates before unique-ID handling.
exact=int(df.duplicated().sum());df=df.drop_duplicates().copy()
record('Exact duplicate rows','Keep first occurrence','Identical records do not represent additional invoices',exact)

missing_id=df['invoice_id'].isna() | df['invoice_id'].eq('')
# Use document ID only for records lacking invoice ID; retain provenance.
df['invoice_id_source']='ORIGINAL'
can_fill=missing_id & df['doc_id'].notna() & df['doc_id'].ne('')
df.loc[can_fill,'invoice_id']='DOC_'+df.loc[can_fill,'doc_id']
df.loc[can_fill,'invoice_id_source']='DOC_ID_FALLBACK'
record('Missing invoice_id','Use prefixed doc_id when available','Preserves record without confusing fallback with original invoice ID',can_fill.sum())
remaining=df['invoice_id'].isna()|df['invoice_id'].eq('')
record('Missing both invoice_id and doc_id','Drop record','Cannot identify invoice reliably',remaining.sum())
df=df.loc[~remaining].copy()

# Multiple records for same invoice: retain first, flag this as a limitation.
dup_id=df.duplicated(subset=['invoice_id'],keep='first')
record('Repeated invoice_id','Keep first record','One record per invoice; first-occurrence rule must be reviewed if records are updates',dup_id.sum())
df=df.loc[~dup_id].copy()

# Source-specific field mapping.
df=df.rename(columns={'cust_number':'customer_id','name_customer':'customer_name','posting_date':'invoice_date','due_in_date':'due_date','clear_date':'payment_date','total_open_amount':'amount','invoice_currency':'currency','isOpen':'is_open','document type':'document_type','buisness_year':'business_year','document_create_date.1':'document_create_date_posted'})
for c in ['document_create_date','document_create_date_posted','baseline_create_date']:
    df[c]=parse_compact(df[c])
for c in ['due_date']:
    df[c]=parse_compact(df[c])
for c in ['invoice_date','payment_date']:
    df[c]=pd.to_datetime(df[c],errors='coerce')
df['amount']=pd.to_numeric(df['amount'],errors='coerce')
df['is_open']=pd.to_numeric(df['is_open'],errors='coerce').astype('Int64')
for c in ['business_year','posting_id']:
    df[c]=pd.to_numeric(df[c],errors='coerce').astype('Int64')

for c in ['invoice_date','due_date']:
    record(f'Invalid or missing {c}','Flag; exclude from date-based metrics','Do not invent transaction dates',df[c].isna().sum())
invalid_amount=df['amount'].isna() | (df['amount']<=0)
record('Missing, zero or negative amount','Flag; keep for audit but exclude from amount totals','Cannot assume a replacement amount',invalid_amount.sum())
df['invalid_amount_flag']=invalid_amount
bad_dates=df['invoice_date'].notna()&df['due_date'].notna()&(df['due_date']<df['invoice_date'])
df['due_before_invoice_flag']=bad_dates
record('Due date before invoice date','Flag, do not silently alter','Could reflect source errors or unusual business rules',bad_dates.sum())

status_mismatch=((df['is_open']==1)&df['payment_date'].notna())|((df['is_open']==0)&df['payment_date'].isna())
df['status_date_conflict_flag']=status_mismatch.fillna(True)
record('Payment status conflicts with payment date','Flag for review','Do not infer a payment date or override source status',df['status_date_conflict_flag'].sum())

# Observed labels only; leave unpaid invoices unlabelled, not zero-day delays.
valid_paid=(df['is_open']==0)&df['payment_date'].notna()&df['invoice_date'].notna()&df['due_date'].notna()&~df['due_before_invoice_flag']&~df['status_date_conflict_flag']
df['days_to_pay']=pd.Series(pd.NA,index=df.index,dtype='Int64')
df['delay_days']=pd.Series(pd.NA,index=df.index,dtype='Int64')
df.loc[valid_paid,'days_to_pay']=(df.loc[valid_paid,'payment_date']-df.loc[valid_paid,'invoice_date']).dt.days.astype('Int64')
df.loc[valid_paid,'delay_days']=(df.loc[valid_paid,'payment_date']-df.loc[valid_paid,'due_date']).dt.days.astype('Int64')
negative_payment=valid_paid & (df['days_to_pay']<0)
record('Payment before invoice date','Flag; clear derived labels','Suspicious chronology; requires mentor review',negative_payment.sum())
df['payment_before_invoice_flag']=negative_payment
df.loc[negative_payment,['days_to_pay','delay_days']]=pd.NA
df['paid_late_flag']=pd.Series(pd.NA,index=df.index,dtype='Int64')
labelled=df['delay_days'].notna()
df.loc[labelled,'paid_late_flag']=(df.loc[labelled,'delay_days']>0).astype('Int64')

# Country is not explicit; do not claim business_code or currency is a country.
df['country']=pd.Series(pd.NA,index=df.index,dtype='string')
record('Country not available','Leave as missing','Currency and business code are not reliable country identifiers',len(df))

for c in ['invoice_date','due_date','payment_date','document_create_date','document_create_date_posted','baseline_create_date']:
    df[c]=df[c].dt.strftime('%Y-%m-%d')
df.to_csv(OUT/'cleaned_invoices.csv',index=False)
pd.DataFrame(log).to_csv(REPORT/'cleaning_log.csv',index=False)
summary=pd.DataFrame([{'raw_rows':original_rows,'clean_rows':len(df),'removed_rows':original_rows-len(df),'raw_columns':19,'clean_columns':len(df.columns),'open_invoices':int((df['is_open']==1).sum()),'paid_invoices':int((df['is_open']==0).sum()),'valid_delay_labels':int(df['delay_days'].notna().sum()),'paid_late_invoices':int((df['paid_late_flag']==1).sum())}])
summary.to_csv(REPORT/'summary.csv',index=False)
print(summary.to_string(index=False))
print('Saved cleaned CSV, cleaning log and summary.')