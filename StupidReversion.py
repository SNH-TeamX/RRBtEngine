import numpy as np
import datetime

class LookBackWindow:
    def __init__(self, n):
        self.length = n
        self.buffer = []
        
    def push(self, value):
        self.buffer.append(value)
        if len(self.buffer) > self.length:
            self.buffer.pop(0)
            
    def std(self):
        return np.array(self.buffer).std()
    
    def first(self):
        return self.buffer[0]
    
    def last(self):
        return self.buffer[-1]
    
    def diff(self):
        if len(self.buffer) < self.length:
            return None
        else:
            return self.last() - self.first()

    
    def clear(self):
        self.buffer = []
        
    def trend(self):
        if len(self.buffer) < self.length:
            return None
        
        if self.diff() > self.std():
            return 1
        
        if self.diff() < -self.std():
            return -1
        
        else:
            return 0


class StupidReversion(KLineBt):
    def __init__(self, file_address):
        KLineBt.__init__(self)
        KLineBt.load_data(self, file_address)
        
        self.test_buf = None
        self.ma_slow = di.MA(600)
        self.ma_fast = di.MA(120)
        
        self.lbw = LookBackWindow(120)
        # self.
        
    def on_kline(self, k_data):
        value_slow = self.ma_slow.update(k_data.close)
        value_fast = self.ma_fast.update(k_data.close)
        self.lbw.push(k_data.close)
        
        if value_slow is None or value_fast is None:
            return
        
        if self.lbw.trend() is None:
            return
        
        if self.position == 0:
            # print(self.lbw.trend())
            if self.lbw.trend() == 1:
                #assert False
                if k_data.close < self.ma_fast.get_value():
                    #assert False
                    self.limit_position(1)
                    
            if self.lbw.trend() == -1:
                if k_data.close > self.ma_fast.get_value():
                    self.limit_position(-1)
                    
        elif self.position == 1:
            if self.lbw.diff() < 0:
                self.limit_position(0)
                
        elif self.position == -1:
            if self.lbw.diff() > 0:
                self.limit_position(0)
        
    def on_day_change(self, new_row, last_row):
        self.limit_position(0)
        


ss = StupidReversion('D:/data/1min/processed/rb.csv')
# ss = SimpleStrat('D:/data/10s/rb_10s.csv')
print(datetime.datetime.now())
ss.bt()
print(datetime.datetime.now())
tran_ret, day_ret = fee_ret(ss.ret, ss.day_ret, 0)
tran_ret.plot()