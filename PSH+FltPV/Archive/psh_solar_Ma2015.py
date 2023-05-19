# Model for PSH Solar based on Ma 2015

from cmath import e, pi
import math
import json
from xml.etree.ElementTree import PI
# from xml.etree.ElementTree import PI
import numpy as np
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Input Data
MaData = pd.read_excel("Ma2015 PSH Solar Data.xlsx", sheet_name=0)
print (MaData)

t = MaData["Hour"].values.tolist()
print("Time (hr)", t)

P_pv = MaData["Solar Power Input (kW)"].values.tolist()
print("Hourly Solar Power (kW)",P_pv)

P_l = MaData["Demand (kW)"].values.tolist()
print("Hourly Power Demand (kW)", P_l)

# constants
h = 60 # meters
p = 1000 # kg/m3
g = 9.8 # m/s2
n_p = 0.88 # efficiency from the excel sheet not Ma2015
n_t = 0.88 # efficiency from the excel sheet not Ma2015
Q_ur_max = 6000 # m3
a = 0.01 # evaporation & leakage loss
P_pR = 1 # kW

# inital conditions
Q_ur_0 = 5100 # m3
soc_0 = Q_ur_0/Q_ur_max

# Output data sets
P_t = np.empty(len(t))
P_p = np.empty(len(t))
q_t = np.empty(len(t))
q_p = np.empty(len(t))
Q_ur = np.empty(len(t))
soc = np.empty(len(t))

for i in range(len(t)):
    if i == 0:
        if P_pv[i] - P_l[i] >= 0.15 * P_pR and soc_0 < 1:
            P_p[i] = P_pv[i] - P_l[i]
            q_p[i] = (P_p[i] * 1000)/(n_p * p * g * h)
            P_t[i] = 0
            q_t[i] = 0
        elif P_pv[i] < P_l[i] and soc_0 > 0:
            P_t[i] = P_l[i] - P_pv[i]
            q_t[i] = (P_t[i] * 1000)/(n_t * p * g * h)
            P_p[i] = 0
            q_p[i] = 0
        else:
            P_t[i] = 0
            q_t[i] = 0
            P_p[i] = 0
            q_p[i] = 0

        Q_ur[i] = Q_ur_0 * (1 - a) + ((q_p[i] - q_t[i]) * 3600)
        soc[i] = Q_ur[i]/Q_ur_max
    else:
        if P_pv[i] - P_l[i] >= 0.15 * P_pR and soc[i-1] < 1:
            P_p[i] = P_pv[i] - P_l[i]
            q_p[i] = (P_p[i] * 1000)/(n_p * p * g * h)
            P_t[i] = 0
            q_t[i] = 0
        elif P_pv[i] < P_l[i] and soc[i-1] > 0:
            P_t[i] = P_l[i] - P_pv[i]
            q_t[i] = (P_t[i] * 1000)/(n_t * p * g * h)
            P_p[i] = 0
            q_p[i] = 0
        else:
            P_t[i] = 0
            q_t[i] = 0
            P_p[i] = 0
            q_p[i] = 0

        Q_ur[i] = Q_ur[i-1] * (1 - a) + ((q_p[i] - q_t[i]) * 3600)
        soc[i] = Q_ur[i]/Q_ur_max

# # Plot the results
# plt.plot(t, P_t, t, P_p, t, P_l, t, Q_ur/100)
# plt.ylabel('Power (kW)')
# plt.xlabel('Hours')
# plt.grid(True)
# plt.legend(['Turbine', 'Pump', 'Demand', 'Water Vol'])
# plt.title('Ma 2015 PSH + Solar Results')
# plt.show()

print(Q_ur)
print(soc)

# Comparison with Results to OG results
# Input Data
MaOGdata = pd.read_excel("Ma2015 Comp Data.xlsx", sheet_name=0)
print (MaOGdata)

t_og = MaOGdata["Hour"].values.tolist()
print("Time (hr)", t_og)
P_pv2l_og = MaOGdata["PV to Load (kW)"].values.tolist()
print("PV to Load (kW) =", P_pv2l_og)
P_t_og = MaOGdata["Turbine Output (kW)"].values.tolist()
print("Turbine Output (kW) =", P_t_og)
P_p_og = MaOGdata["PV to Pump (kW)"].values.tolist()
print("PV to Pump (kW) =", P_p_og)
Q_ur_og = MaOGdata["Water Quantity (m3)"].values.tolist()
print("Water Quantity (m3) =", Q_ur_og)

# Determining percent error
P_pv2l_error = np.empty(len(t))
P_t_error = np.empty(len(t))
P_p_error = np.empty(len(t))
Q_ur_error = np.empty(len(t))

for i in range(len(t)):
    P_pv2l_error[i] = (P_l[i] - P_t[i] - P_pv2l_og[i]) 
    P_t_error[i] = (P_t[i] - P_t_og[i]) 
    P_p_error[i] = (P_p[i] - P_p_og[i]) 
    Q_ur_error[i] = (Q_ur[i] - Q_ur_og[i]) / Q_ur_og[i]
print("PV to Load Error (%)", P_pv2l_error)
print("Turbine Error (%)", P_t_error)
print("Pump Error (%)", P_p_error)
print("Water Vol Error (%)", Q_ur_error)


# Testing the dual y axis method
# create figure and axis objects with subplots()
fig,ax = plt.subplots()
# make a plot
ax.plot(t, P_t, color="green", marker="o")
ax.plot(t, P_p, color="black", marker="o")
ax.plot(t, P_l - P_t, color="red", marker="o")
# set x-axis label
ax.set_xlabel("Hour", fontsize = 14)
# set 1st y-axis label
ax.set_ylabel("Power (kW)",
              color="red",
              fontsize=14)
ax.set_ylim([0, 45])
ax.legend(['Turbine', 'Pump', 'Demand'], loc='upper left')
# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(t, Q_ur, color="blue", marker="o")
ax2.set_ylabel("Water Storage Volume (m3)",color="blue",fontsize=14)
ax2.set_ylim([4000, 5800])
ax2.legend(['Water Vol'], loc='upper right')
plt.title('Ma 2015 PSH + Solar Results')
plt.xlim([1, 24])
plt.grid(True)
plt.show()

# Plot the results
plt.plot(t, P_pv2l_error*100, t, P_t_error*100, t, P_p_error*100, t, Q_ur_error*100)
plt.ylabel('Error (%)')
plt.xlabel('Hours')
plt.grid(True)
plt.legend(['PV to Load', 'Turbine', 'Pump', 'Water Vol'])
plt.title('Ma 2015 PSH + Solar Comparison: Percent Error')
plt.show()









   










