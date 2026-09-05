import pandas as pd, numpy as np
from dataclasses import dataclass
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

@dataclass
class ForecastResult:
    model:str; forecast:pd.Series; mae:float|None=None; rmse:float|None=None; wape:float|None=None

def metrics(y, p):
    y=np.asarray(y,float); p=np.asarray(p,float); e=y-p
    return {'mae':float(np.mean(np.abs(e))),'rmse':float(np.sqrt(np.mean(e**2))),'wape':float(np.abs(e).sum()/max(np.abs(y).sum(),1))*100}

def fit_forecast(train:pd.DataFrame,horizon=14,model='sarimax'):
    y=train.set_index('date')['parcel_volume'].astype(float)
    if model=='arima': fit=ARIMA(y,order=(2,1,2)).fit(); pred=fit.forecast(horizon)
    elif model=='sarima': fit=SARIMAX(y,order=(1,1,1),seasonal_order=(1,1,1,7),enforce_stationarity=False,enforce_invertibility=False).fit(disp=False); pred=fit.forecast(horizon)
    elif model=='sarimax':
        ex=train.set_index('date')[['weather_severity','promotion_index','holiday_flag']].astype(float)
        future_ex=pd.DataFrame({'weather_severity':[ex.weather_severity.tail(28).mean()]*horizon,'promotion_index':[ex.promotion_index.tail(28).mean()]*horizon,'holiday_flag':[0]*horizon})
        fit=SARIMAX(y,exog=ex,order=(1,1,1),seasonal_order=(1,1,1,7),enforce_stationarity=False,enforce_invertibility=False).fit(disp=False); pred=fit.forecast(horizon,exog=future_ex)
    elif model=='prophet':
        from prophet import Prophet
        p=train[['date','parcel_volume']].rename(columns={'date':'ds','parcel_volume':'y'}); m=Prophet(weekly_seasonality=True,yearly_seasonality=True).fit(p); future=m.make_future_dataframe(periods=horizon,freq='D'); pred=m.predict(future).tail(horizon).set_index('ds')['yhat']
    else: raise ValueError(model)
    return pd.Series(pred.to_numpy(), index=pd.date_range(pd.to_datetime(train.date.max())+pd.Timedelta(days=1), periods=horizon))

def rolling_backtest(df,models=('arima','sarima','sarimax'),horizon=14):
    df=df.sort_values('date').copy(); train=df.iloc[:-horizon]; test=df.iloc[-horizon:]; out=[]
    for m in models:
        p=fit_forecast(train,horizon,m); score=metrics(test.parcel_volume,p); out.append({'model':m,**score})
    return pd.DataFrame(out).sort_values('wape')
