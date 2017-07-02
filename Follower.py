from kbt import *

class Follower(KLineBt):
    def __init__(self, file_address, start=None, end=None):
        KLineBt.__init__(self)
        KLineBt.load_data(self, file_address, start, end)
        self.ma = di.MA(500)
        self.ma1 = di.MA(100)
        self.std = di.Std(100)
        
    def on_kline(self, tick_data):
        value = self.ma.update(tick_data.close)
        value1 = self.ma1.update(tick_data.close)
        std = self.std.update(tick_data.close)
        
        if value is None:
            return
        
        if tick_data.low > value + std:
#            if tick_data.low > value1:
#                self.limit_position(2)
#            else:
                self.limit_position(1)
            
        elif tick_data.high < value-std:
#            if tick_data.high < value1:
#                self.limit_position(-2)
#            else:
                self.limit_position(-1)
            
            
    def on_day_change(self, new_row, last_row):
        return
        self.limit_position(0)
            
ss = Follower('D:/data/1min/processed/rb.csv', 20160101, 20170101)
ss.bt()
tran_ret, day_ret = fee_ret(ss.ret, ss.day_ret, 1)
tran_ret.plot()
