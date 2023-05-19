# Test combo of FLT solar & PSH for generic location
from cmath import e, pi
import math
import json
from xml.etree.ElementTree import PI
# from xml.etree.ElementTree import PI
import numpy as np
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import csv

from psh_cost_fxn import psh_cost
from flt_pv_cost_fxn import fltPVcost


def psh_flt_pvFXNv5(A_total, z_max, h_o, P_kW):
    LocDataCSV = pd.read_csv("33.162_-83.8_psmv3_60_2013.csv",header=2,usecols=["Year","Month","Day","Hour","Minute", "GHI", "DHI","DNI","Temperature"])
    # print(LocDataCSV)

    T_c = LocDataCSV["Temperature"].values.tolist() #C
    # print(T_c)
    t = np.empty(len(T_c)) # overall hours for dataset
    for i in range(len(T_c)):
        t[i] = i+1
    #print(t)
    ghi = LocDataCSV["GHI"].values.tolist() #W/m2
    dhi = LocDataCSV["DHI"].values.tolist() #W/m2
    dni = LocDataCSV["DNI"].values.tolist() #W/m2
    L_irr = ghi+dhi+dni # total irradiance W/m2
    # print(L_irr)

    # Variables to optimize
    # A_total = 1600 #m2 area of reservoir
    # z_max = 2 # m max depth of reservoir

    # Possibe other variables to optimize
    # h_o = 90 # m static head (distance between reservoirs)
    # P_kW = 55 # kW (Max load of generator/motor)

    # Values to minimize
    # Total cost or lcoe of PV + PSH 
    # % of hours that the grid has to provide power 

    # Calculating P_pv from Floating Solar Model
    # Constants -> could be changed to inputs
    n_inv = 0.93 # Inverter efficiency
    n_pv = 0.16 # PV efficiency
    # n_use = 0.62 # useable fraction of surface area for PV
    V_max = A_total * z_max # total surface area of reservoir
    A_ca = 1.53 # m2 (area of an individual solar panel)
    A_real = A_total - np.sqrt(2 * math.pi * A_total * A_ca) # area useable by PV
    # A_real = A_total * n_use 
    a_p = 0.47/100 # %/C
    T_ref = 25 #C
    
    n = math.floor(A_real/A_ca) # Number of solar panels
    #print("Number of Solar Panels =", n)
    n_array = n_inv*n_pv # efficiency of array (determined previously)

    # Calculate capacity of floating solar system (kW)
    P_c = n_array * max(L_irr) * n*A_ca/1000
    #print("Capacity of Floating PV =", P_cap, "kW")

    # Adjust the motor capacity to be ~25% of the total solar capacity (55/212.5 in Shyam)
    # P_kW = 0.25 * P_c # kW (Max load of generator/motor)

    P_pv = np.empty(len(T_c))
    for i in range(len(T_c)):
        P_pv[i] = (n*n_pv*n_inv*(1- a_p*(T_c[i] - T_ref))*L_irr[i]*A_ca)/1000

    # Demand
    # getting load power data (kW) from single column csv file
    with open('caiso_rice_ironmtn_2015.csv') as f:
        P_l = [float(s) for line in f.readlines() for s in line[:-1].split(',')]
        # print(P_l)
    # Remove any negative demand
    for i in range(len(P_l)):
        if P_l[i] < 0:
            P_l[i] = 0

    # PSH System
    # Constants
    V_intial = 0.2 * V_max

    P_save = P_kW # Power from grid to fill reservoir
    P_cap = P_kW # Max power pump can recieve from PV


    # Function for determining h & V from past volume (m3), pump power (W), generator (W)
    def est_hV(V_t_1, P_p_kW, P_g_kW, h_o, P_cap_kW, V_max, A_total):
        # Conver kW to W
        P_p = P_p_kW * 1000
        P_g = P_g_kW * 1000
        P_kW = P_cap_kW * 1000
        
        # Constants
        # h_o = 90 # m
        C_h = 1/A_total # m2 or the area of the reservoir
        p = 1000 # kg/m3
        g = 9.81 # m/s^2
        C_np = 1604372730.9155
        C_nt = 1.4841 * 10**-7
        C_ng = 0.89942
        # P_kW = 55000 # W (Max load of generator/motor)
        t = 60 * 60 # Interval from hours to seconds

        # Guesses for h 
        h_n = 50 # number of guesses 
        h_min = h_o
        h_max = 1/A_total * (V_max) + h_o
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
            H_eqA[i] = (((h[i] - h_o))/C_h)
            h_frac = 2 * (h[i] - h_o)/(h_max - h_o) + h_o
            # H_eqB[i] = V_t_1 + t/(p*g*(h_frac ** 4.4264)) * (((C_np*P_p)/(h_frac ** 1.3022))-(((P_g ** 0.8309) * (P_kW ** 0.16913))/(C_ng*C_nt)))
            # H_eqB[i] = V_t_1 + t/(p*g*(h[i] ** 4.4264)) * (((C_np*P_p)/(h[i] ** 1.3022))-(((P_g ** 0.8309) * (P_kW ** 0.16913))/(C_ng*C_nt)))
            H_eqB[i] = V_t_1 + t/(p*g*h[i]) * (((C_np*P_p)/(h_frac ** 4.7286))-(((P_g ** 0.8309) * (P_kW ** 0.16913))/(C_ng*C_nt*(h_frac**3.4264))))
            error[i] = abs(H_eqA[i] - H_eqB[i])
            
        h_final = h[pd.Series(error).idxmin()]
        V_final = ((h_final - h_o)/C_h)
        if V_final > V_max:
            V_final = V_max
        
        if V_final > 0:
            error_min = min(error)/V_final
        else:
            error_min = 0
        return h_final, V_final, error_min

    # Empty sets for outputs
    P_grid2L = np.empty(len(t))
    P_pv2L = np.empty(len(t))
    P_psh2L = np.empty(len(t))
    P_pv2psh = np.empty(len(t))
    P_grid2psh = np.empty(len(t))
    P_pv2grid = np.empty(len(t))
    E_psh = np.empty(len(t))


    V_t = np.empty(len(t)+1)
    V_t[0] = V_intial
    h_t = np.empty(len(t)+1)
    h_t[0] = 1/A_total * V_t[0] + h_o
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
                V_t[i+1] = est_hV(V_t[i], 0, P_l[i] - P_pv[i], h_o, P_kW, V_max, A_total)[1]
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
        
        hV = est_hV(V_t[i], P_pv2psh[i] + P_grid2psh[i], P_psh2L[i], h_o, P_kW, V_max, A_total)
        h_t[i+1] = hV[0]
        V_t[i+1] = hV[1]
        h_errors[i+1] = hV[2]
        E_psh[i] = (P_pv2psh[i] + P_psh2L[i])*1 # times 1 since the data is hourly (removed grid power to PSH to reduce grid dependence)

    # Record the times where the grid has to provide power to the system
    grid_counter = 0
    for i in range(len(t)):
        if P_grid2L[i] > 0 or P_grid2psh[i] > 0:
            grid_counter = grid_counter + 1
    grid_req_frac = grid_counter/max(t)

    #print("Percent of hours where grid must provide power = ", grid_req_frac * 100, "%")
    psh_costs = psh_cost(h_t, h_o, A_total, z_max)
    #print("Total PSH Cost = $", psh_costs[0])
    #print("Total PSH Cost ($/kW) =", psh_costs[1])
    #print("Total PSH Cost ($/kWh) =", psh_costs[2])
    pv_lcoe = fltPVcost(P_c)
    #print("Floating PV Cost ($/kWh) =", pv_lcoe)
    total_lcoe = pv_lcoe + psh_costs[2]
    #print("Floating PV + PSH Cost ($/kWh) =", total_lcoe)
    psh_cap_cost = psh_costs[0]

    # Utilization factor
    Uf = sum(E_psh)/(P_kW * max(t))
    Neg_uf = -1 * Uf
   
    return grid_req_frac, total_lcoe, psh_cap_cost, Neg_uf

# Results = psh_flt_pvFXNv3(100000,100,100)
# print("Percent of hours where grid must provide power = ", Results[0] *100, "%")
# print("Floating PV + PSH Cost ($/kWh) =", Results[1])
# print("Max Excess Ratio (max PV power to grid vs max load) =", Results[2])