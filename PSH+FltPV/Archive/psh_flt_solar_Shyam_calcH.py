# Test file for finding h & V for Shyam 2022 PSH + Floating Solar Model
from cmath import e, pi
import math
import json
from xml.etree.ElementTree import PI
# from xml.etree.ElementTree import PI
import numpy as np
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# Test for determining h value using the derivation from including the equations for efficiency
# Constants
h_o = 90 # m
C_h = 0.0012098 # m2 or the area of the reservoir
p = 1000 # kg/m3
g = 9.81 # m/s^2
C_np = 1604372730.9155
C_nt = 1.4841 * 10**-7
C_ng = 0.89942
P_kW = 55000 # W (Max load of generator/motor)
V_max = 1600 # m3
t = 0.25 * 60 * 60 # Interval from hours to seconds

# For 6PM to 6:15PM in figure 13
V_t_1 = V_max
P_p = 32.609 * 1000 # W
P_g = 38.478 * 1000 # W

# Guesses for h 
h_n = 50 # number of guesses 
h_min = h_o
h_max = 0.0012098 * (V_max ** 0.99887) + h_o
h = np.empty(h_n+1)
h_i = (h_max-h_min)/h_n

for i in range(len(h)):
    h[i] = h_min + i*h_i
# print(h)
error = np.empty(len(h))

# Equations
H_eqA = np.empty(len(h))
H_eqB = np.empty(len(h))
h_final = 0

for i in range(len(h)):
    H_eqA[i] = (((h[i] - h_o))/C_h) ** (1/0.99887)
    H_eqB[i] = V_t_1 + t/(p*g*(h[i] ** 4.4264)) * (((C_np*P_p)/(h[i] ** 1.3022))-(((P_g ** 0.8309) * (P_kW ** 0.16913))/(C_ng*C_nt)))
    error[i] = abs(H_eqA[i] - H_eqB[i])
    
h_final = h[pd.Series(error).idxmin()]
V_final = ((h_final - h_o)/C_h) ** (1/0.99887)
error_min = min(error)/V_final
# print("Vals for Eq A =", H_eqA)
# print("Vals for Eq B =", H_eqB)
# print("Errors", error)
print("Final guess for h =", h_final, "m")
print("Min Error = ", error_min*100, "%")
print("Volume = ", V_final, "m3")
print("% Volume = ", V_final/V_max * 100, "%")
