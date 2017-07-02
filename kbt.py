import pandas as pd
import numpy as np
import datetime
import sys

import dynamic_indicator as di

from matplotlib import pyplot as plt

# read file from csv file
def read_file(tb_day_data, start=None, end=None):
    data = pd.read_csv(tb_day_data, header=None)
    data.columns = ["date", "time", "open", "high", 
                    "low", "close", "vol", "holdings"]
    
    if start is not None:
        data = data[data.date>=start]
        
    if end is not None:
        data = data[data.date<=end]
    
    print("read data finish.")
    return data

# transform time into python datetime format
def get_rowtime(row):
    time = datetime.datetime(int(row.date/10000), int(row.date/100%100), row.date%100,
                             int(row.time/10000), int(row.time/100%100), row.time%100)
    return time



class KLineBt:
    def __init__(self, cash=0, transac_delay = 0):
        self.k_line_data = None
        
        self.position = 0
        self.cash = cash
        self.init_cash = cash
        
        self.current_row = None
        
        self.ret = []
        self.day_ret = []
        
        self.current_time = None
        
        self.last_row = None
        
        self.transactions = []
        
        self.date_list = {}

    
    # load data to object
    def load_data(self, tb_day_data, start=None, end=None):
        self.k_line_data = read_file(tb_day_data, start, end)
        
    # backtesting loop
    def bt(self):
        total_length = len(self.k_line_data)
        for index, row in self.k_line_data.iterrows():
            
            self.date_list[row.date] = row.close
            self.current_time = get_rowtime(row)
            
            if self.last_row is not None and row.date != self.last_row.date:
                self._on_day_change(row, self.last_row)
            
            self.current_row = row
            self.on_kline(row)
            self.last_row = row
            
            index_revised = index-self.k_line_data.index[0]
            if index_revised % 1000 == 0:
                progress = int(index_revised/total_length*100)
                print('\r[{0}] {1}%'.format('#'*int(progress/10), progress))

        
    # on_day change function, calculate daily return
    def _on_day_change(self, new_row, last_row):
        self.day_ret.append({
                "time": self.current_time.date(),
                "cash":self.cash + last_row.close * self.position
                })
        self.on_day_change(new_row, last_row)
        
    # a interface to inherent class
    def on_day_change(self, new_row, last_row):
        pass
    
    # a interface to inherent class
    def on_kline(self, k_line_data):
        pass
    
    # send order 
    def limit_position(self, position):
        if self.position == position:
            return
        
        if self.position * position > 0:
            self.transactions.append({
                    "time": self.current_time,
                    "qty": position - self.position,
                    "price": self.current_row.close,
                    "current_qty": position
                    })
            self.cash += -(position - self.position) * self.current_row.close
            self.position = position
            return
        
        if self.position == 0:
            self.transactions.append({
                    "time": self.current_time,
                    "qty": position - self.position,
                    "price": self.current_row.close,
                    "current_qty": position
                    })
            self.position = position
            self.cash += -position * self.current_row.close
                
        elif self.position > 0:
            if position < 0:
                self.limit_position(0)
                self.limit_position(position)
                
            elif position == 0:
                self.transactions.append({
                    "time": self.current_time,
                    "qty": position - self.position,
                    "price": self.current_row.close,
                    "current_qty": position
                    })
                
                self.cash += self.position * self.current_row.close
                self.position = 0
                self.ret.append({
                    "time": self.current_time,
                    "cash": self.cash}
                )

                
        elif self.position < 0:
            if position > 0:
                self.limit_position(0)
                self.limit_position(position)
                
            elif position == 0:
                self.transactions.append({
                    "time": self.current_time,
                    "qty": position - self.position,
                    "price": self.current_row.close,
                    "current_qty": position
                    })
                self.cash += self.position * self.current_row.close
                self.position = 0
                self.ret.append({
                    "time": self.current_time,
                    "cash": self.cash}
                )

                
# calculate the return after fee
def fee_ret(tran_ret, day_ret, fee):
    tran_ret_fee = []
    day_ret_fee = []
    acc_fee = 0
    
    day_count = 0
    
    for i in tran_ret:
        
        if i["time"].date() > day_ret[day_count]["time"]:
            day_ret_fee.append({
                "time": day_ret[day_count]["time"],
                "cash": day_ret[day_count]["cash"] - acc_fee
            })
            day_count += 1
        
        
        acc_fee += fee
        tran_ret_fee.append({
            "time": i["time"],
            "cash": i["cash"] - acc_fee
            })
                    
    day_ret_fee.append({
            "time": day_ret[day_count]["time"],
            "cash": day_ret[day_count]["cash"] - acc_fee
        })
                    
                    
    tran_ret_fee = pd.DataFrame(tran_ret_fee)
    tran_ret_fee.index = tran_ret_fee["time"]
    
    day_ret_fee = pd.DataFrame(day_ret_fee)
    day_ret_fee.index = day_ret_fee["time"]
                    
    return (tran_ret_fee.cash, day_ret_fee.cash)
        
# a simple dual MA strategy
class SimpleStrat(KLineBt):
    def __init__(self, file_address):
        KLineBt.__init__(self)
        KLineBt.load_data(self, file_address)
        
        self.test_buf = None
        self.ma_slow = di.MA(300)
        self.ma_fast = di.MA(100)
        # self.
        
    def on_kline(self, k_data):
        value_slow = self.ma_slow.update(k_data.close)
        value_fast = self.ma_fast.update(k_data.close)
        
        if value_slow is None or value_fast is None:
            return
        
        if value_fast > value_slow:
            self.limit_position(1)
            
        elif value_fast < value_slow:
            self.limit_position(-1)
        
    def on_day_change(self, new_row, last_row):
        self.limit_position(0)
        
# demo
if __name__=="__main__":
    ss = SimpleStrat('D:/data/1min/processed/rb.csv')
    # ss = SimpleStrat('D:/data/10s/rb_10s.csv')
    print(datetime.datetime.now())
    ss.bt()
    print(datetime.datetime.now())
    tran_ret, day_ret = fee_ret(ss.ret, ss.day_ret, 0.3)
    tran_ret.plot()