# Cost equations for a PSH facility originally from the
# Excel Workbook "GS-6669 Implemenation for NREL 8-3-22.xlsx"
# obtained from Vignesh Ramasamy an Stuart Cohen and 
# converted to Python by James Niffenegger on 9-27-22 

from cmath import e, pi
import math
import json
from statistics import mean
from xml.etree.ElementTree import PI
# from xml.etree.ElementTree import PI
import numpy as np
from pathlib import Path
import pandas as pd

# Note currently just has default parameters!

def psh_cost(h_vals, h_o, A, z_max):
    # h_vals = hourly values for head
    # h_o = static head
    # A = area of the reservoir
    
    # Default Inputs
    Z_u_avg = z_max * 3.28084 # ft; Avg. Upper Reservoir Depth (C8)
    if Z_u_avg <= 0:
        print("Error: Avg Upper Reservoir Depth is Less Than or Equal to Zero!")
        return error_val, error_val, error_val
    A_u = A * 0.000247105 # acres; Upper Reservoir Area (C9)
    if A_u <= 0:
        print("Error: Upper Reservoir Area is Less Than or Equal to Zero!")
        return error_val, error_val, error_val
    Z_L_avg = Z_u_avg # ft; Avg. Lower Resev. Depth (C11)
    A_l = A_u # acres; Lower Resv. Area (C12)
    L_c = 100 # ft; Conveyance Length (C15)
    T_cond = "Poor" # Tuneling Cond. (C17)
    # H_nomMaxM = 100 # m; Nominal (max) Head 
    H_nomMax = (z_max + h_o) * 3.28084 # ft; Nominal (max possible) Head (C21)
    t_gen = 10 # hr; Generating Time (C22)
    Loc = "United States" # Location (C26) 
    A_acq = A_u/0.8 # acres; Acerage to Aquire (C27)
    Surge_chambs = "Yes" # Surge Chambers (C29)
    L_at_mi = 0.75 # mi; Length, access tunnel (C30)
    D_at = 30 # ft; Diameter, access tunnel (C31)
    ter_AR = "Mild" # Access Road, Terrain (C32)
    Typ_ar = "New" # Access Road, Type (C33)
    L_ar = 1.2 # mi; Access Road, Length (C34)
    uri = "Horizontal" # Upper Resv. Intake (C36)
    lri = "Horizontal" # Lower Resv. Intake (C37)
    G_pps = "Adverse" # Powerstation Struct. Geology (C38)
    Z_pps = "Surface" # Power Station (Above or Below Ground) (C39)

    # Definition of function

    # Assumptions
    p_AS = 0.85 # Percent Active Storage (G8)
    Hmin_Hmax = h_o/(z_max + h_o) # Hmin/Hmax (G11) originally assumed to be 0.7
    V_u_avg = Z_u_avg * A_u # ac-ft; Average Upper Resv. Volume (G12)
    V_L_avg = Z_L_avg * A_l # ac-ft; Average Lower Resv. Volume
    v_T_max = 20 # ft/s; Max tunnel velocity 
    D_T_max = 35 # ft; Max tunnel diameter
    L_c_mi = L_c * 0.000189394 # mi; Conveyance Length
    C_hw = 90 # Hazen Williams Constant
    t_sales = 0.06 # Sales Tax
    t_cont = 0.25 # Contingency Tax
    t_EPC = 0.083 # EPC Cost
    t_DC = 0.03 # Developer cost
    t_OP = 0.07 # Overhead and Profit
    n_PT = 0.88 # P-T Efficiency
    P_capMax = 150 # MW, Max Unit Capacity
    N_min = 4 # minimum number of units
    v_P_max = 25 # ft/s; max penstock velocity
    n_mE = 0.9 # Material/equipment %
    C_t_pump = 1.2 # pump time
    V_trans = 150 # kV; Transmission
    V_sub = 150 # kV; Substation
    ter_trans = "Flat" # Transmission Terrain
    Typ_trans = "Single" # Transmission Type
    error_val = 10 ** 9

    # Outputs Related to PSH power production
    S_act = p_AS * V_u_avg # ac-ft; Active Storage
    # print("Active Storage (ac-ft) =", S_act)
    Q_dis = S_act * 43560 / (t_gen * 3600) # ft3/s; Mean Gen Discharge
    # print("Mean Gen Discharge (ft3/s) =", Q_dis)
    H_G_min = Hmin_Hmax * H_nomMax # ft; min gross head (= to the static head)
    # print("Min Gross Head (ft) =", H_G_min)
    H_G_avg = (H_G_min + H_nomMax)/2 # ft; mean gross head
    # print("Avg Gross Head (ft) =", H_G_avg)
    Q_gen_min = Q_dis * (H_G_min/H_G_avg) ** 0.5 # ft3/s; Min Gen Discharge
    # print("Min Gen Discharge (ft3/s) =", Q_gen_min)
    Q_gen_max = Q_dis * (H_nomMax/H_G_avg) ** 0.5 # ft3/s; Max Gen Discharge
    # print("Max Gen Discharge (ft3/s) =", Q_gen_max)
    D_t = ((4 * Q_gen_max)/(v_T_max * pi)) ** 0.5 # ft; Tunnel Diameter
    # print("Tunnel Diameter (ft) =", D_t)
    # Number of tunnels
    if D_t <= D_T_max:
        N_t = 1
    else:
        N_t = 2
    # print("Number of Tunnels =", N_t)
    D_t_adj = ((4 * Q_gen_max)/(pi * N_t * v_T_max)) ** 0.5 # ft; Adjusted Tunnel Diameter
    # print("Adjusted Tunnel Diameter (ft) =", D_t_adj)
    L_h = L_c/H_G_avg # L/H
    # print("L/H =", L_h)
    h_gen_min = (4.73 * L_c * (Q_gen_min ** 1.85))/((C_hw ** 1.85) * (D_t_adj ** 4.87)) # ft; Min Gen Headloss 
    # print("Min Gen Headloss (ft) =", h_gen_min)
    h_gen_avg = (4.73 * L_c * (Q_dis ** 1.85))/((C_hw ** 1.85) * (D_t_adj ** 4.87)) # ft; Mean Gen Headloss
    # print("Mean Gen Headloss (ft) =", h_gen_avg)
    h_gen_max = (4.73 * L_c * (Q_gen_max ** 1.85))/((C_hw ** 1.85) * (D_t_adj ** 4.87)) # ft; Max Gen Headloss
    # print("Max Gen Headloss (ft) =", h_gen_max)
    
    dH_gen_min = H_G_min - h_gen_min # ft; net head at min gen discharge
    # print("Net Head @ Min Gen Discharge (ft) =", dH_gen_min)
    if dH_gen_min <= 0:
        print("Error: Net Head is Less Than or Equal to Zero!")
        return error_val, error_val, error_val
    
    dH_gen_avg = H_G_avg - h_gen_avg # ft; net head at avg gen discharge
    # print("Net Head @ Avg Gen Discharge (ft) =", dH_gen_avg)
    if dH_gen_avg <= 0:
        print("Error: Net Head is Less Than or Equal to Zero!")
        return error_val, error_val, error_val
    
    dH_gen_max = H_nomMax - h_gen_max # ft; net head at max gen discharge
    # print("Net Head @ Max Gen Discharge (ft) =", dH_gen_max)
    if dH_gen_max <= 0:
        print("Error: Net Head is Less Than or Equal to Zero!")
        return error_val, error_val, error_val
    
    P_G_min = (Q_gen_min * dH_gen_min * n_PT)/(11.81 * 1000) # MW; min plant gen power
    # print("Min Plant Gen Power (MW) =", P_G_min)
    P_G_avg = (Q_dis * dH_gen_avg * n_PT)/(11.81 * 1000) # MW; mean plant gen power
    # print("Mean Plant Gen Power (MW) =", P_G_avg)
    P_G_max = (Q_gen_max * dH_gen_max * n_PT)/(11.81 * 1000) # MW; max plant gen power
    # print("Max Plant Gen Power (MW) =", P_G_max)
    # Number of units N_u
    if P_G_max / P_capMax <= N_min:
        N_u = N_min
    else:
        N_u = math.ceil(P_G_max / P_capMax)
    # print("Number of Units =", N_u)
    P_capU = P_G_max / N_u # MW; Unit Rating 
    # print("Unity Capacity (MW) =", P_capU)
    D_p = ((4 * Q_gen_max)/(pi * v_P_max)) ** 0.5 # ft; Penstock Diameter
    # print("Penstock Diameter (ft) =", D_p)
    t_pump = C_t_pump * t_gen # hr; Pump Time
    # print("Pump Time (hr) =", t_pump)
    Q_pump_avg = (S_act * 43560)/(t_pump * 3600) # ft3/s; Mean Pump Discharge
    # print("Mean Pump Discharge (ft3/s) =", Q_pump_avg)
    h_pump_avg = (4.73 * (Q_pump_avg ** 1.85) * L_c)/((C_hw ** 1.85) * (D_t_adj ** 4.87)) # ft; mean pump headloss
    # print("Mean Pump Headloss (ft) =", h_pump_avg)
    dH_pump_avg = H_G_avg + h_pump_avg # ft; Mean Pump Net Head
    # print("Mean Pump Net Head (ft) =", dH_pump_avg)
    P_pump_avg = (Q_pump_avg * dH_pump_avg * n_PT)/(11.81 * 1000) # MW; Mean Pump Power
    # print("Mean Pump Power (MW) =", P_pump_avg)

    # Cost Calculations
    A_land_OR = 0 # acres; Land Area Override
    # Land & Land Rights: Land Area (acres)
    if A_land_OR > 0:
        A_land = A_land_OR
    else:
        A_land = A_acq
    # print("Land Area (acres) =", A_land)
    # Cost of land based on location
    df = pd.read_excel('Land Value Data.xlsx', sheet_name= 'Sheet1')
    c_landL = df[df['State'] == Loc]['Average $/Acre 2021'].sum()
    # Land & Land Rights: Unit Cost ($/ac)
    u_land_OR = 0
    if u_land_OR > 0:
        u_land = u_land_OR
    else:
        u_land = 2.4063214 * c_landL
    # print("Land Area Acre Cost ($/ac) =",u_land)
    C_land = A_land * u_land # $; Cost of land & land rights
    # print("Cost of Land & Land Rights = $",C_land)
    # Powerplant Structure
    # Powerplant Power (kW)
    P_pps_OR = 0
    if P_pps_OR > 0:
        P_pps = P_pps_OR
    else:
        P_pps = P_G_max * 1000
    # print("Powerplant Power (kW) =", P_pps)

    # Set Material Cost Value Based on Location
    df = pd.read_excel('Location Factors.xlsx', sheet_name= 'Sheet1')
    c_matL = df[df['State'] == Loc]['Material Cost'].sum() # Material cost for location

    # Powerplant Unit Cost ($/kW)
    u_pps_OR = 0
    if G_pps == "Average" and Z_pps == "Underground":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pps = 740.12 * H_nomMax ** -0.298 
            elif N_u > 2 and N_u <= 3:
                u_pps = 760.42 * H_nomMax ** -0.328
            elif N_u > 3 and N_u <= 4:
                u_pps = 645.72 * H_nomMax ** -0.32
            elif N_u > 4:
                u_pps = 640.28 * H_nomMax ** -0.337
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pps = 1229.6 * H_nomMax ** -0.405
            elif N_u > 2 and N_u <= 3:
                u_pps = 1113.2 * H_nomMax ** -0.412
            elif N_u > 3 and N_u <= 4:
                u_pps = 1126.8 * H_nomMax ** -0.431
            elif N_u > 4:
                u_pps = 1195.5 * H_nomMax ** -0.454
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pps = 2163.3 * H_nomMax ** -0.512
            elif N_u > 2 and N_u <= 3:
                u_pps = 1725.2 * H_nomMax ** -0.501
            elif N_u > 3 and N_u <= 4:
                u_pps = 1735.2 * H_nomMax ** -0.52
            elif N_u > 4:
                u_pps = 1578.2 * H_nomMax ** -0.524
        elif P_G_max > 225:
            if N_u <= 2:
                u_pps = 2032.8 * H_nomMax ** -0.532
            elif N_u > 2 and N_u <= 3:
                u_pps = 2231.2 * H_nomMax ** -0.565
            elif N_u > 3 and N_u <= 4:
                u_pps = 2553 * H_nomMax ** -0.604
            elif N_u > 4:
                u_pps = 2504.2 * H_nomMax ** -0.615
    elif G_pps == "Adverse" and Z_pps == "Underground":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pps = 1096.7 * H_nomMax ** -0.319
            elif N_u > 2 and N_u <= 3:
                u_pps = 878.1 * H_nomMax ** -0.313
            elif N_u > 3 and N_u <= 4:
                u_pps = 926.99 * H_nomMax ** -0.337
            elif N_u > 4:
                u_pps = 911.22 * H_nomMax ** -0.352
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pps = 1435.5 * H_nomMax ** -0.392
            elif N_u > 2 and N_u <= 3:
                u_pps = 1258 * H_nomMax ** -0.396
            elif N_u > 3 and N_u <= 4:
                u_pps = 1375 * H_nomMax ** -0.424
            elif N_u > 4:
                u_pps = 1131 * H_nomMax ** -0.41
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pps = 2315.8 * H_nomMax ** -0.49
            elif N_u > 2 and N_u <= 3:
                u_pps = 2194.6 * H_nomMax ** -0.505
            elif N_u > 3 and N_u <= 4:
                u_pps = 2353.1 * H_nomMax ** -0.53
            elif N_u > 4:
                u_pps = 2162.4 * H_nomMax ** -0.533
        elif P_G_max > 225:
            if N_u <= 2:
                u_pps = 2613 * H_nomMax ** -0.533
            elif N_u > 2 and N_u <= 3:
                u_pps = 2154.7 * H_nomMax ** -0.53
            elif N_u > 3 and N_u <= 4:
                u_pps = 2380.6 * H_nomMax ** -0.559
            elif N_u > 4:
                u_pps = 4996.8 * H_nomMax ** -0.687
    elif G_pps == "Average" and Z_pps == "Surface":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pps = 0.000005 * (H_nomMax ** 2) - 0.0009 * H_nomMax + 83.095
            elif N_u > 2 and N_u <= 3:
                u_pps = 0.000004 * (H_nomMax ** 2) + 0.0004 * H_nomMax + 75.715
            elif N_u > 3 and N_u <= 4:
                u_pps = 0.000004 * (H_nomMax ** 2) + 0.0021 * H_nomMax + 71.437
            elif N_u > 4:
                u_pps = 0.0000006 * (H_nomMax ** 2) + 0.0109 * H_nomMax + 62.383
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pps = 0.000007 * (H_nomMax ** 2) - 0.0146 * H_nomMax + 67.574
            elif N_u > 2 and N_u <= 3:
                u_pps = 0.000007 * (H_nomMax ** 2) - 0.0117 * H_nomMax + 59.042
            elif N_u > 3 and N_u <= 4:
                u_pps = 0.000005 * (H_nomMax ** 2) - 0.0065 * H_nomMax + 54.377
            elif N_u > 4:
                u_pps = 0.000003 * (H_nomMax ** 2) - 0.0018 * H_nomMax + 48.04
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pps = 6E-6 * (H_nomMax ** 2) - 0.0159 * H_nomMax + 53.593
            elif N_u > 2 and N_u <= 3:
                u_pps = 6E-6 * (H_nomMax ** 2) - 0.0157 * H_nomMax + 47.989
            elif N_u > 3 and N_u <= 4:
                u_pps = 5E-6 * (H_nomMax ** 2) - 0.0116 * H_nomMax + 43.522
            elif N_u > 4:
                u_pps = 3E-6 * (H_nomMax ** 2) - 0.0078 * H_nomMax + 39.647
        elif P_G_max > 225:
            if N_u <= 2:
                u_pps = 6E-6 * (H_nomMax ** 2) - 0.0183 * H_nomMax + 43.547
            elif N_u > 2 and N_u <= 3:
                u_pps = 7E-6 * (H_nomMax ** 2) - 0.0198 * H_nomMax + 41.489
            elif N_u > 3 and N_u <= 4:
                u_pps = 6E-6 * (H_nomMax ** 2) - 0.0162 * H_nomMax + 36.672
            elif N_u > 4:
                u_pps = 5E-6 * (H_nomMax ** 2) - 0.0128 * H_nomMax + 33.573
    elif G_pps == "Adverse" and Z_pps == "Surface":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pps = 3E-6 * (H_nomMax ** 2) + 0.0062 * H_nomMax + 109.48
            elif N_u > 2 and N_u <= 3:
                u_pps = 1E-6 * (H_nomMax ** 2) + 0.0099 * H_nomMax + 90.767
            elif N_u > 3 and N_u <= 4:
                u_pps = 2E-6 * (H_nomMax ** 2) + 0.0073 * H_nomMax + 84.676
            elif N_u > 4:
                u_pps = -1E-7 * (H_nomMax ** 2) + 0.0123 * H_nomMax + 73.167
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pps = 4E-6 * (H_nomMax ** 2) - 0.0039 * H_nomMax + 90.761
            elif N_u > 2 and N_u <= 3:
                u_pps = 2E-6 * (H_nomMax ** 2) + 0.0008 * H_nomMax + 75.02
            elif N_u > 3 and N_u <= 4:
                u_pps = 2E-6 * (H_nomMax ** 2) + 0.0002 * H_nomMax + 70.655
            elif N_u > 4:
                u_pps = 2E-6 * (H_nomMax ** 2) + 0.002 * H_nomMax + 62.446
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pps = 8E-6 * (H_nomMax ** 2) - 0.024 * H_nomMax + 80.261
            elif N_u > 2 and N_u <= 3:
                u_pps = 5E-6 * (H_nomMax ** 2) - 0.0155 * H_nomMax + 65.884
            elif N_u > 3 and N_u <= 4:
                u_pps = 6E-6 * (H_nomMax ** 2) - 0.0165 * H_nomMax + 61.35
            elif N_u > 4:
                u_pps = 4E-6 * (H_nomMax ** 2) - 0.0099 * H_nomMax + 52.44
        elif P_G_max > 225:
            if N_u <= 2:
                u_pps = 1E-5 * (H_nomMax ** 2) - 0.0308 * H_nomMax + 67.023
            elif N_u > 2 and N_u <= 3:
                u_pps = 7E-6 * (H_nomMax ** 2) - 0.0207 * H_nomMax + 54.238
            elif N_u > 3 and N_u <= 4:
                u_pps = 7E-6 * (H_nomMax ** 2) - 0.0205 * H_nomMax + 50.886
            elif N_u > 4:
                u_pps = 5E-6 * (H_nomMax ** 2) - 0.0146 * H_nomMax + 43.361
    else:
        print("Error the options for geography are Average or Adverse and the options for location are Underground or Surface")
    if u_pps_OR > 0:
        u_pps_final = u_pps_OR
    else:
        maf_PS = 1.3 # Suggested MAF for powerstation
        u_pps_final = u_pps * c_matL / 100 * maf_PS 
    # print("Powerplant Station Unit Cost ($/kW) =", u_pps_final)
    C_pps = u_pps_final * P_pps # Cost of Powerplant Structure
    # print("Powerplant Structure Cost = $", C_pps)

    # Reservoirs, Dams, & Waterways
    # Upper Reservoir Dam & Spillway Volume (CY, cubic yards)
    V_u_ds_OR = 0
    if V_u_ds_OR > 0:
        V_u_ds = V_u_ds_OR
    else:
        V_u_ds = V_u_avg * 1613.33
    # print("Upper Resv. Dam & Spillway Volume (CY) =", V_u_ds)
    # Unit cost for upper reservoir dam & spillway ($/CY)
    u_u_ds_OR = 0
    if u_u_ds_OR > 0:
        u_u_ds = u_u_ds_OR
    else:
        u_cy = 41.699 * H_nomMax ** -0.317
        maf_DSD = 1.4 # MAF suggested for dams, spillways, diversions, emb
        u_u_ds = u_cy * c_matL / 100 * maf_DSD
    # print("Upper Resv. Dam & Spillway Unit Cost ($/CY) =", u_u_ds)
    # Cost of Upper Resv Dam & Spillway ($)
    C_uds = V_u_ds * u_u_ds
    # print("Upper Resv. Dam & Spillway Cost = $", C_uds)
    # Upper Reservoir Intake
    # Number of Upper Resv. Intake
    N_uri_OR = 0
    if N_uri_OR > 0:
        N_uri = N_uri_OR
    else:
        N_uri = N_t
    # print("Upper Resv. Intake Tunnels =", N_uri)
    # Unit Cost for URI
    maf_UI = 2 # suggested MAF for upper intake
    u_uri_OR = 0
    if u_uri_OR > 0:
        u_uri = u_uri_OR
    elif uri == "Horizontal":
        u_uri = (0.0154 * D_p ** 2 - 0.1968 * D_p + 1.85) * c_matL/100 * maf_UI
    elif uri == "Vertical":
        u_uri = (0.0046 * D_p ** 2 - 0.0819 * D_p + 0.5993) * c_matL/100 * maf_UI
    else:
        print("Error Upper Resv. Intake (uri) must be Horizontal or Vertical")
    # print("Upper Resv. Intake Unit Cost ($/ft) =", u_uri)
    # URI total cost ($)
    C_uri = u_uri * N_uri * 10 ** 6
    # print("Upper Resv. Intake Cost = $", C_uri)
    # Lower Resv. Intake
    # Number of LRI tunnels
    N_lri_OR = 0
    if N_lri_OR > 0:
        N_lri = N_lri_OR
    else:
        N_lri = N_t
    # print("Lower Resv. Intake Tunnels =", N_lri)
    # Unit Cost for Lower Resv. Intake
    maf_LI = 1.3 # Suggested MAF for Lower Intake
    u_lri_OR = 0
    if u_lri_OR > 0:
        u_lri = u_lri_OR
    elif lri == "Horizontal":
        u_lri = (0.0154 * D_p ** 2 - 0.1968 * D_p + 1.85) * c_matL/100 * maf_LI
    elif lri == "Vertical":
        u_lri = (0.0046 * D_p ** 2 - 0.0819 * D_p + 0.5993) * c_matL/100 * maf_LI
    else:
        print("Error Lower Resv. Intake (lri) must be Horizontal or Vertical")
    # print("Lower Resv. Intake Unit Cost ($/ft) =", u_lri)
    # Cost of Lower Resv. Intake ($)
    C_lri = u_lri * N_lri * 10 ** 6
    # print("Lower Resv. Intake Cost = $", C_lri)

    # Lower Resv. Dam & Spillway (LRDS)
    # Volume of Lower Resv. Dam & Spillway (CY)
    V_lrds_OR = 0
    if V_lrds_OR > 0:
        V_lrds = V_lrds_OR
    else:
        V_lrds = V_L_avg * 1613.33 # convert from ac-ft to cy
    # print("Lower Resv. Dam & Spillway Volume (CY) =", V_lrds)
    # Unit Cost of LRDS ($/CY)
    u_lrds_OR = 0
    if u_lrds_OR > 0:
        u_lrds = u_lrds_OR
    else:
        u_cy = 41.699 * H_nomMax ** -0.317
        u_lrds = u_cy * c_matL/100 * maf_DSD
    # print("Lower Resv. Dam & Spillway Unit Cost ($/CY) =", u_lrds)
    # Cost of LRDS
    C_lrds = V_lrds * u_lrds
    # print("Lower Resv. Dam & Spillway Cost = $", C_lrds)

    # Concrete Lined Water Conductors
    # Upper Low & High Pressure Tunnels (ulhpt)
    # Length of ulhpt (ft)
    L_ulhpt_OR = 0
    if L_ulhpt_OR > 0:
        L_ulhpt = L_ulhpt_OR
    else:
        L_ulhpt = L_c * N_t
    # print("Upper Low & High Pressure Tunnels Length (ft) =", L_ulhpt)
    # Unit cost of ulhpt ($/ft)
    maf_CLT = 1.6 # MAF suggested for concrete lined tunnels
    u_ulhpt_OR = 0
    if T_cond == "Average":
        if L_c_mi <= 0.5:
            u_ulhpt = 3.9286 * D_t_adj ** 2 + 10.071 * D_t_adj + 481.43
        elif L_c_mi > 0.5 and L_c_mi <= 1:
            u_ulhpt = 4.3214 * D_t_adj ** 2 - 5.6071 * D_t_adj + 815
        elif L_c_mi > 1 and L_c_mi <= 2:
            u_ulhpt = 5.5536 * D_t_adj ** 2 - 42.339 * D_t_adj + 1165.4
        elif L_c_mi > 2:
            u_ulhpt = 7.6786 * D_t_adj ** 2 - 103.54 * D_t_adj + 1690.7
    elif T_cond == "Poor":
        if L_c_mi <= 0.5:
            u_ulhpt = 6.6786 * D_t_adj ** 2 - 17.393 * D_t_adj + 915
        elif L_c_mi > 0.5 and L_c_mi <= 1:
            u_ulhpt = 6.25 * D_t_adj ** 2 + 7.8929 * D_t_adj + 819.29
        elif L_c_mi > 1 and L_c_mi <= 2:
            u_ulhpt = 6.7143 * D_t_adj ** 2 + 13.857 * D_t_adj + 732.86
        elif L_c_mi > 2:
            u_ulhpt = 11.107 * D_t_adj ** 2 - 120.11 * D_t_adj + 1777.9
    else:
        print("Error Tunneling Condition (T_cond) is either Average or Poor")
    if u_ulhpt_OR > 0:
        u_ulhpt_final = u_ulhpt_OR
    else:
        u_ulhpt_final = u_ulhpt * c_matL/100 * maf_CLT
    # print("Upper Low & High Pressure Tunnels Unit Cost ($/ft) =", u_ulhpt_final)
    # Total cost of ulhpt $
    C_ulhpt = L_ulhpt * u_ulhpt_final
    # print("Upper Low & High Pressure Tunnels Cost = $", C_ulhpt)

    # Vertical Shafts
    D_vs_OR = 0
    if D_vs_OR > 0:
        D_vs = D_vs_OR
    else:
        D_vs = D_t * N_t # Vertical Shaft Diameter in ft
    # print("Vertical Shaft Diameter (ft) =", D_vs)
    # Unit cost for vs
    maf_VS = 1.8 # suggested for vertical shafts
    u_vs_OR = 0
    if u_vs_OR > 0:
        u_vs = u_vs_OR
    else:
        u_vs = (186.57 * D_t_adj + 27.143)* c_matL/100 * maf_VS
    # print("Vertical Shaft Unit Cost ($/ft) =", u_vs)
    # Total cost of vs
    C_vs = D_vs * u_vs
    # print("Vertical Shaft Cost = $", C_vs)

    # Penstock Tunnels
    # Diameter of penstock tunnels (ft)
    D_pt_OR = 0
    if D_pt_OR > 0:
        D_pt = D_pt_OR
    else:
        D_pt = D_p * N_u
    # print("Penstock Tunnel Diameter (ft) =", D_pt)
    # Unit cost of pt
    if H_nomMax <= 500:
        u_pt = 47.162 * D_p ** 1.6615
    elif H_nomMax > 500 and H_nomMax <= 1000:
        u_pt = 43.711 * D_p ** 1.7314
    elif H_nomMax > 1000 and H_nomMax <= 1500:
        u_pt = 45.454 * D_p ** 1.8126
    elif H_nomMax > 1500:
        u_pt = 60.182 * D_p ** 1.7959
    maf_SLT = 1.9 # MAF suggested for steel lined tunnels
    u_pt_OR = 0
    if u_pt_OR > 0:
        u_pt_final = u_pt_OR
    else:
        u_pt_final = u_pt * c_matL/100 * maf_SLT
    # print("Penstock Tunnels Unit Cost ($/ft) =", u_pt_final)
    # Cost of penstock tunnels
    C_pt = D_pt * u_pt_final
    # print("Penstock Tunnel Cost = $", C_pt)

    # Draft Tube Tunnels
    # Draft Tube Tunnel Diameter (ft)
    D_dtt_OR = 0
    if D_dtt_OR > 0:
        D_dtt = D_dtt_OR
    else:
        D_dtt = N_u * D_p
    # print("Draft Tube Tunnel Diameter (ft) =", D_dtt)
    # unit cost for dtt
    if Z_pps == "Underground":
        if H_nomMax <= 500:
            u_dtt = 47.162 * D_p ** 1.6615
        elif H_nomMax > 500 and H_nomMax <= 1000:
            u_dtt = 43.711 * D_p ** 1.7314
        elif H_nomMax > 1000 and H_nomMax <= 1500:
            u_dtt = 45.454 * D_p ** 1.8126
        elif H_nomMax > 1500:
            u_dtt = 60.182 * D_p ** 1.7959
    elif Z_pps == "Surface":
        u_dtt = 0
    else:
        print("Error the options for location are Underground or Surface")
    maf_DT = 1.9 # Suggested MAF for Draft Tubes
    u_dtt_OR = 0
    if u_dtt_OR > 0:
        u_dtt_final = u_dtt_OR
    else:
        u_dtt_final = u_dtt * c_matL/100 * maf_DT
    # print("Draft Tube Tunnel Unit Cost ($/ft) =", u_dtt_final)
    # Cost of draft tube tunnels
    C_dtt = u_dtt_final * D_dtt 
    # print("Draft Tube Tunnel Cost = $", C_dtt)

    # Tailrace Tunnels
    # Tailrace tunnel diameter (ft)
    D_tt_OR = 0
    if D_tt_OR > 0:
        D_tt = D_tt_OR
    else:
        D_tt = N_u * D_p
    # print("Tailrace Tunnel Diameter (ft) =", D_tt)
    # Tailrace tunnel unit cost
    u_tt_OR = 0
    if u_tt_OR > 0:
        u_tt = u_tt_OR
    else:
        u_tt = u_dtt * c_matL/100 * maf_CLT
    # print("Tailrace Tunnel Unit Cost ($/ft) =", u_tt)
    # Tailrace tunnel cost
    C_tt = u_tt * D_tt
    # print("Tailrace Tunnel Cost = $", C_tt)

    # Surface Penstock
    # Surface penstock diameter (ft)
    D_sp_OR = 0
    if D_sp_OR > 0:
        D_sp = D_sp_OR
    else:
        D_sp = N_u * D_p
    # print("Surface Penstock Diameter (ft)", D_sp)
    # Sp unit cost ($/ft)
    if H_nomMax <= 300:
        u_sp = 0.02 * D_p ** 1.885
    elif H_nomMax > 300 and H_nomMax <= 500:
        u_sp = 0.0226 * D_p ** 1.9901
    elif H_nomMax > 500 and H_nomMax <= 700:
        u_sp = 0.0365 * D_p ** 1.9417
    elif H_nomMax > 700 and H_nomMax <= 1000:
        u_sp = 0.0483 * D_p ** 1.9694
    elif H_nomMax > 1000:
        u_sp = 0.0721 * D_p ** 1.9647
    maf_SP = 1.3 # Suggested MAF for Surface Penstock
    u_sp_OR = 0
    if u_sp_OR > 0:
        u_sp_final = u_sp_OR
    else:
        u_sp_final = u_sp * c_matL/100 * maf_SP
    # print("Surface Penstock Unit Cost ($/ft) =",u_sp_final)
    # Surface Penstock Cost
    C_sp = u_sp_final * D_sp * 1000
    # print("Surface Penstock Cost = $", C_sp)

    # Surge Facilities (Reservoirs, Dams, & Waterways)
    # Percent of surge facilities 
    n_sf_OR = 0
    if n_sf_OR > 0:
        n_sf = n_sf_OR
    elif Surge_chambs == "Yes":
        n_sf = 0.4
    elif Surge_chambs == "No":
        n_sf = 0
    else:
        print("Surge Chambers needs to be Yes or No")
    # print("Percent of Surge Facilities = ", n_sf * 100)
    # Cost of Surge Facilities
    C_sf = n_sf * (C_ulhpt + C_vs + C_pt + C_tt + C_dtt + C_sp)
    # print("Surge Facilities Cost = $", C_sf)

    # Powerstation Equipment
    # PSE power (kW)
    P_pse_OR = 0
    if P_pse_OR > 0:
        P_pse = P_pse_OR
    else:
        P_pse = P_pps
    # print("Powerstation Equipment Power (kW) =", P_pse)
    # PSE unit cost ($/kW)
    if Z_pps == "Underground":
        if P_G_max <= 80: # MW
            if N_u <= 2:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0609 * H_G_avg + 259.97
            elif N_u > 2 and N_u <= 3:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0609 * H_G_avg + 247.79
            elif N_u > 3 and N_u <= 4:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0617 * H_G_avg + 241.53
            elif N_u > 4:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0555 * H_G_avg + 232.3
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0485 * H_G_avg + 216.18
            elif N_u > 2 and N_u <= 3:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0462 * H_G_avg + 206.27
            elif N_u > 3 and N_u <= 4:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0453 * H_G_avg + 200.29
            elif N_u > 4:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0456 * H_G_avg + 196.43
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0544 * H_G_avg + 177.56
            elif N_u > 2 and N_u <= 3:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0488 * H_G_avg + 166.28
            elif N_u > 3 and N_u <= 4:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.048 * H_G_avg + 163.78
            elif N_u > 4:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0452 * H_G_avg + 157.75
        elif P_G_max > 225:
            if N_u <= 2:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0365 * H_G_avg + 139.89
            if N_u > 2 and N_u <= 3:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0355 * H_G_avg + 132.8
            if N_u > 3 and N_u <= 4:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.033 * H_G_avg + 129.39
            if N_u > 4:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0316 * H_G_avg + 125.28
    elif Z_pps == "Surface":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pse = 8 * 10 ** -6 * H_G_avg ** 2 - 0.0174 * H_G_avg + 242.74
            elif N_u > 2 and N_u <= 3:
                u_pse = 8 * 10 ** -6 * H_G_avg ** 2 - 0.017 * H_G_avg + 230.3
            elif N_u > 3 and N_u <= 4:
                u_pse = 8 * 10 ** -6 * H_G_avg ** 2 - 0.0168 * H_G_avg + 223.7
            elif N_u > 4:
                u_pse = 8 * 10 ** -6 * H_G_avg ** 2 - 0.0173 * H_G_avg + 219.28
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0499 * H_G_avg + 212.36
            elif N_u > 2 and N_u <= 3:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0457 * H_G_avg + 200.9
            elif N_u > 3 and N_u <= 4:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.046 * H_G_avg + 196.81
            elif N_u > 4:
                u_pse = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0501 * H_G_avg + 195
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0319 * H_G_avg + 165.52
            elif N_u > 2 and N_u <= 3:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0338 * H_G_avg + 159.73
            elif N_u > 3 and N_u <= 4:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0313 * H_G_avg + 155.12
            elif N_u > 4:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0309 * H_G_avg + 151.13
        elif P_G_max > 225:
            if N_u <= 2:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0447 * H_G_avg + 144.85
            elif N_u > 2 and N_u <= 3:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.041 * H_G_avg + 136.46
            elif N_u > 3 and N_u <= 4:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0391 * H_G_avg + 133.75
            elif N_u > 4:
                u_pse = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0406 * H_G_avg + 131.67
    else:
        print("Error: Position of the Power Plant Station is either Underground or Surface")
    maf_EM = 1.7 # suggested MAF for electromechanical devices
    u_pse_OR = 0
    if u_pse_OR > 0:
        u_pse_final = u_pse_OR
    else:
        u_pse_final = u_pse * c_matL/100 * maf_EM
    # print("Powerstation Equipment Unit Cost ($/kW) =", u_pse_final)
    # Cost of Powerstation Equipment
    C_pse = u_pse_final * P_pse
    # print("Powerstation Equipment Cost = $", C_pse)

    # Roads, Railroads, & Bridges 
    # Access Roads
    # Access road length (mi)
    L_rrb_OR = 0
    if L_rrb_OR > 0:
        L_rrb = L_rrb_OR
    else:
        L_rrb = L_ar
    # print("Access Road Length (mi) =", L_rrb)
    # Access road unit cost ($/mi)
    if ter_AR == "Steep" and Typ_ar == "New":
        u_rrb = 439000
    elif ter_AR == "Mild" and Typ_ar == "New":
        u_rrb = 283000
    elif ter_AR == "Flat" and Typ_ar == "New":
        u_rrb = 189000
    elif ter_AR == "Steep" and Typ_ar == "Rebuild":
        u_rrb = 293000
    elif ter_AR == "Mild" and Typ_ar == "Rebuild":
        u_rrb = 186000
    elif ter_AR == "Flat" and Typ_ar == "Rebuild":
        u_rrb = 123000
    else:
        print("Error: Access road terrain is either Steep, Mild, or Flat and Acess road type is either New or Rebuild")
    maf_R = 1 # suggested MAF for roads
    u_ar_OR = 0
    if u_ar_OR > 0:
        u_ar = u_ar_OR
    else:
        u_ar = u_rrb * c_matL/100 * maf_R
    # print("Access Road Unit Cost ($/mi) =", u_ar)
    # Access Road Cost 
    C_ar = L_rrb * u_ar
    # print("Access Road Cost = $", C_ar)

    # Access Tunnels
    # Length of Access Tunnels in ft
    L_at_ft_OR = 0
    if L_at_ft_OR > 0:
        L_at_ft = L_at_ft_OR
    else:
        L_at_ft = L_at_mi * 5280
    # print("Access Tunnel Length (ft) =", L_at_ft)
    # Unit cost of access tunnels ($/ft)
    maf_AVT = 1 # suggested MAF for access and volt tunnels
    u_at_OR = 0
    if u_at_OR > 0:
        u_at = u_at_OR
    else:
        u_at = (2489.4 * L_at_mi ** 0.118) * c_matL/100 * maf_AVT
    # print("Access Tunnel Unit Cost ($/ft) =", u_at)
    # Cost of access tunnels
    C_at = L_at_ft * u_at
    # print("Access Tunnel Cost = $", C_at)

    # Switchyard
    # Switchyard voltage (kV)
    V_sy_OR = 0
    if V_sy_OR > 0:
        V_sy = V_sy_OR
    else:
        V_sy = V_sub
    # print("Switchyard Voltage (kV) =", V_sy)
    # Switchyard unit cost ($/kV)
    if V_sub <= 160:
        u_sy = -0.0643 * N_u ** 2 + 1.0743 * N_u - 0.48
    elif V_sub > 160 and V_sub <= 230:
        u_sy = -0.1 * N_u ** 2 + 1.6 * N_u - 1.1
    elif V_sub > 230 and V_sub <= 345:
        u_sy = -0.1607 * N_u ** 2 + 3.1007 * N_u - 1.91
    elif V_sub > 345:
        u_sy = -0.6286 * N_u ** 2 + 8.3086 * N_u - 6.45
    maf_SY = 1 # Suggested MAF for switchyard
    u_sy_OR = 0
    if u_sy_OR > 0:
        u_sy_final = u_sy_OR
    else:
        u_sy_final = u_sy * c_matL/100 * maf_SY
    # print("Switchyard Unit Cost ($M) =", u_sy_final)
    # Total cost of switchyard
    C_sy = u_sy_final * 10 ** 6
    # print("Switchyard Cost = $", C_sy)

    # Transmission Lines
    # TL power (kW)
    P_tl_OR = 0
    if P_tl_OR > 0:
        P_tl = P_tl_OR
    else:
        P_tl = P_pps
    # print("Transmission Lines Power (kW) =", P_tl)
    # TL unit cost 
    if V_trans <= 138:
        u_tl = 0.0043 * P_G_max ** 2 - 0.028 * P_G_max + 108.72
    elif V_trans > 138 and V_trans <= 230:
        u_tl = 0.0007 * P_G_max ** 2 - 0.0382 * P_G_max + 169.98
    elif V_trans > 230 and V_trans <= 345:
        u_tl = 0.0003 * P_G_max ** 2 - 0.2536 * P_G_max + 335.57
    elif V_trans > 345:
        u_tl = 4 * 10 ** -5 * P_G_max ** 2 - 0.0652 * P_G_max + 428.5
    maf_TW = 1.3 # suggested MAF for transmission works
    u_tl_OR = 0
    if u_tl_OR > 0:
        u_tl_final = u_tl_OR
    else:
        u_tl_final = u_tl * c_matL/100 * maf_TW
    # print("Transmission Lines Unit Cost ($1000s) =", u_tl_final)
    # Transmission circuit multiplier (M_tc)
    if Typ_trans == "Double":
        M_tc = 1.6005
    elif Typ_trans == "Single":
        M_tc = 1
    else:
        print("Error: Transmission type is either Single or Double")
    # Transmission terrain multiplier (M_tt)
    if ter_trans == "Dessert":
        M_tt = 1.05
    elif ter_trans == "Flat":
        M_tt = 1
    elif ter_trans == "Farmland":
        M_tt = 1
    elif ter_trans == "Forrested":
        M_tt = 2.25
    elif ter_trans == "Rolling":
        M_tt = 1.4
    elif ter_trans == "Mountain":
        M_tt = 1.75
    elif ter_trans == "Wetland":
        M_tt = 1.2
    elif ter_trans == "Suburban":
        M_tt = 1.27
    elif ter_trans == "Urban":
        M_tt = 1.59
    else:
        print("Error: Transmission Terrain is either: Dessert, Flat, Farmland, Forrested, Rolling, Mountain, Wetland, Suburban, or Urban")
    # Transmission Line Cost ($)
    C_tl = u_tl_final * 1000 * M_tc * M_tt
    # print("Transmission Line Cost = $", C_tl)

    # Soft Costs
    # Sales Tax
    t_s_OR = 0
    if t_s_OR > 0:
        t_s = t_s_OR
    else:
        t_s = t_sales
    # print("Sales Tax (%) =", t_s * 100)
    # Sum of pre-tax costs (S_cpt)
    S_cpt = C_land + C_pps + C_uds + C_uri + C_sf + C_lri + C_lrds + C_ulhpt + C_vs + C_pt + C_dtt + C_tt + C_sp + C_pse + C_ar + C_at + C_sy + C_tl
    # Sales Tax Cost
    C_s = t_s * n_mE * S_cpt
    # print("Sales Tax Cost = $", C_s)

    # Contingency
    t_con_OR = 0
    if t_con_OR > 0:
        t_con = t_con_OR
    else:
        t_con = t_cont
    # print("Contingency (%) =", t_con * 100)
    # Contingency cost
    C_con = t_con * S_cpt
    # print("Contingency Cost = $", C_con)

    # EPC tax
    t_epc_OR = 0
    if t_epc_OR > 0:
        t_epc = t_epc_OR
    else:
        t_epc = t_EPC
    # print("EPC Cost (%) =", t_epc * 100)
    # EPC Cost
    C_epc = S_cpt * t_epc * n_mE
    # print("EPC Cost = $", C_epc)

    # Developer Cost
    t_dc_OR = 0
    if t_dc_OR > 0:
        t_dc = t_dc_OR
    else:
        t_dc = t_DC
    # print("Developer Cost (%) =", t_dc * 100)
    C_dc = t_dc * S_cpt
    # print("Developer Cost = $", C_dc)

    # Overhead and Profit
    t_op_OR = 0
    if t_op_OR > 0:
        t_op = t_op_OR
    else:
        t_op = t_OP
    # print("Overhead and Profit (%) =", t_op * 100)
    C_op = S_cpt * t_op * n_mE
    # print("Overhead and Profit = $", C_op)

    # TOTAL COST for PSH
    C_total = S_cpt + C_s + C_con + C_epc + C_dc + C_op
    # print("Total PSH Cost = $", C_total)

    # TOTAL Cost/kW
    C_p_total = C_total/(1000 * P_G_avg)
    # print("Total PSH Cost ($/kW) =", C_p_total)

    # TOTAL Cost/kWh
    C_e_total = C_total/(1000 * P_G_avg * t_gen)
    # print("Total PSH Cost ($/kWh) =", C_e_total)
    return C_total, C_p_total, C_e_total

# h_vals = [90, 92]
# costs = psh_cost(h_vals, 90, 2100)
# print("Total PSH Cost = $", costs[0])
# print("Total PSH Cost ($/kW) =", costs[1])
# print("Total PSH Cost ($/kWh) =", costs[2])
