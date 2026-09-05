# Databricks notebook source
# MAGIC %md
# MAGIC # Daily demand forecasting tutorial
# COMMAND ----------
import pandas as pd
from src.forecast import rolling_backtest
df=pd.read_csv('../data/daily_parcel_volume.csv',parse_dates=['date'])
s=df[(df.facility_id=='CENTRAL-01')&(df.service_level=='standard')].groupby('date',as_index=False).agg(parcel_volume=('parcel_volume','sum'),weather_severity=('weather_severity','mean'),promotion_index=('promotion_index','mean'),holiday_flag=('holiday_flag','max'))
print(rolling_backtest(s))
