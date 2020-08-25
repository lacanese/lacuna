import datetime
import backtrader as bt
import backtrader.analyzers as btanalyzers
import pandas as pd
from collections import defaultdict

# Create a subclass of Strategy to define the indicators and logic

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast = 50,
        pslow = 120,
    )

    def __init__(self):
        self.sma1 = bt.ind.SMA(self.data.close, period=self.p.pfast) 
        self.sma2 = bt.ind.SMA(self.data.close, period=self.p.pslow)
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
        sma1 = self.sma1[0]
        sma2 = self.sma2[0]
        hold = sma1>sma2
        if self.can_trade:
            if hold:
                self.order_target_size(data=self.data, target=1)
            elif not hold:
                self.order_target_size(data=self.data, target=0)
        df = defaultdict(list)
        df['date'].append(bt.utils.date.num2date(self.datas[0].datetime[0]))
        df['asset'].append(self.data._name)
        df['close'].append(self.data[0])
        df['sma1'].append(sma1)
        df['sma2'].append(sma2)
        df['hold'].append(hold)
        pos = self.getposition(data=self.data)
        position  = pos.size*pos.price
        df['pos'].append(position)
        df = pd.DataFrame(data=df)
        df = df.set_index('date')#pd.DatetimeIndex(df['date']))
        print("\n######")
        print(df)


cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

ibstore = bt.stores.IBStore(port=7496)
cerebro.broker = ibstore.getbroker() 

# Create a data feed
instruments = ["MES-202009-GLOBEX"]
for instrument in instruments:
    data = ibstore.getdata(dataname=instrument,
                         fromdate=datetime.datetime(2020, 8, 1))
    cerebro.resampledata(data,
                         timeframe=bt.TimeFrame.Minutes,
                         compression=60,
    )

cerebro.addstrategy(SmaCross)  # Add the trading strategy
#cerebro.addsizer(bt.sizers.FixedSize, stake=1) 
cerebro.run(maxcpus=1)  # run it all
#cerebro.plot()
