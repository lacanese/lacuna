import datetime
import backtrader as bt
import backtrader.analyzers as btanalyzers
import pandas as pd
from collections import defaultdict

# Create a subclass of Strategy to define the indicators and logic

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast = 40,
        pslow = 120,
    )

    def __init__(self):
        self.sma1s = [bt.ind.SMA(d, period=self.p.pfast) for d in self.datas]
        self.sma2s = [bt.ind.SMA(d, period=self.p.pslow) for d in self.datas]
        self.can_trade = False

    def notify_data(self, data, status, *args, **kwargs):
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
        if status == data.LIVE:
            self.can_trade = True
        else:
            self.can_trade = False 

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                print(order.data._name, 'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buycomm = order.executed.comm
            else:  
                print(order.data._name, 'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))


        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('Order Canceled/Margin/Rejected')


    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        print('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        df = defaultdict(list)
        for d,sma1,sma2 in zip(self.datas, self.sma1s, self.sma2s):
            sma1 = sma1[0]
            sma2 = sma2[0]
            hold = sma1>sma2
            if self.can_trade:
                if hold:
                    self.order_target_percent(data=d, target=0.05)
                elif not hold:
                    self.order_target_percent(data=d, target=0)
            pos = self.getposition(data=d)
            position  = pos.size*pos.price
            for k,v in [
                    ('date',bt.utils.date.num2date(d.datetime[0])),
                    ('asset',d._name),
                    ('close',d[0]),
                    ('sma1',sma1),
                    ('sma2',sma2),
                    ('hold',hold),
                    ('pos',position)]:
                df[k].append(v)
        df = pd.DataFrame(data=df)
        df = df.set_index('date')#pd.DatetimeIndex(df['date']))
        print("\n######")
        print(df)


cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

ibstore = bt.stores.IBStore(port=7496)
cerebro.broker = ibstore.getbroker() 

# Create a data feed
instruments = ["VNQ-STK-ARCA","VTI-STK-ARCA","DBC-STK-ARCA","VEU-STK-ARCA","IEF-STK-ARCA"]

for instrument in instruments:
    data = ibstore.getdata(dataname=instrument,
                         fromdate=datetime.datetime(2020, 8, 1))
    cerebro.resampledata(data,
                         timeframe=bt.TimeFrame.Minutes,
                         compression=60,
    )


cerebro.addstrategy(SmaCross)
cerebro.run()
