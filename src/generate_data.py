from pathlib import Path
import numpy as np, pandas as pd

def generate(days=730, seed=42):
    rng=np.random.default_rng(seed); start=pd.Timestamp('2024-01-01'); rows=[]
    facilities=['NORTH-01','NORTH-02','CENTRAL-01','SOUTH-01','SOUTH-02','WEST-01']
    services=['standard','priority','economy']
    for d in pd.date_range(start, periods=days):
        dow=d.dayofweek; holiday=int((d.month,d.day) in {(1,1),(7,4),(11,28),(12,25)})
        peak=1 if d.month in [11,12] else 0
        for f_i,f in enumerate(facilities):
          for s_i,s in enumerate(services):
            base=5200+f_i*430+s_i*(-620)+900*(dow in [0,1])+2200*peak+1600*holiday
            trend=(d-start).days*1.4; weather=max(0,rng.normal(0.18,0.12)); promo=max(0,rng.normal(0.15+0.2*peak,0.08))
            vol=max(400,int(base+trend+1250*promo-900*weather+rng.normal(0,420)))
            backlog=max(0,int(rng.normal(180+0.03*vol,120)))
            rows.append([d.date(),f,s,vol,round(weather,3),round(promo,3),holiday,dow,backlog])
    return pd.DataFrame(rows,columns=['date','facility_id','service_level','parcel_volume','weather_severity','promotion_index','holiday_flag','day_of_week','opening_backlog'])

if __name__=='__main__':
    out=Path(__file__).resolve().parents[1]/'data'; out.mkdir(exist_ok=True); df=generate(); df.to_csv(out/'daily_parcel_volume.csv',index=False); print(df.head()); print(len(df))
