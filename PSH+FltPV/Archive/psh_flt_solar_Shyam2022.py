# Test file for Shyam 2022 PSH + Floating Solar Model
from cmath import e, pi
import math
import json
from xml.etree.ElementTree import PI
# from xml.etree.ElementTree import PI
import numpy as np
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Function for determining h & V from past volume (m3), pump power (W), generator (W)
def est_hV(V_t_1, P_p_kW, P_g_kW):
    # Conver kW to W
    P_p = P_p_kW * 1000
    P_g = P_g_kW * 1000
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
    if V_final > 0:
        error_min = min(error)/V_final
    else:
        error_min = 0
    return h_final, V_final, error_min

# Test function
# test_H = est_hV(1600, 32.609, 38.478)
# print("Final guess for h =",test_H[0],"m")
# print("Volume = ", test_H[1], "m3")
# print("Min Error = ", test_H[2]*100, "%")

# Input data
ShyamData = pd.read_excel("Shyam2022 PSH Solar Data.xlsx", sheet_name=0)
print (ShyamData)

t = ShyamData["Hour"].values.tolist()
# print("Time (hr)", t)
P_pv = ShyamData["Solar (kW)"].values.tolist()
# print("Hourly Solar Power (kW)",P_pv)
P_l = ShyamData["Demand (kW)"].values.tolist()
# print("Hourly Power Demand (kW)", P_l)

# Constants
V_max = 1600
V_intial = 0.2 * V_max
P_kW = 55 # (Max load of generator/motor)
P_save = P_kW # Power from grid to fill reservoir
P_cap = P_kW # Max power pump can recieve from PV

# Empty sets for outputs
P_grid2L = np.empty(len(t))
P_pv2L = np.empty(len(t))
P_psh2L = np.empty(len(t))
P_pv2psh = np.empty(len(t))
P_grid2psh = np.empty(len(t))
P_pv2grid = np.empty(len(t))

V_t = np.empty(len(t)+1)
V_t[0] = V_intial
h_t = np.empty(len(t)+1)
h_t[0] = 0.0012098 * V_t[0] ** 0.99887 + 90
h_errors = np.empty(len(t)+1)
h_errors[0] = 0


for i in range(len(t)):
    if P_pv[i] >= P_l[i]:
        if V_t[i] < V_max:
            P_pv2L[i] = P_l[i]
            P_grid2L[i] = 0
            P_psh2L[i] = 0
            P_grid2psh[i] = 0
            P_pv2grid[i] = 0
            P_pv2psh[i] = P_pv[i] - P_l[i]
            if P_pv2psh[i] > P_cap:
                P_pv2psh[i] = P_cap
                P_pv2grid[i] = P_pv[i] - P_l[i] - P_cap
        if V_t[i] >= V_max:
            P_pv2L[i] = P_l[i]
            P_pv2psh[i] = 0
            P_grid2L[i] = 0
            P_psh2L[i] = 0
            P_grid2psh[i] = 0
            P_pv2grid[i] = P_pv[i] - P_l[i]
    if P_pv[i] < P_l[i]:
        if V_t[i] > 0:
            P_pv2L[i] = P_pv[i]
            P_pv2psh[i] = 0
            P_pv2grid[i] = 0
            V_t[i+1] = est_hV(V_t[i], 0, P_l[i] - P_pv[i])[1]
            if V_t[i+1] > 0:
                P_psh2L[i] = P_l[i] - P_pv[i]
                P_grid2L[i] = 0
                P_grid2psh[i] = 0
            elif V_t[i+1] <= 0:
                P_psh2L[i] = 0
                P_grid2L[i] = P_l[i] - P_pv[i]
                P_grid2psh[i] = P_save
        if V_t[i] <= 0:
            P_pv2L[i] = P_pv[i]
            P_pv2psh[i] = 0
            P_pv2grid[i] = 0
            P_psh2L[i] = 0
            P_grid2L[i] = P_l[i] - P_pv[i]
            P_grid2psh[i] = P_save
    
    hV = est_hV(V_t[i], P_pv2psh[i] + P_grid2psh[i], P_psh2L[i])
    h_t[i+1] = hV[0]
    V_t[i+1] = hV[1]
    h_errors[i+1] = hV[2]



# Plot the figures
plt.figure(1)
plt.plot(t,P_grid2psh,color="blue", marker="o")
plt.plot(t,P_grid2L,color="red", marker="_")
plt.plot(t,P_pv2psh,color="orange", marker="o")
plt.plot(t,P_pv2L,color="cyan", marker="+")
plt.plot(t, P_psh2L,color="magenta",marker="^")
plt.plot(t,P_pv2grid,color="green", marker="o")
plt.xlabel("Hour", fontsize = 14)
plt.ylabel("Power (kW)", fontsize = 14)
plt.legend(["G-PSH","G-L","PV-PSH","PV-L","PSH-L","PV-G"])
plt.title("Shyam 2022 Fig 13 Recreated")
plt.grid(True)
plt.show()

