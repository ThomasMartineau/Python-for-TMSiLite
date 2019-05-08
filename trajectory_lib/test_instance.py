# -*- coding: utf-8 -*-
"""
Created on Wed May  8 09:56:15 2019

@author: tlm111
"""

class Celsius:
    def __init__(self, temperature = [0,0]):
        self.temperature = temperature

    def to_fahrenheit(self):
        x = self.temperature
        return [(x[1]* 2) + 32, 1]
    
man = Celsius()
print(man.temperature)
print(man.to_fahrenheit())
print(man.temperature)
print(man.to_fahrenheit())
print(man.temperature)