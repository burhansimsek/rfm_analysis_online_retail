####################################################################################################
# Dataset Info
# Invoice: transaction id, unique but multiple, if contains "C" this is canceled transaction.
# StockCode: product stock code, unique
# Description: product description
# Quantity: number of product sold
# InvoiceDate: invoice date
# Price: product price
# Customer ID: customer id, unique
# Country: customer country

import datetime as dt
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)

df_ = pd.read_excel("M3_crm_analytics/my_codes/datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

df.head()
df.shape
df.info()
df.describe().T

df.isnull().sum()
df[df["Customer ID"].isnull()].describe()
df[df["Description"].isnull()].describe()
df.dropna(inplace=True)

df["Description"].nunique()
df.groupby("Description").agg({"Quantity": "sum"})
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

df = df[~df["Invoice"].str.contains("C", na=False)]

df["TotalPrice"] = df["Quantity"] * df["Price"]
df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()

# Recency: today - last transaction date
# Frequency: transaction count
# Monetary: transactions total price

df["InvoiceDate"].max()  # 2011-12-09
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda x: (today_date - x.max()).days,
                                     "Invoice": lambda x: x.nunique(),
                                     "TotalPrice": lambda x: x.sum()})

rfm.columns = ["r_metrics", "f_metrics", "m_metrics"]
rfm.head()
rfm.describe().T
rfm = rfm[rfm["m_metrics"] > 0]
rfm.describe().T

rfm["r_scores"] = pd.qcut(rfm["r_metrics"], 5, labels=[5, 4, 3, 2, 1])
rfm["f_scores"] = pd.qcut(rfm["f_metrics"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["m_scores"] = pd.qcut(rfm["m_metrics"], 5, labels=[1, 2, 3, 4, 5])
rfm.head()
rfm.describe().T
rfm["RF_SCORES"] = rfm["r_scores"].astype(str) + rfm["f_scores"].astype(str)

rfm.head()
rfm[rfm["RF_SCORES"] == "55"]

# REGEX
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["segment"] = rfm["RF_SCORES"].replace(seg_map, regex=True)
rfm.head()

rfm[["segment", "r_metrics", "f_metrics", "m_metrics"]].groupby("segment").agg("mean")
rfm[rfm["segment"] == "loyal_customers"].describe().T

loyal_customers = pd.DataFrame()
loyal_customers["loyal_customers"] = rfm[rfm["segment"] == "loyal_customers"].index
loyal_customers.head()
loyal_customers = loyal_customers.astype(int)
loyal_customers.to_excel("loyal_customers.xlsx")

