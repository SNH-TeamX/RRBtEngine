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

class Turtle(KLineBt):
    def __init__(self, file_address):
        KLineBt.__init__(self)
        KLineBt.load_data(self, file_address)
        
        self.start = None
        self.lbw = LookBackWindow(480)
        self.vol = 100
        # self.
        
    def on_kline(self, k_data):
        self.lbw.push(k_data.close)
        if self.start is None:
            self.start = k_data.open
            
        stage = int((k_data.close - self.start) / self.vol * 5)
        if stage > 10:
            stage = 10
        
        if self.position == 0:
            if stage > 0 and stage > self.position:
                self.limit_position(stage)
                
            elif stage < 0 and stage < self.position:
                self.limit_position(stage)
        
        elif self.position == 1:
            if k_data.close < self.start:
                self.limit_position(0)
        
        elif self.position == -1:
            if k_data.close > self.start:
                self.limit_position(0)
        
    def on_day_change(self, new_row, last_row):
        self.limit_position(0)
        self.start = None
        self.vol = self.lbw.std()
        
        
    
ss = Turtle('D:/data/1min/processed/rb.csv')
# ss = SimpleStrat('D:/data/10s/rb_10s.csv')
print(datetime.datetime.now())
ss.bt()
print(datetime.datetime.now())
tran_ret, day_ret = fee_ret(ss.ret, ss.day_ret, 1.3)
tran_ret.plot()