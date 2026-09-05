from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from src.forecast import fit_forecast, rolling_backtest
app=FastAPI(title='Parcel Demand Forecasting API',version='1.0')
DATA='data/daily_parcel_volume.csv'
class Request(BaseModel): facility_id:str='CENTRAL-01'; service_level:str='standard'; horizon:int=14; model:str='sarimax'
def load(q):
    d=pd.read_csv(DATA,parse_dates=['date']); return d[(d.facility_id==q.facility_id)&(d.service_level==q.service_level)].groupby('date',as_index=False).agg(parcel_volume=('parcel_volume','sum'),weather_severity=('weather_severity','mean'),promotion_index=('promotion_index','mean'),holiday_flag=('holiday_flag','max'))
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/forecast')
def forecast(q:Request):
    d=load(q); p=fit_forecast(d,q.horizon,q.model); return {'model':q.model,'forecast':[{'date':str(i.date()),'volume':round(v,1)} for i,v in p.items()]}
@app.post('/compare')
def compare(q:Request): return rolling_backtest(load(q)).to_dict('records')
