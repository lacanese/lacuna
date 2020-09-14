import backtrader as bt
from datetime import datetime
import pandas as pd 
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt;
import itertools
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

instruments = [
     'BIZD-STK-ARCA',
     'BKLN-STK-ARCA',
     'CEW-STK-ARCA',
     'CWB-STK-ARCA',
     'DBA-STK-ARCA',
     'DBB-STK-ARCA',
     'FXE-STK-ARCA',
     'GLD-STK-ARCA',
     'HYG-STK-ARCA',
     'IEF-STK-ARCA',
     'IYZ-STK-ARCA',
     'JJC-STK-ARCA',
     'LQD-STK-ARCA',
     'LTL-STK-ARCA',
     'MBB-STK-ARCA',
     'MUB-STK-ARCA',
     'PFF-STK-ARCA',
     'SHY-STK-ARCA',
     'TIP-STK-ARCA',
     'TLT-STK-ARCA',
     'UDN-STK-ARCA',
     'USO-STK-ARCA',
     'UUP-STK-ARCA',
     'VNQ-STK-ARCA',
     'XLB-STK-ARCA',
     'XLE-STK-ARCA',
     'XLF-STK-ARCA',
     'XLI-STK-ARCA',
     'XLK-STK-ARCA',
     'XLP-STK-ARCA',
     'XLU-STK-ARCA',
     'XLV-STK-ARCA',
     'XLY-STK-ARCA',
]



ibstore = bt.stores.IBStore(port=7496)
for instrument in instruments:
    try:
        print(instrument)
        cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
        data = ibstore.getdata(dataname=instrument, 
                               historical=True,
                               fromdate=datetime(2015, 1, 1),
                               timeframe=bt.TimeFrame.Days,
                               compression=1)
        cerebro.adddata(data)
        cerebro.addstrategy(scrape) 
        strat = cerebro.run()
        df = pd.DataFrame(data=strat[0].df).set_index(['time','asset'])
        df.to_pickle("data/"+instrument+"_2015.pkl")
        time.sleep(10)
    except:
      pass