plt.figure(2)
plt.plot(t,P_pv,color="cyan",marker="o")
plt.plot(t,P_l,color="green",marker="o")
# making a new version of t that includes 0
t_V = np.empty(len(t)+1)
t_V[0] = 0
for i in range(len(t)):
    t_V[i+1] = t[i]
plt.plot(t_V, V_t/V_max * 100, color="orange", marker="o")
plt.xlabel("Hour", fontsize = 14)
plt.ylabel("Power (kW) & Volume (%)", fontsize = 14)
plt.legend(["PV Generation","Load", "% Volume"])
plt.title("Shyam 2022 Fig 14 Recreated")
plt.grid(True)
plt.show()

ShyamData2 = pd.read_excel("Shyam2022 PSH Solar Data p2.xlsx", sheet_name=0)
print(ShyamData2)

# Comparison with data from Shyam 2022
hour = ShyamData2["Hour"].values.tolist()
g_psh = ShyamData2["G-PSH"].values.tolist()
g_l = ShyamData2["G2l"].values.tolist()
pv_psh = ShyamData2["Pv to psh"].values.tolist()
pv_l = ShyamData2["Pv to l"].values.tolist()
psh_l = ShyamData2["Psh to l"].values.tolist()
pv_g = ShyamData2["Pv to g"].values.tolist()

# Comparison plot
fig, axs = plt.subplots(3, 2)
fig.suptitle('Calculated (color) vs Results from Shyam (black)')
axs[0, 0].plot(t,P_grid2psh,color="blue")
axs[0,0].plot(t,g_psh,color="black")
axs[0,0].set_title('Grid to PSH')
axs[0,1].plot(t,P_grid2L,color="red")
axs[0,1].plot(t,g_l,color="black")
axs[0,1].set_title('Grid to Load')
axs[1,0].plot(t,P_pv2psh,color="orange")
axs[1,0].plot(t,pv_psh,color="black")
axs[1,0].set_title('PV to PSH')
axs[1,1].plot(t,P_pv2L,color="cyan")
axs[1,1].plot(t,pv_l,color="black")
axs[1,1].set_title('PV to Load')
axs[2,0].plot(t,P_psh2L,color="magenta")
axs[2,0].plot(t,psh_l,color="black")
axs[2,0].set_title('PSH to Load')
axs[2,1].plot(t,P_pv2grid,color="green")
axs[2,1].plot(t,pv_g,color="black")
axs[2,1].set_title('PV to Grid')

for ax in axs.flat:
    ax.set(xlabel='Hours', ylabel='Power (kW)')

# Hide x labels and tick labels for top plots and y ticks for right plots.
for ax in axs.flat:
    ax.label_outer()
plt.show()


# plt.subplot(611)
# plt.plot(t,P_grid2psh,color="blue")
# plt.plot(t,g_psh,color="black")
# plt.subplot(621)
# plt.plot(t,P_grid2L,color="red")
# plt.plot(t,g_l,color="black")
# plt.subplot(631)
# plt.plot(t,P_pv2psh,color="orange")
# plt.plot(t,pv_psh,color="black")
# plt.subplot(612)
# plt.plot(t,P_pv2L,color="cyan")
# plt.plot(t,pv_l,color="black")
# plt.subplot(622)
# plt.plot(t,P_psh2L,color="magenta")
# plt.plot(t,psh_l,color="black")
# plt.subplot(632)
# plt.plot(t,P_pv2grid,color="green")
# plt.plot(t,pv_g,color="black")
# plt.show()

plt.figure(4)
plt.plot(t,P_grid2psh - g_psh,color="blue")
plt.plot(t,P_grid2L - g_l,color="red")
plt.plot(t,P_pv2psh - pv_psh,color="orange")
plt.plot(t,P_pv2L - pv_l,color="cyan")
plt.plot(t, P_psh2L - psh_l,color="magenta")
plt.plot(t,P_pv2grid - pv_g,color="green")
plt.xlabel("Hour", fontsize = 14)
plt.ylabel("Power (kW)", fontsize = 14)
plt.legend(["G-PSH","G-L","PV-PSH","PV-L","PSH-L","PV-G"])
plt.title("Shyam 2022 Comparisons")
plt.grid(True)
plt.show()

plt.figure(5)
plt.plot(t,g_psh,color="blue")
plt.plot(t,g_l,color="red")
plt.plot(t,pv_psh,color="orange")
plt.plot(t,pv_l,color="cyan")
plt.plot(t, psh_l,color="magenta")
plt.plot(t,pv_g,color="green")
plt.xlabel("Hour", fontsize = 14)
plt.ylabel("Power (kW)", fontsize = 14)
plt.legend(["G-PSH","G-L","PV-PSH","PV-L","PSH-L","PV-G"])
plt.title("Shyam 2022 OG Fig 13")
plt.grid(True)
plt.show()

