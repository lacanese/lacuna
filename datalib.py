import backtrader as bt
import pandas as pd 
import numpy as np
from collections import defaultdict
import time

class scrape(bt.Strategy):
    def __init__(self):
        self.df = defaultdict(list)
    def next(self):
        for d in self.datas:
            for a,v in [
                ('asset',d._name),
                ('open', d.open[0]),
                ('high', d.high[0]),
                ('low',  d.low[0]),
                ('close', d.close[0]),
                ('volume', d.volume[0]),
                ('time', bt.utils.date.num2date(self.datas[0].datetime[0]))]:
                self.df[a].append(v)

def get_data(instruments, startdate = None, enddate = None,timeframe=bt.TimeFrame.Days,compression=1):
    ibstore = bt.stores.IBStore(port=7496)
    dfs = []
    for instrument in instruments:
        print(instrument)
        cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
        data = ibstore.getdata(dataname=instrument, 
                               historical=True,
                               fromdate=startdate,
                               #todate=enddate,
                               timeframe=timeframe,
                               compression=compression)
        cerebro.adddata(data)
        cerebro.addstrategy(scrape) 
        strat = cerebro.run()
        df = pd.DataFrame(data=strat[0].df).set_index(['time','asset'])
        df.to_pickle("data/%s_%s_%s_.pkl" % (instrument,startdate.strftime("%Y-%m-%d"),enddate.strftime("%Y-%m-%d")))
        dfs.append(df)
    return pd.concat(dfs, axis=0).swaplevel(0,1)
