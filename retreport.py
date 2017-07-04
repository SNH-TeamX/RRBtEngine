import numpy as np
import pandas as pd

class RetAnalyzer:
    def __init__(self, transactions, datelist, day_ret, cash=5000):
        
        
        self.buf =[]
        
        self.transactions = pd.DataFrame(transactions)
        self.transac_ret = []
        self.long_short_stat = None
        self.cal_status()
        self.datelist = datelist
        self.basecash = cash
        
        self.day_ret = day_ret

    def cal_status(self):
        cash = 0
        position = 0

        current_direction = 0
        current_cost = 0
        current_profit = 0
        
        
        long_count = 0
        short_count = 0
        long_profit = []
        short_profit = []

        for index, transac in self.transactions.iterrows():
            self.buf.append({"time":transac["time"], "index":index})
            last_direction = current_direction
            cash += -transac["qty"] * transac["price"]
            position += transac["qty"]
            
            #print(transac)
            if position != transac["current_qty"]:
                print(transac["time"])
                raise Exception("transaction qty calc error")
            
            if position > 0:
                current_direction = 1
            elif position == 0:
                current_direction = 0
            elif position < 0:
                current_direction = -1
                
            if current_direction * transac["qty"] > 0:
                current_cost += abs(transac["qty"]) * transac["price"]
            else:
                current_profit += abs(transac["qty"]) * transac["price"]
            
            if current_direction * transac["qty"] > 0:
                if current_direction > 0:
                    long_count += transac["qty"]
                elif current_direction < 0:
                    short_count += -transac["qty"]
                
            if position == 0:
                #print(current_cost,",", current_profit)
                if last_direction == 1:
                    long_profit.append(current_profit - current_cost)
                elif last_direction == -1:
                    short_profit.append(current_cost - current_profit)
                
                current_direction = 0
                current_cost = 0
                current_profit = 0
                
                self.transac_ret.append({
                        "ret": cash,
                        "time": transac["time"]
                        })
        self.long_short_stat = {
                "long_profit": long_profit,
                "short_profit": short_profit,
                "long_count": long_count,
                "short_count": short_count
                }
    
    def accumulate_ret(self):   
        return self.transac_ret[-1]["ret"]

    def annual_ret(self):
        trading_days = len(self.datelist)
        return self.accumulate_ret() / trading_days * 250
    
    def profit_ratio(self):
        long_profit = np.array(self.long_short_stat["long_profit"])
        short_profit = np.array(self.long_short_stat["short_profit"])
    
        profit_count = len(long_profit[long_profit>0]) + len(short_profit[short_profit>0])
        
        total_count = self.trade_count()
        return float(profit_count) / float(total_count)
        
    def avg_ret(self):
        total_count = self.trade_count()
        return self.accumulate_ret() / total_count
    
    def trade_count(self):
        long_profit = np.array(self.long_short_stat["long_profit"])
        short_profit = np.array(self.long_short_stat["short_profit"])
        return len(long_profit) + len(short_profit)
        
    def max_dropdown(self):
        max_profit = 0
        max_dropdown = 0
        time = None
        for transac in self.transac_ret:
            if transac["ret"] > max_profit:
                max_profit = transac["ret"]
                
            dropdown = max_profit - transac["ret"]

            if dropdown >  max_dropdown:
                max_dropdown = dropdown
                time = transac["time"]
                
        return {
                "time":time,
                "dropdown": max_dropdown}
    
    def max_dropdown_ratio(self):
        max_profit = 0
        max_dropdown = 0
        for transac in self.transac_ret:
            if transac["ret"] > max_profit:
                max_profit = transac["ret"]
                

            dropdown = 1-((transac["ret"]+self.basecash) / (max_profit + self.basecash))
            if dropdown >  max_dropdown:
                max_dropdown = dropdown
                
        return max_dropdown
    
    def ret_std(self):
        long_profit = np.array(self.long_short_stat["long_profit"])
        short_profit = np.array(self.long_short_stat["short_profit"])
        ret_series = np.concatenate([long_profit, short_profit])
        return ret_series.std()
    
    def win_lose_ratio(self):
        long_profit = np.array(self.long_short_stat["long_profit"])
        short_profit = np.array(self.long_short_stat["short_profit"])
        
        profit = long_profit[long_profit>0].sum() + short_profit[short_profit>0].sum()
        loss = long_profit[long_profit<0].sum() + short_profit[short_profit<0].sum()
        
        return -profit/loss
    
    def long_profit(self):
        return np.array(self.long_short_stat["long_profit"]).sum()
    
    def short_profit(self):
        return np.array(self.long_short_stat["short_profit"]).sum()
    
    def avg_profit(self):
        long_profit = np.array(self.long_short_stat["long_profit"])
        short_profit = np.array(self.long_short_stat["short_profit"])
        
        profit = long_profit[long_profit>0].sum() + short_profit[short_profit>0].sum()
        profit_count = len(long_profit[long_profit>0]) + len(short_profit[short_profit>0])
        return profit/profit_count
    
    def avg_loss(self):
        long_profit = np.array(self.long_short_stat["long_profit"])
        short_profit = np.array(self.long_short_stat["short_profit"])
        
        loss = long_profit[long_profit<0].sum() + short_profit[short_profit<0].sum()
        loss_count = len(long_profit[long_profit<0]) + len(short_profit[short_profit<0])
        return -loss/loss_count
    
    def calmar(self):
        return self.annual_ret()/self.max_dropdown()["dropdown"]
    
    def sharpe(self):
        day_ret = np.array(pd.DataFrame(self.day_ret)["cash"])
        day_ret = day_ret[1:] - day_ret[:-1]
        return self.annual_ret() / day_ret.std() / np.sqrt(250)
    
    def stat(self):
        return {
                "annual_ret": self.annual_ret(),
                "accumulate_ret": self.accumulate_ret(),
                "long_profit": self.long_profit(),
                "short_profit": self.short_profit(),
                "win_ratio": self.profit_ratio(),
                "avg_ret": self.avg_ret(),
                "trade_count": len(self.transactions),
                "max_drop_down_cash": self.max_dropdown(),
                "max_drop_down": self.max_dropdown_ratio(),
                "calma": self.calmar(),
                "sharpe": self.sharpe(),
                "win_lose_ratio": self.win_lose_ratio(),
                "avg_profit": self.avg_profit(),
                "avg_loss": self.avg_loss(),
                "ret_std": self.ret_std()
                
                }
    

