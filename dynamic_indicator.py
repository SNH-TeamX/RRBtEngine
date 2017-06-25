import numpy as np

class MA:
    def __init__(self, n):
        self.length = n
        self.buffer = []
        
    def update(self, value):
        self.buffer.append(value)
        if len(self.buffer) > self.length:
            self.buffer.pop(0)
        return self.get_value()
            
    def get_value(self):
        if len(self.buffer) < self.length:
            return None

        else:
            return np.array(self.buffer).mean()
        
        
        
