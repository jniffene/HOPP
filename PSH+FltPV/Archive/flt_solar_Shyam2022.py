# Floating Solar Model from Shyam 2022
from cmath import e, pi
import math
import json
from xml.etree.ElementTree import PI
# from xml.etree.ElementTree import PI
import numpy as np
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Checking Irradiance
# Variables
# Input data
ShyamData = pd.read_excel("Shyam2022 PSH Solar Data.xlsx", sheet_name=0)

t = ShyamData["Hour"].values.tolist()
T_c = ShyamData["Temp"].values.tolist()
P_pv_check = ShyamData["Flt Solar"].values.tolist()

# Capacity of floating solar
# Constants
P_c_check = 212.5 # Capacity of floating solar array (kW) 
n_inv = 0.93 # Inverter efficiency
n_pv = 0.16 # PV efficiency
n_total = n_inv * n_pv
A_real = 1300 # Real area (m2)

# Checking Max Irradiance
L_max = (P_c_check * 1000) / (n_total * A_real)
print("Max Irradiance from Cap", L_max, "W/m2")

# Irradiance check over the course of the day
# Constants
a_p = 0.47/100 # %/C
T_ref = 25 #C
n = 850 # Number of solar panels
A_ca = 1.53 # m2

L_check = np.empty(len(T_c))
for i in range(len(T_c)):
    L_check[i] = (P_pv_check[i]*1000) / (n*n_pv*n_inv*(1-a_p*(T_c[i]-T_ref))*A_ca)

L_check_max = max(L_check)
print("Max Irradiance for Hourly", L_check_max, "W/m2")
L_check_sum = sum(L_check)
print("Sum Irradiance for Hourly", L_check_sum, "W/m2")

# Efficiency diff to get proper L_max
n_diff = L_max/L_check_max
print("Efficiency Diff to Determine Overall Solar Array", n_diff*100,"%")
n_array = n_diff*n_pv*n_inv
print("Efficiency of PV Array", n_array*100, "%")

L_max_new_cap = (P_c_check*1000)/(n_array * A_real)
print("New Estimate from Cap", L_max_new_cap, "W/m2")
