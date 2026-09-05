from src.forecast import metrics
def test_metrics():
    m=metrics([100,120],[90,130]); assert round(m['mae'],2)==10.0; assert m['wape']>0
