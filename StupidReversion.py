class SimpleStrat(KLineBt):
    def __init__(self, file_address):
        KLineBt.__init__(self)
        KLineBt.load_data(self, file_address)
        
        self.test_buf = None
        self.ma_slow = di.MA(600)
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
        