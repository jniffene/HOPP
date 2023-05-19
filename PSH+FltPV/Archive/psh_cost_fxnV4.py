# Cost equations for a PSH facility originally from the
# Excel Workbook "GS-6669 Implemenation for NREL 8-3-22.xlsx"
# obtained from Vignesh Ramasamy an Stuart Cohen and 
# converted to Python by James Niffenegger on 4-19-23 

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

def psh_costV4(h_o, A, z_max, P_G_min, P_G_avg, P_G_max):
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
    L_c_ft = 100 # ft; Conveyance Length (C15)
    T_cond = "Poor" # Tuneling Cond. (C16)
    T_pSmall = "Standby" # Small PSH Power Type (Standby or No Standby) (C17)
    # H_nomMaxM = 100 # m; Nominal (max) Head (C20)
    H_max = (z_max + h_o) * 3.28084 # ft; Nominal (max possible) Head (C21)
    t_gen = 10 # hr; Generating Time (C22)
    F_i = "Yes" # Inflation Factor (C23) (Yes or No)
    Loc = "United States" # Location (C26) 
    A_acq = A_u/0.8 # acres; Acerage to Aquire (C27)
    L_at = 0.75 # mi; Length, access tunnel (C30)
    ter_AR = "Mild" # Access Road, Terrain (C31) (Mild, Steep, or Flat)
    Typ_ar = "New" # Access Road, Type (C32) (New or Rebuild)
    L_ar = 1.2 # mi; Access Road, Length (C33)
    P_loc = "Underground" # Penstock Location (C34) (Underground or Surface)
    Hr = "No" # Highway realignment (C35) (No or Yes)
    I_ur = "Horizontal" # Upper Resv. Intake (C37)
    I_lr = "Horizontal" # Lower Resv. Intake (C37)
    G_ps = "Adverse" # Powerstation Struct. Geology (C38)
    Z_ps = "Surface" # Power Station (Above or Below Ground) (C39)

    # Definition of function

    # Assumptions
    p_AS = 0.85 # Percent Active Storage (G8)
    Hmin_Hmax = h_o/(z_max + h_o) # Hmin/Hmax (G11) originally assumed to be 0.7
    V_u_avg = Z_u_avg * A_u # ac-ft; Average Upper Resv. Volume (G12)
    V_L_avg = Z_L_avg * A_l # ac-ft; Average Lower Resv. Volume (G13)
    v_T_max = 20 # ft/s; Max tunnel velocity (G15)
    D_T_max = 35 # ft; Max tunnel diameter (G16)
    L_c = L_c_ft * 0.000189394 # mi; Conveyance Length (G17)
    C_hw = 90 # Hazen Williams Constant (G19)
    t_sales = 0.06 # Sales Tax (G20)
    t_cont = 0.25 # Contingency Tax (G21)
    t_EPC = 0.083 # EPC Cost (G22)
    t_DC = 0.03 # Developer cost (G23)
    t_OP = 0.07 # Overhead and Profit (G24)
    n_PT = 0.88 # P-T Efficiency (G25)
    P_capMax = 150 # MW, Max Unit Capacity (G28)
    N_min = 4 # minimum number of units (G29)
    v_P_max = 25 # ft/s; max penstock velocity (G30)
    n_mE = 0.9 # Material/equipment % (G31)
    L_trans = 30 # mi; Transmission length (G32)
    Ws = "No" # Water supply (G33) (Yes or No)
    Md = "No" # Mob/Demob (G35) (Yes or No)
    C_t_pump = 1.2 # pump time (G37)
    V_trans = 150 # kV; Transmission (G38)
    V_sub = 150 # kV; Substation (G39)
    ter_trans = "Flat" # Transmission Terrain (G40)
    Typ_trans = "Single" # Transmission Type (G41)
    # Transmission circuit multiplier (m_trans) (I41)
    if Typ_trans == "Double":
        m_trans = 1.6005
    elif Typ_trans == "Single":
        m_trans = 1
    else:
        print("Error: Transmission type is either Single or Double")
    # Transmission terrain multiplier (M_trans) (I40)
    if ter_trans == "Dessert":
        M_trans = 1.05
    elif ter_trans == "Flat":
        M_trans = 1
    elif ter_trans == "Farmland":
        M_trans = 1
    elif ter_trans == "Forrested":
        M_trans = 2.25
    elif ter_trans == "Rolling":
        M_trans = 1.4
    elif ter_trans == "Mountain":
        M_trans = 1.75
    elif ter_trans == "Wetland":
        M_trans = 1.2
    elif ter_trans == "Suburban":
        M_trans = 1.27
    elif ter_trans == "Urban":
        M_trans = 1.59
    else:
        print("Error: Transmission Terrain is either: Dessert, Flat, Farmland, Forrested, Rolling, Mountain, Wetland, Suburban, or Urban")
    error_val = 10 ** 9

    # Outputs Related to PSH power production
    S_act = p_AS * V_u_avg # ac-ft; Active Storage (M8)
    # print("Active Storage (ac-ft) =", S_act)
    Q_dis = S_act * 43560 / (t_gen * 3600) # ft3/s; Mean Gen Discharge (M9)
    # print("Mean Gen Discharge (ft3/s) =", Q_dis)
    H_G_min = Hmin_Hmax * H_max # ft; min gross head (= to the static head) (M11)
    # print("Min Gross Head (ft) =", H_G_min)
    H_G_avg = (H_G_min + H_max)/2 # ft; mean gross head (M12)
    # print("Avg Gross Head (ft) =", H_G_avg)
    Q_gen_min = Q_dis * (H_G_min/H_G_avg) ** 0.5 # ft3/s; Min Gen Discharge (M13)
    # print("Min Gen Discharge (ft3/s) =", Q_gen_min)
    Q_gen_max = Q_dis * (H_max/H_G_avg) ** 0.5 # ft3/s; Max Gen Discharge (M14)
    # print("Max Gen Discharge (ft3/s) =", Q_gen_max)
    D_t = ((4 * Q_gen_max)/(v_T_max * pi)) ** 0.5 # ft; Tunnel Diameter (M15)
    # print("Tunnel Diameter (ft) =", D_t)
    # Number of tunnels (M16)
    if D_t <= D_T_max:
        N_t = 1
    else:
        N_t = 2
    # print("Number of Tunnels =", N_t)
    D_t_adj = ((4 * Q_gen_max)/(pi * N_t * v_T_max)) ** 0.5 # ft; Adjusted Tunnel Diameter (M17)
    # print("Adjusted Tunnel Diameter (ft) =", D_t_adj)
    L_h = L_c_ft/H_G_avg # L/H (M18)
    # Surge Chambers (Yes or No) (C29)
    if L_h >= 7:
        Sc = "Yes"
    else:
        Sc = "No"
    # print("L/H =", L_h)
    h_gen_min = (4.73 * L_c_ft * (Q_gen_min ** 1.85))/((C_hw ** 1.85) * (D_t_adj ** 4.87)) # ft; Min Gen Headloss (M19)
    # print("Min Gen Headloss (ft) =", h_gen_min)
    h_gen_avg = (4.73 * L_c_ft * (Q_dis ** 1.85))/((C_hw ** 1.85) * (D_t_adj ** 4.87)) # ft; Mean Gen Headloss (M20)
    # print("Mean Gen Headloss (ft) =", h_gen_avg)
    h_gen_max = (4.73 * L_c_ft * (Q_gen_max ** 1.85))/((C_hw ** 1.85) * (D_t_adj ** 4.87)) # ft; Max Gen Headloss (M21)
    # print("Max Gen Headloss (ft) =", h_gen_max)
    
    dH_gen_min = H_G_min - h_gen_min # ft; net head at min gen discharge (M22)
    # print("Net Head @ Min Gen Discharge (ft) =", dH_gen_min)
    if dH_gen_min <= 0:
        print("Error: Net Head is Less Than or Equal to Zero!")
        return error_val, error_val, error_val
    
    dH_gen_avg = H_G_avg - h_gen_avg # ft; net head at avg gen discharge (M23)
    # print("Net Head @ Avg Gen Discharge (ft) =", dH_gen_avg)
    if dH_gen_avg <= 0:
        print("Error: Net Head is Less Than or Equal to Zero!")
        return error_val, error_val, error_val
    
    dH_gen_max = H_max - h_gen_max # ft; net head at max gen discharge (M24)
    # print("Net Head @ Max Gen Discharge (ft) =", dH_gen_max)
    if dH_gen_max <= 0:
        print("Error: Net Head is Less Than or Equal to Zero!")
        return error_val, error_val, error_val
    
    # P_G_min = (Q_gen_min * dH_gen_min * n_PT)/(11.81 * 1000) # MW; min plant gen power (M25)
    # # print("Min Plant Gen Power (MW) =", P_G_min)
    # P_G_avg = (Q_dis * dH_gen_avg * n_PT)/(11.81 * 1000) # MW; mean plant gen power (M26)
    # # print("Mean Plant Gen Power (MW) =", P_G_avg)
    # P_G_max = (Q_gen_max * dH_gen_max * n_PT)/(11.81 * 1000) # MW; max plant gen power (M27)
    # # print("Max Plant Gen Power (MW) =", P_G_max)
    
    # # Power definitions altered to reflect simulation
    # # Counter for when P_psh2L is nonzero
    # N_psh2L = 0
    # for i in range(len(P_psh2L)):
    #     if P_psh2L[i] > 0:
    #         N_psh2L = N_psh2L + 1
    # Pos_psh2L = np.empty(N_psh2L)
    # c = 0
    # for i in range(len(P_psh2L)):
    #     if P_psh2L[i] > 0:
    #         Pos_psh2L[c] = P_psh2L[i]
    #         c = c + 1
    # P_G_min = min(Pos_psh2L)/1000 # going from kW to MW
    # P_G_avg = mean(Pos_psh2L)/1000 # going from kW to MW
    # P_G_max = max(Pos_psh2L)/1000 # going from kW to MW

    
    # Number of units N_u (M28)
    if P_G_max / P_capMax <= N_min:
        N_u = N_min
    else:
        N_u = math.ceil(P_G_max / P_capMax)
    # print("Number of Units =", N_u)
    P_capU = P_G_max / N_u # MW; Unit Rating (M29) 
    # print("Unity Capacity (MW) =", P_capU)
    D_p = ((4 * Q_gen_max)/(pi * v_P_max)) ** 0.5 # ft; Penstock Diameter (M31)
    # print("Penstock Diameter (ft) =", D_p)
    t_pump = C_t_pump * t_gen # hr; Pump Time (M37)
    # print("Pump Time (hr) =", t_pump)
    Q_pump_avg = (S_act * 43560)/(t_pump * 3600) # ft3/s; Mean Pump Discharge (M38)
    # print("Mean Pump Discharge (ft3/s) =", Q_pump_avg)
    h_pump_avg = (4.73 * (Q_pump_avg ** 1.85) * L_c_ft)/((C_hw ** 1.85) * (D_t_adj ** 4.87)) # ft; mean pump headloss (M39)
    # print("Mean Pump Headloss (ft) =", h_pump_avg)
    dH_pump_avg = H_G_avg + h_pump_avg # ft; Mean Pump Net Head (M40)
    # print("Mean Pump Net Head (ft) =", dH_pump_avg)
    P_pump_avg = (Q_pump_avg * dH_pump_avg * n_PT)/(11.81 * 1000) # MW; Mean Pump Power (M41)
    # print("Mean Pump Power (MW) =", P_pump_avg)

    # Cost Calculations
    a_land = "Yes" # applicability (Yes or No) (D59)
    A_land_OR = 0 # acres; Land Area Override (L59)
    # Land & Land Rights: Land Area (acres) (F59)
    if a_land == "Yes":
        if A_land_OR > 0:
            A_land = A_land_OR
        else:
            A_land = A_acq
    else:
        A_land = 0
    # print("Land Area (acres) =", A_land)
    # Cost of land based on location
    df = pd.read_excel('Land Value Data.xlsx', sheet_name= 'Sheet1')
    u_land = df[df['State'] == Loc]['Average $/Acre 2021'].sum()
    # Land & Land Rights: Unit Cost ($/ac) (G59)
    
    # print("Land Area Acre Cost ($/ac) =",u_land)
    F_landLoc = 1 # Loc Factor (H59)
    # Escalation Factor (I59)
    if F_i == "Yes":
        F_landEsc = 2.4063214 # (MAF!P59)
    else:
        F_landEsc = 1
    F_landOth = 1 # Other Adjustment factor (J59)
    u_land_OR = 0 # (M59)
    if u_land_OR > 0:
        u_landAdj = u_land_OR
    else:
        u_landAdj = u_land * F_landLoc * F_landEsc * F_landOth
    C_land = A_land * u_landAdj # $; Cost of land & land rights (N59)
    # print("Cost of Land & Land Rights = $",C_land)
    
    # Powerplant Structure
    # Powerplant Power (kW)
    a_pps = "Yes" # applicability (Yes or No) (D61)
    P_pps_OR = 0 # (L61)
    # Qty (F61) (kW)
    if a_pps == "Yes":
        if P_pps_OR > 0:
            P_pps = P_pps_OR
        else:
            P_pps = P_G_max * 1000
    else:
        P_pps = 0
    # print("Powerplant Power (kW) =", P_pps)

    # Set Material Cost Value Based on Location
    df = pd.read_excel('Location Factors.xlsx', sheet_name= 'Sheet1')
    c_matL = df[df['State'] == Loc]['Material Cost'].sum() # Material cost for location

    # Powerplant Unit Cost ($/kW) 
    if G_ps == "Average" and Z_ps == "Underground":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pps = 740.12 * H_max ** -0.298 
            elif N_u > 2 and N_u <= 3:
                u_pps = 760.42 * H_max ** -0.328
            elif N_u > 3 and N_u <= 4:
                u_pps = 645.72 * H_max ** -0.32
            elif N_u > 4:
                u_pps = 640.28 * H_max ** -0.337
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pps = 1229.6 * H_max ** -0.405
            elif N_u > 2 and N_u <= 3:
                u_pps = 1113.2 * H_max ** -0.412
            elif N_u > 3 and N_u <= 4:
                u_pps = 1126.8 * H_max ** -0.431
            elif N_u > 4:
                u_pps = 1195.5 * H_max ** -0.454
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pps = 2163.3 * H_max ** -0.512
            elif N_u > 2 and N_u <= 3:
                u_pps = 1725.2 * H_max ** -0.501
            elif N_u > 3 and N_u <= 4:
                u_pps = 1735.2 * H_max ** -0.52
            elif N_u > 4:
                u_pps = 1578.2 * H_max ** -0.524
        elif P_G_max > 225:
            if N_u <= 2:
                u_pps = 2032.8 * H_max ** -0.532
            elif N_u > 2 and N_u <= 3:
                u_pps = 2231.2 * H_max ** -0.565
            elif N_u > 3 and N_u <= 4:
                u_pps = 2553 * H_max ** -0.604
            elif N_u > 4:
                u_pps = 2504.2 * H_max ** -0.615
    elif G_ps == "Adverse" and Z_ps == "Underground":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pps = 1096.7 * H_max ** -0.319
            elif N_u > 2 and N_u <= 3:
                u_pps = 878.1 * H_max ** -0.313
            elif N_u > 3 and N_u <= 4:
                u_pps = 926.99 * H_max ** -0.337
            elif N_u > 4:
                u_pps = 911.22 * H_max ** -0.352
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pps = 1435.5 * H_max ** -0.392
            elif N_u > 2 and N_u <= 3:
                u_pps = 1258 * H_max ** -0.396
            elif N_u > 3 and N_u <= 4:
                u_pps = 1375 * H_max ** -0.424
            elif N_u > 4:
                u_pps = 1131 * H_max ** -0.41
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pps = 2315.8 * H_max ** -0.49
            elif N_u > 2 and N_u <= 3:
                u_pps = 2194.6 * H_max ** -0.505
            elif N_u > 3 and N_u <= 4:
                u_pps = 2353.1 * H_max ** -0.53
            elif N_u > 4:
                u_pps = 2162.4 * H_max ** -0.533
        elif P_G_max > 225:
            if N_u <= 2:
                u_pps = 2613 * H_max ** -0.533
            elif N_u > 2 and N_u <= 3:
                u_pps = 2154.7 * H_max ** -0.53
            elif N_u > 3 and N_u <= 4:
                u_pps = 2380.6 * H_max ** -0.559
            elif N_u > 4:
                u_pps = 4996.8 * H_max ** -0.687
    elif G_ps == "Average" and Z_ps == "Surface":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pps = 0.000005 * (H_max ** 2) - 0.0009 * H_max + 83.095
            elif N_u > 2 and N_u <= 3:
                u_pps = 0.000004 * (H_max ** 2) + 0.0004 * H_max + 75.715
            elif N_u > 3 and N_u <= 4:
                u_pps = 0.000004 * (H_max ** 2) + 0.0021 * H_max + 71.437
            elif N_u > 4:
                u_pps = 0.0000006 * (H_max ** 2) + 0.0109 * H_max + 62.383
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pps = 0.000007 * (H_max ** 2) - 0.0146 * H_max + 67.574
            elif N_u > 2 and N_u <= 3:
                u_pps = 0.000007 * (H_max ** 2) - 0.0117 * H_max + 59.042
            elif N_u > 3 and N_u <= 4:
                u_pps = 0.000005 * (H_max ** 2) - 0.0065 * H_max + 54.377
            elif N_u > 4:
                u_pps = 0.000003 * (H_max ** 2) - 0.0018 * H_max + 48.04
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pps = 6E-6 * (H_max ** 2) - 0.0159 * H_max + 53.593
            elif N_u > 2 and N_u <= 3:
                u_pps = 6E-6 * (H_max ** 2) - 0.0157 * H_max + 47.989
            elif N_u > 3 and N_u <= 4:
                u_pps = 5E-6 * (H_max ** 2) - 0.0116 * H_max + 43.522
            elif N_u > 4:
                u_pps = 3E-6 * (H_max ** 2) - 0.0078 * H_max + 39.647
        elif P_G_max > 225:
            if N_u <= 2:
                u_pps = 6E-6 * (H_max ** 2) - 0.0183 * H_max + 43.547
            elif N_u > 2 and N_u <= 3:
                u_pps = 7E-6 * (H_max ** 2) - 0.0198 * H_max + 41.489
            elif N_u > 3 and N_u <= 4:
                u_pps = 6E-6 * (H_max ** 2) - 0.0162 * H_max + 36.672
            elif N_u > 4:
                u_pps = 5E-6 * (H_max ** 2) - 0.0128 * H_max + 33.573
    elif G_ps == "Adverse" and Z_ps == "Surface":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pps = 3E-6 * (H_max ** 2) + 0.0062 * H_max + 109.48
            elif N_u > 2 and N_u <= 3:
                u_pps = 1E-6 * (H_max ** 2) + 0.0099 * H_max + 90.767
            elif N_u > 3 and N_u <= 4:
                u_pps = 2E-6 * (H_max ** 2) + 0.0073 * H_max + 84.676
            elif N_u > 4:
                u_pps = -1E-7 * (H_max ** 2) + 0.0123 * H_max + 73.167
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pps = 4E-6 * (H_max ** 2) - 0.0039 * H_max + 90.761
            elif N_u > 2 and N_u <= 3:
                u_pps = 2E-6 * (H_max ** 2) + 0.0008 * H_max + 75.02
            elif N_u > 3 and N_u <= 4:
                u_pps = 2E-6 * (H_max ** 2) + 0.0002 * H_max + 70.655
            elif N_u > 4:
                u_pps = 2E-6 * (H_max ** 2) + 0.002 * H_max + 62.446
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pps = 8E-6 * (H_max ** 2) - 0.024 * H_max + 80.261
            elif N_u > 2 and N_u <= 3:
                u_pps = 5E-6 * (H_max ** 2) - 0.0155 * H_max + 65.884
            elif N_u > 3 and N_u <= 4:
                u_pps = 6E-6 * (H_max ** 2) - 0.0165 * H_max + 61.35
            elif N_u > 4:
                u_pps = 4E-6 * (H_max ** 2) - 0.0099 * H_max + 52.44
        elif P_G_max > 225:
            if N_u <= 2:
                u_pps = 1E-5 * (H_max ** 2) - 0.0308 * H_max + 67.023
            elif N_u > 2 and N_u <= 3:
                u_pps = 7E-6 * (H_max ** 2) - 0.0207 * H_max + 54.238
            elif N_u > 3 and N_u <= 4:
                u_pps = 7E-6 * (H_max ** 2) - 0.0205 * H_max + 50.886
            elif N_u > 4:
                u_pps = 5E-6 * (H_max ** 2) - 0.0146 * H_max + 43.361
    else:
        print("Error the options for geography are Average or Adverse and the options for location are Underground or Surface")
    F_ppsLoc = c_matL / 100 # location factor (H61)
    # Esc factor (I61)
    if F_i == "Yes":
        F_ppsEsc = 2.4063
    else:
        F_ppsEsc = 1
    F_ppsOth = 1.3 # (J61) (MAF PS)
    u_pps_OR = 0 # (M61)
    if u_pps_OR > 0:
        u_ppsAdj = u_pps_OR
    else:
        u_ppsAdj = u_pps * F_ppsLoc * F_ppsEsc * F_ppsOth
    # print("Powerplant Station Unit Cost ($/kW) =", u_ppsAdj)
    C_pps = u_ppsAdj * P_pps # Cost of Powerplant Structure (N61)
    # print("Powerplant Structure Cost = $", C_pps)

    # Reservoirs, Dams, & Waterways
    # Upper Reservoir Dam & Spillway Volume (CY, cubic yards)
    a_uds = "Yes" # applicability (Yes or No) (D64)
    # Qty V_uds (F64) (CY)
    if a_uds == "Yes":
        V_uds_or = 0
        if V_uds_or > 0:
            V_uds = V_uds_or
        else:
            V_uds = V_u_avg * 1613.33
    else:
        V_uds = 0
    # print("Upper Resv. Dam & Spillway Volume (CY) =", V_uds)
    u_uds = 41.699 * H_max ** -0.317 # Unit cost for upper reservoir dam & spillway ($/CY) (G64)
    F_udsLoc = F_ppsLoc # (H64)
    F_udsEsc = F_ppsEsc # I64
    F_udsOth = 1.4 # J64 (MAF!C31)
    # Adj Unit Cost (K64)
    u_uds_or = 0 # (M64)
    if u_uds_or > 0:
        u_udsAdj = u_uds_or
    else:
        u_udsAdj = u_uds * F_udsLoc * F_udsEsc * F_udsOth
    # print("Upper Resv. Dam & Spillway Unit Cost ($/CY) =", u_udsAdj)
    # Cost of Upper Resv Dam & Spillway ($)
    C_uds = V_uds * u_udsAdj # (N64)
    # print("Upper Resv. Dam & Spillway Cost = $", C_uds)
    
    # Upper Reservoir Intake
    a_uri = "Yes" # app? (D65) (Yes or No)
    # Number of Upper Resv. Intake (F65)
    N_uri_OR = 0 # (L65)
    if a_uri == "Yes":
        if N_uri_OR > 0:
            N_uri = N_uri_OR
        else:
            N_uri = N_t
    else:
        N_uri = 0
    # print("Upper Resv. Intake Tunnels =", N_uri)
    # Unit Cost for URI (G65)
    if I_ur == "Horizontal":
        u_uri = (0.0154 * D_p ** 2 - 0.1968 * D_p + 1.85) * 1E6
    elif I_ur == "Vertical":
        u_uri = (0.0046 * D_p ** 2 - 0.0819 * D_p + 0.5993) * 1E6
    else:
        print("Error Upper Resv. Intake (I_ur) must be Horizontal or Vertical")
    # print("Upper Resv. Intake Unit Cost ($/ft) =", u_uri)
    F_uriLoc = F_ppsLoc #(H65)
    F_uriEsc = F_ppsEsc # (I65)
    F_uriOth = 2 # (J65) (MAF for upper intake)
    # Adjusted Unit Cost (K65)
    u_uri_OR = 0 # M65
    if u_uri_OR > 0:
        u_uriAdj = u_uri_OR
    else:
        u_uriAdj = u_uri * F_uriLoc * F_uriEsc * F_uriOth
    # URI total cost ($) (N65)
    C_uri = u_uriAdj * N_uri
    # print("Upper Resv. Intake Cost = $", C_uri)
    
    # Lower Resv. Intake
    a_lri = "Yes" # App (Yes or No) (D67)
    # Number of LRI tunnels (F67)
    N_lri_OR = 0 # L67
    if a_lri == "Yes":
        if N_lri_OR > 0:
            N_lri = N_lri_OR
        else:
            N_lri = N_t
    else:
        N_uri = 0
    # print("Lower Resv. Intake Tunnels =", N_lri)
    # Unit Cost for Lower Resv. Intake (G67)
    if P_G_avg <= 25:
        u_lri = 0
    elif I_lr == "Horizontal":
        u_lri = (0.0154 * D_p ** 2 - 0.1968 * D_p + 1.85) * 1E6
    elif I_lr == "Vertical":
        u_lri = (0.0046 * D_p ** 2 - 0.0819 * D_p + 0.5993) * 1E6
    else:
        print("Error Lower Resv. Intake (I_lr) must be Horizontal or Vertical")
    # print("Lower Resv. Intake Unit Cost ($/ft) =", u_lri)
    F_lriLoc = F_ppsLoc # H67
    F_lriEsc = F_ppsEsc # I67
    F_lriOth = 1.3 # J67 Suggested MAF for Lower Intake
    # Adjusted Unit Cost (K67)
    u_lri_OR = 0 # M67
    if u_lri_OR > 0:
        u_lriAdj = u_lri_OR
    else:
        u_lriAdj = u_lri * F_lriLoc * F_lriEsc * F_lriOth
    # Cost of Lower Resv. Intake ($) (N67)
    C_lri = u_lriAdj * N_lri
    # print("Lower Resv. Intake Cost = $", C_lri)

    # Lower Resv. Dam & Spillway (LRDS)
    a_lrds = "Yes" # app (Yes or No) D68
    # Volume of Lower Resv. Dam & Spillway (CY) (F68)
    V_lrds_OR = 0
    if a_lrds == "Yes":
        if V_lrds_OR > 0:
            V_lrds = V_lrds_OR
        else:
            V_lrds = V_L_avg * 1613.33 # convert from ac-ft to cy
    else:
        V_lrds = 0
    # print("Lower Resv. Dam & Spillway Volume (CY) =", V_lrds)
    u_lrds = 41.699 * H_max ** -0.317 # Unit Cost of LRDS ($/CY) (G68)
    F_lrdsLoc = F_ppsLoc # H68
    F_lrdsEsc = F_ppsEsc # I68
    F_lrdsOth = 1.4 # (MAF for Dams) J68
    # Adj unit cost (K68)
    u_lrds_OR = 0
    if u_lrds_OR > 0:
        u_lrdsAdj = u_lrds_OR
    else:
        u_lrdsAdj = u_lrds * F_lrdsLoc * F_lrdsEsc * F_lrdsOth
    # print("Lower Resv. Dam & Spillway Unit Cost ($/CY) =", u_lrds)
    # Cost of LRDS (N68)
    C_lrds = V_lrds * u_lrdsAdj 
    # print("Lower Resv. Dam & Spillway Cost = $", C_lrds)

    # Concrete Lined Water Conductors
    # Upper Low & High Pressure Tunnels (ulhpt)
    a_ulhpt = "Yes" # App D71
    # Length of ulhpt (ft) F71
    L_ulhpt_OR = 0 # L71
    if a_ulhpt == "Yes":
        if L_ulhpt_OR > 0:
            L_ulhpt = L_ulhpt_OR
        elif P_G_avg <= 25:
            L_ulhpt = 0
        else:
            L_ulhpt = abs(L_c_ft - H_G_min) * 0.25 # set to abs to avoid error
    else:
        L_ulhpt = 0
    # print("Upper Low & High Pressure Tunnels Length (ft) =", L_ulhpt)
    # Unit cost of ulhpt ($/ft) (G71)
    if T_cond == "Average":
        if L_c <= 0.5:
            u_ulhpt = 3.9286 * D_t_adj ** 2 + 10.071 * D_t_adj + 481.43
        elif L_c > 0.5 and L_c <= 1:
            u_ulhpt = 4.3214 * D_t_adj ** 2 - 5.6071 * D_t_adj + 815
        elif L_c > 1 and L_c <= 2:
            u_ulhpt = 5.5536 * D_t_adj ** 2 - 42.339 * D_t_adj + 1165.4
        elif L_c > 2:
            u_ulhpt = 7.6786 * D_t_adj ** 2 - 103.54 * D_t_adj + 1690.7
    elif T_cond == "Poor":
        if L_c <= 0.5:
            u_ulhpt = 6.6786 * D_t_adj ** 2 - 17.393 * D_t_adj + 915
        elif L_c > 0.5 and L_c <= 1:
            u_ulhpt = 6.25 * D_t_adj ** 2 + 7.8929 * D_t_adj + 819.29
        elif L_c > 1 and L_c <= 2:
            u_ulhpt = 6.7143 * D_t_adj ** 2 + 13.857 * D_t_adj + 732.86
        elif L_c > 2:
            u_ulhpt = 11.107 * D_t_adj ** 2 - 120.11 * D_t_adj + 1777.9
    else:
        print("Error Tunneling Condition (T_cond) is either Average or Poor")
    F_ulhptLoc = F_ppsLoc # H71
    F_ulhptEsc = F_ppsEsc # I71
    F_ulhptOth = 1.6 # J71 MAF suggested for concrete lined tunnels
    u_ulhpt_OR = 0 # M71
    # Adj Unit Cost K71
    if u_ulhpt_OR > 0:
        u_ulhptAdj = u_ulhpt_OR
    else:
        u_ulhptAdj = u_ulhpt * F_ulhptLoc * F_ulhptEsc * F_ulhptOth
    # print("Upper Low & High Pressure Tunnels Unit Cost ($/ft) =", u_ulhpt_final)
    # Total cost of ulhpt $ (N71)
    C_ulhpt = L_ulhpt * u_ulhptAdj
    # print("Upper Low & High Pressure Tunnels Cost = $", C_ulhpt)

    # Vertical Shafts
    a_vs = "Yes" # app? (Yes or No) D72
    # Qty (F72)
    L_vs_or = 0
    if a_vs == "Yes":
        if L_vs_or > 0:
            L_vs = L_vs_or
        elif P_G_avg <= 25:
            L_vs = 0
        else:
            L_vs = dH_gen_min
    else:
        L_vs = 0
    # print("Vertical Shaft Diameter (ft) =", L_vs)
    u_vs = (186.57 * D_t_adj + 27.143) # Unit cost for vs G72
    F_vsLoc = F_ppsLoc # H72
    F_vsEsc = F_ppsEsc # I72
    F_vsOth = 1.8 # MAF for vert shafts J72
    # Adj unit cost (K72)
    u_vs_OR = 0 # M72
    if u_vs_OR > 0:
        u_vsAdj = u_vs_OR
    else:
        u_vsAdj = u_vs * F_vsLoc * F_vsEsc * F_vsOth
    # print("Vertical Shaft Unit Cost ($/ft) =", u_vs)
    # Total cost of vs N72
    C_vs = L_vs * u_vsAdj
    # print("Vertical Shaft Cost = $", C_vs)

    # Penstock Tunnels
    a_pt = "Yes" # app? D73
    L_pt_or = 0 # L73
    # Length of penstock tunnels (ft) F73
    if a_pt == "Yes":
        if L_pt_or > 0:
            L_pt = L_pt_or
        elif P_G_avg <= 25:
            L_pt = 0
        else:
            L_pt = abs(L_c_ft - H_G_min)*0.25
    else:
        L_pt = 0
    # print("Penstock Tunnel Diameter (ft) =", L_pt)
    # Unit cost of pt (G73)
    if H_max <= 500:
        u_pt = 47.162 * D_p ** 1.6615
    elif H_max > 500 and H_max <= 1000:
        u_pt = 43.711 * D_p ** 1.7314
    elif H_max > 1000 and H_max <= 1500:
        u_pt = 45.454 * D_p ** 1.8126
    elif H_max > 1500:
        u_pt = 60.182 * D_p ** 1.7959
    F_ptLoc = F_ppsLoc # H73
    F_ptEsc = F_ppsEsc # I73
    F_ptOth = 1.9 # MAF suggested for steel lined tunnels (J73)
    u_pt_OR = 0 # M73
    # Adj unit cost K73
    if u_pt_OR > 0:
        u_ptAdj = u_pt_OR
    else:
        u_ptAdj = u_pt * F_ptLoc * F_ptEsc * F_ptOth
    # print("Penstock Tunnels Unit Cost ($/ft) =", u_pt_final)
    # Cost of penstock tunnels (N73)
    C_pt = L_pt * u_ptAdj
    # print("Penstock Tunnel Cost = $", C_pt)

    # Draft Tube Tunnels
    a_dtt = "Yes" # App D74
    L_dtt_or = 0 # L74
    # Draft Tube Tunnel Length (ft) F74
    if a_dtt == "Yes":
        if L_dtt_or > 0:
            L_dtt = L_dtt_or
        elif P_G_avg <= 25:
            L_dtt = 0
        else:
            L_dtt = abs(L_c_ft - H_G_min)*0.25
    else:
        L_dtt = 0
    # print("Draft Tube Tunnel Diameter (ft) =", L_dtt)
    # unit cost for dtt G74
    if Z_ps == "Underground":
        if H_max <= 500:
            u_dtt = 47.162 * D_p ** 1.6615
        elif H_max > 500 and H_max <= 1000:
            u_dtt = 43.711 * D_p ** 1.7314
        elif H_max > 1000 and H_max <= 1500:
            u_dtt = 45.454 * D_p ** 1.8126
        elif H_max > 1500:
            u_dtt = 60.182 * D_p ** 1.7959
    elif Z_ps == "Surface":
        u_dtt = 0
    else:
        print("Error the options for location are Underground or Surface")
    F_dttLoc = F_ppsLoc # H74
    F_dttEsc = F_ppsEsc # I74
    F_dttOth = 1.9 # J74 Suggested MAF for Draft Tubes
    u_dtt_OR = 0 # M74
    # Adj Unit Cost K74
    if u_dtt_OR > 0:
        u_dttAdj = u_dtt_OR
    else:
        u_dttAdj = u_dtt * F_dttLoc * F_dttEsc * F_dttOth
    # print("Draft Tube Tunnel Unit Cost ($/ft) =", u_dttAdj)
    # Cost of draft tube tunnels N74
    C_dtt = u_dttAdj * L_dtt 
    # print("Draft Tube Tunnel Cost = $", C_dtt)

    # Tailrace Tunnels
    a_tt = "Yes" # app D75
    L_tt_or = 0 # L75
    # Tailrace tunnel diameter (ft) F75
    if a_tt == "Yes":
        if L_tt_or > 0:
            L_tt = L_tt_or
        elif P_G_avg <= 25:
            L_tt = 0
        else:
            L_tt = abs(L_c_ft - H_G_min)*0.25
    else:
        L_tt = 0
    # print("Tailrace Tunnel Diameter (ft) =", L_tt)
    u_tt = u_dtt # G75 Tailrace tunnel unit cost
    F_ttLoc = F_ppsLoc # H75
    F_ttEsc = F_ppsEsc # I75
    F_ttOth = 1.6 # J75 MAF for concrete lined tunnels
    u_tt_OR = 0 # M75
    # Adj unit costs
    if u_tt_OR > 0:
        u_ttAdj = u_tt_OR
    else:
        u_ttAdj = u_tt * F_ttLoc * F_ttEsc * F_ttOth
    # print("Tailrace Tunnel Unit Cost ($/ft) =", u_tt)
    # Tailrace tunnel cost N75
    C_tt = u_ttAdj * L_tt
    # print("Tailrace Tunnel Cost = $", C_tt)

    # Surface Penstock
    a_sp = "Yes" # app D76
    L_sp_or = 0 # L76
    # Surface penstock length (ft) F76
    if a_sp == "Yes":
        if L_sp_or > 0:
            L_sp = L_sp_or
        elif P_G_avg < 100 or P_loc == "Surface":
            L_sp = N_u * D_p
        else:
            L_sp = 0
    else:
        L_sp = 0
    # print("Surface Penstock Diameter (ft)", L_sp)
    # Sp unit cost ($/ft) G76
    if P_G_avg < 100 or P_loc == "Surface":
        if H_max <= 300:
            u_sp = 0.02 * D_p ** 1.885 * 1000
        elif H_max > 300 and H_max <= 500:
            u_sp = 0.0226 * D_p ** 1.9901 * 1000
        elif H_max > 500 and H_max <= 700:
            u_sp = 0.0365 * D_p ** 1.9417 * 1000
        elif H_max > 700 and H_max <= 1000:
            u_sp = 0.0483 * D_p ** 1.9694 * 1000
        elif H_max > 1000:
            u_sp = 0.0721 * D_p ** 1.9647 * 1000
    else:
        u_sp = 0
    F_spLoc = F_ppsLoc # H76
    F_spEsc = F_ppsEsc # I76
    F_spOth = 1.3 # J76 Suggested MAF for Surface Penstock
    u_sp_OR = 0 # M76
    # Adj Unit Cost K76
    if u_sp_OR > 0:
        u_spAdj = u_sp_OR
    else:
        u_spAdj = u_sp * F_spLoc * F_spEsc * F_spOth
    # print("Surface Penstock Unit Cost ($/ft) =",u_spAdj)
    # Surface Penstock Cost (N76)
    C_sp = u_spAdj * L_sp
    # print("Surface Penstock Cost = $", C_sp)

    # Surge Facilities (Reservoirs, Dams, & Waterways)
    a_sf = "Yes" # app D66
    n_sf_OR = 0 # L66
    # Percent of surge facilities F66
    if a_sf == "Yes":
        if n_sf_OR > 0:
            n_sf = n_sf_OR
        elif Sc == "Yes":
            n_sf = 0.4
        elif Sc == "No":
            n_sf = 0
        else:
            print("Surge Chambers needs to be Yes or No")
    else:
        n_sf = 0
    # print("Percent of Surge Facilities = ", n_sf * 100)
    # Cost of Surge Facilities N66
    C_sf = n_sf * (C_ulhpt + C_vs + C_pt + C_tt + C_dtt + C_sp)
    # print("Surge Facilities Cost = $", C_sf)

    # Powerstation Equipment
    # Pump/Motors
    a_pm = "Yes" #app D79
    # qty F79
    if a_pm == "Yes":
        N_pm = 1
    else:
        N_pm = 0
    # unit cost G79
    if P_G_avg > 100:
        u_pm = 0
    else:
        u_pm = 0.7799 * (Q_pump_avg * 448.83) ** 0.7442 * 1000
    F_pmLoc = F_ppsLoc # H79
    F_pmEsc = 1 #I79
    F_pmOth = 1 #J79
    u_pm_or = 0 # M79
    # adj unit costs K79
    if u_pm_or > 0:
        u_pmAdj = u_pm_or
    else:
        u_pmAdj = u_pm * F_pmLoc * F_pmEsc * F_pmOth
    C_pm = u_pmAdj * N_pm # cost N79

    # Generator/turbines:
    a_gt = "Yes" # app D80
    P_gt_or = 0 # L80
    # qty F80
    if a_gt =="Yes":
        if P_G_avg <= 100:
            if P_gt_or > 0:
                P_gt = P_gt_or
            else:
                P_gt = P_pps
        else:
            P_gt = 0
    else:
        P_gt = 0
    # unit cost # G80
    if P_G_avg > 100:
        u_gt = 0
    elif H_G_min <= 200:
        u_gt = 1051.9 * (P_gt/1000) ** -0.204 * 1.2009
    else:
        u_gt = 697.41 * (P_gt/1000) ** -0.329 * 1.2009
    F_gtLoc = F_ppsLoc # H80
    F_gtEsc = 1 # I80
    F_gtOth = 1 # J80
    u_gt_or = 0 # M80
    # adj unit cost K80
    if u_gt_or > 0:
        u_gtAdj = u_gt_or
    else:
        u_gtAdj = u_gt * F_gtLoc * F_gtEsc * F_gtOth
    C_gt = P_gt * u_gtAdj # N80
    
    # Powerstation Equipment Total
    a_pet = "Yes" # app D81
    P_pet_or = 0
    # PET power (kW) F81
    if a_pet == "Yes":
        if P_G_avg > 100:
            if P_pet_or > 0:
                P_pet = P_pet_or
            else:
                P_pet = P_G_max * 1000
        else:
            P_pet = 0
    else:
        P_pet = 0
    # print("Powerstation Equipment Power (kW) =", P_pet)
    # PET unit cost ($/kW) G81
    if P_G_avg <= 100:
        u_pet = 0
    elif Z_ps == "Underground":
        if P_G_max <= 80: # MW
            if N_u <= 2:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0609 * H_G_avg + 259.97
            elif N_u > 2 and N_u <= 3:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0609 * H_G_avg + 247.79
            elif N_u > 3 and N_u <= 4:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0617 * H_G_avg + 241.53
            elif N_u > 4:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0555 * H_G_avg + 232.3
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0485 * H_G_avg + 216.18
            elif N_u > 2 and N_u <= 3:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0462 * H_G_avg + 206.27
            elif N_u > 3 and N_u <= 4:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0453 * H_G_avg + 200.29
            elif N_u > 4:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0456 * H_G_avg + 196.43
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0544 * H_G_avg + 177.56
            elif N_u > 2 and N_u <= 3:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0488 * H_G_avg + 166.28
            elif N_u > 3 and N_u <= 4:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.048 * H_G_avg + 163.78
            elif N_u > 4:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0452 * H_G_avg + 157.75
        elif P_G_max > 225:
            if N_u <= 2:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0365 * H_G_avg + 139.89
            if N_u > 2 and N_u <= 3:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0355 * H_G_avg + 132.8
            if N_u > 3 and N_u <= 4:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.033 * H_G_avg + 129.39
            if N_u > 4:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0316 * H_G_avg + 125.28
    elif Z_ps == "Surface":
        if P_G_max <= 80:
            if N_u <= 2:
                u_pet = 8 * 10 ** -6 * H_G_avg ** 2 - 0.0174 * H_G_avg + 242.74
            elif N_u > 2 and N_u <= 3:
                u_pet = 8 * 10 ** -6 * H_G_avg ** 2 - 0.017 * H_G_avg + 230.3
            elif N_u > 3 and N_u <= 4:
                u_pet = 8 * 10 ** -6 * H_G_avg ** 2 - 0.0168 * H_G_avg + 223.7
            elif N_u > 4:
                u_pet = 8 * 10 ** -6 * H_G_avg ** 2 - 0.0173 * H_G_avg + 219.28
        elif P_G_max > 80 and P_G_max <= 125:
            if N_u <= 2:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0499 * H_G_avg + 212.36
            elif N_u > 2 and N_u <= 3:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0457 * H_G_avg + 200.9
            elif N_u > 3 and N_u <= 4:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.046 * H_G_avg + 196.81
            elif N_u > 4:
                u_pet = 2 * 10 ** -5 * H_G_avg ** 2 - 0.0501 * H_G_avg + 195
        elif P_G_max > 125 and P_G_max <= 225:
            if N_u <= 2:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0319 * H_G_avg + 165.52
            elif N_u > 2 and N_u <= 3:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0338 * H_G_avg + 159.73
            elif N_u > 3 and N_u <= 4:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0313 * H_G_avg + 155.12
            elif N_u > 4:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0309 * H_G_avg + 151.13
        elif P_G_max > 225:
            if N_u <= 2:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0447 * H_G_avg + 144.85
            elif N_u > 2 and N_u <= 3:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.041 * H_G_avg + 136.46
            elif N_u > 3 and N_u <= 4:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0391 * H_G_avg + 133.75
            elif N_u > 4:
                u_pet = 1 * 10 ** -5 * H_G_avg ** 2 - 0.0406 * H_G_avg + 131.67
    else:
        print("Error: Position of the Power Plant Station is either Underground or Surface")
    F_petLoc = F_ppsLoc # H81
    F_petEsc = F_ppsEsc # I81
    F_petOth = 1.7 # J81 suggested MAF for electromechanical devices
    u_pet_or = 0 # M81
    #adj unit cost K81
    if u_pet_or > 0:
        u_petAdj = u_pet_or
    else:
        u_petAdj = u_pet * F_petLoc * F_petEsc * F_petOth
    # print("Powerstation Equipment Unit Cost ($/kW) =", u_petAdj)
    # Cost of Powerstation Equipment (N81)
    C_pet = u_petAdj * P_pet
    # print("Powerstation Equipment Cost = $", C_pet)

    # Roads, Railroads, & Bridges 
    # Access Roads
    a_ar = "Yes" # app D84
    L_ar_or = 0 # L84
    #qty F84 Access road length (mi)
    if a_ar == "Yes":
        if L_ar_or > 0:
            L_ar = L_ar_or
        else:
            L_ar = L_ar
    else:
        L_ar = 0
    # print("Access Road Length (mi) =", L_ar)
    # Access road unit cost ($/mi) G84
    if ter_AR == "Steep" and Typ_ar == "New":
        u_ar = 439000
    elif ter_AR == "Mild" and Typ_ar == "New":
        u_ar = 283000
    elif ter_AR == "Flat" and Typ_ar == "New":
        u_ar = 189000
    elif ter_AR == "Steep" and Typ_ar == "Rebuild":
        u_ar = 293000
    elif ter_AR == "Mild" and Typ_ar == "Rebuild":
        u_ar = 186000
    elif ter_AR == "Flat" and Typ_ar == "Rebuild":
        u_ar = 123000
    else:
        print("Error: Access road terrain is either Steep, Mild, or Flat and Acess road type is either New or Rebuild")
    F_arLoc = F_ppsLoc # H84
    F_arEsc = F_ppsEsc # I84
    F_arOth = 1 # J84 suggested MAF for roads
    u_ar_OR = 0 # M84
    # adj unit cost K84
    if u_ar_OR > 0:
        u_arAdj = u_ar_OR
    else:
        u_arAdj = u_ar * F_arLoc * F_arEsc * F_arOth
    # print("Access Road Unit Cost ($/mi) =", u_arAdj)
    # Access Road Cost N84
    C_ar = L_ar * u_arAdj
    # print("Access Road Cost = $", C_ar)

    # Access Tunnels
    a_at = "Yes" # app D85
    L_at_or = 0 # L85
    # Length of Access Tunnels in ft
    if a_at == "Yes":
        if Z_ps == "Surface":
            L_at_ft = 0
        elif L_at_or > 0:
            L_at_ft = L_at_or
        else:
            L_at_ft = L_at * 5280
    else:
        L_at_ft = 0
    # print("Access Tunnel Length (ft) =", L_at_ft)
    # Unit cost of access tunnels ($/ft) G85
    if Z_ps == "Surface":
        u_at = 1E-9
    else:
        u_at = 2489.4 * L_at ** 0.118 
    F_atLoc = F_ppsLoc # H85
    F_atEsc = F_ppsEsc # I85
    F_atOth = 1 # suggested MAF for access and volt tunnels
    u_at_OR = 0 # M85
    if u_at_OR > 0:
        u_atAdj = u_at_OR
    else:
        u_atAdj = u_at * F_atLoc * F_atEsc * F_atOth
    # print("Access Tunnel Unit Cost ($/ft) =", u_at)
    # Cost of access tunnels N85
    C_at = L_at_ft * u_atAdj
    # print("Access Tunnel Cost = $", C_at)

    # Highway Realignment
    a_hr = "Yes" # app D86
    #qty F86
    if a_hr == "Yes":
        if Hr == "Yes":
            n_hr = 0.25
        else:
            n_hr = 0
    else:
        n_hr = 0
    C_hr = C_ar * n_hr # cost N86

    # Switchyard
    a_sy = "Yes" # D88
    # qty F88
    if a_sy == "Yes":
        N_sy = 1
    else:
        N_sy = 0
    # Switchyard unit cost ($/kV) G88
    if V_sub <= 160:
        u_sy = 1E6 * (-0.0643 * N_u ** 2 + 1.0743 * N_u - 0.48)
    elif V_sub > 160 and V_sub <= 230:
        u_sy = 1E6 * (-0.1 * N_u ** 2 + 1.6 * N_u - 1.1)
    elif V_sub > 230 and V_sub <= 345:
        u_sy = 1E6 * (-0.1607 * N_u ** 2 + 3.1007 * N_u - 1.91)
    elif V_sub > 345:
        u_sy = 1E6 * (-0.6286 * N_u ** 2 + 8.3086 * N_u - 6.45)
    # print("Switchyard Unit Cost ($M) =", u_sy_final)
    F_syLoc = F_ppsLoc # H88
    F_syEsc = F_ppsEsc # I88
    F_syOth = 1 #J88 MAF for switchyards
    u_sy_or = 0 #M88
    # adjusted unit cost
    if u_sy_or > 0:
        u_syAdj = u_sy_or
    else:
        u_syAdj = u_sy * F_syLoc * F_syEsc * F_syOth
    
    # Total cost of switchyard N88
    C_sy = u_syAdj * N_sy
    # print("Switchyard Cost = $", C_sy)

    # Transmission Lines
    a_tl = "Yes" # app D90
    #qty F90
    if a_tl == "Yes":
        L_tl = L_trans
    else:
        L_tl = 0
    # TL unit cost 
    if V_trans <= 138:
        u_tl = (0.0043 * P_G_max ** 2 - 0.028 * P_G_max + 108.72)
    elif V_trans > 138 and V_trans <= 230:
        u_tl = (0.0007 * P_G_max ** 2 - 0.0382 * P_G_max + 169.98)
    elif V_trans > 230 and V_trans <= 345:
        u_tl = (0.0003 * P_G_max ** 2 - 0.2536 * P_G_max + 335.57)
    elif V_trans > 345:
        u_tl = (4 * 10 ** -5 * P_G_max ** 2 - 0.0652 * P_G_max + 428.5)
    F_tlLoc = F_ppsLoc # H90
    F_tlEsc = F_ppsEsc # I90
    F_tlOth = 1.3 # J90 suggested MAF for transmission works
    u_tl_OR = 0 # M90
    # adj unit cost
    if u_tl_OR > 0:
        u_tlAdj = u_tl_OR
    else:
        u_tlAdj = u_tl * F_tlLoc * F_tlEsc * F_tlOth * 1000 * m_trans * M_trans
    # print("Transmission Lines Unit Cost ($1000s) =", u_tlAdj)
    
    # Transmission Line Cost ($) N90
    C_tl = u_tlAdj * L_tl 
    # print("Transmission Line Cost = $", C_tl)

    # Other costs
    a_ws = "Yes" # app D93
    #qty F93
    if a_ws == "Yes":
        if Ws == "Yes":
            P_ws = P_G_max * 1000
        else:
            P_ws = 0
    else:
        P_ws = 0
    u_ws = 204.036 # G93 unit cost $/kW
    F_wsLoc = 1 # H93
    F_wsEsc = 1 # I93
    F_wsOth = 1 # J93
    u_ws_or = 0 # M93
    # adj unit cost K93
    if u_ws_or > 0:
        u_wsAdj = u_ws_or
    else:
        u_wsAdj = u_ws * F_wsEsc * F_wsLoc * F_wsOth
    C_ws = u_wsAdj * P_ws # N93

    # De/Mobilization
    a_md = "Yes" # app D94
    # qty F94
    if a_md == "Yes":
        if Hr == "Yes":
            P_md = P_G_max * 1000
        else:
            P_md = 0
    else:
        P_md = 0
    u_md = 246.46 # $/kW G94
    F_mdLoc = 1 # H94
    F_mdEsc = 1 # I94
    F_mdOth = 1 # J94
    u_md_or = 0 # M94
    # adj unit cost K94
    if u_md_or > 0:
        u_mdAdj = u_md_or
    else:
        u_mdAdj = u_md * F_mdLoc * F_mdEsc * F_mdOth
    C_md = u_mdAdj * P_md # N94

    # Soft Costs
    # Sales Tax
    a_st = "Yes" # app D97
    t_s_OR = 0 # L97
    # tax rate F97
    if a_st == "Yes":
        if t_s_OR > 0:
            t_s = t_s_OR
        else:
            t_s = t_sales
    else:
        t_s = 0
    # print("Sales Tax (%) =", t_s * 100)
    # Sum of pre-tax costs (C_sum)
    C_sum = C_land + C_pps + C_uds + C_uri + C_sf + C_lri + C_lrds + C_ulhpt + C_vs + C_pt + C_dtt + C_tt + C_sp + C_pm + C_gt + C_pet + C_ar + C_at + C_sy + C_tl
    # Sales Tax Cost
    C_sales = t_s * n_mE * C_sum
    # print("Sales Tax Cost = $", C_sales)

    # Contingency
    a_cont = "Yes" # D98
    # tax rate F98
    if a_cont == "Yes":
        t_cont = 0.25
    else:
        t_cont = 0
    # print("Contingency (%) =", t_con * 100)
    # Contingency cost N98
    C_cont = t_cont * C_sum
    # print("Contingency Cost = $", C_cont)

    # EPC tax 
    a_epc = "Yes" # D99
    t_epc_OR = 0 # L99
    # tax rate F99
    if a_epc == "Yes":
        if t_epc_OR > 0:
            t_epc = t_epc_OR
        else:
            t_epc = t_EPC
    else:
        t_epc = 0
    # print("EPC Cost (%) =", t_epc * 100)
    # EPC Cost N99
    C_epc = C_sum * t_epc * n_mE
    # print("EPC Cost = $", C_epc)

    # Developer Cost
    a_dev = "Yes" # D100
    t_dev_or = 0 # L100
    # tax rate F100
    if a_dev == "Yes":
        if t_dev_or > 0:
            t_dev = t_dev_or
        else:
            t_dev = t_DC
    else:
        t_dev = 0
    # print("Developer Cost (%) =", t_dev * 100)
    C_dev = t_dev * C_sum # N100
    # print("Developer Cost = $", C_dev)

    # Overhead and Profit
    a_op = "Yes" #D101
    t_op_OR = 0 # L101
    # tax rate F101
    if a_op == "Yes":
        if t_op_OR > 0:
            t_op = t_op_OR
        else:
            t_op = t_OP
    else:
        t_op = 0
    # print("Overhead and Profit (%) =", t_op * 100)
    C_op = C_sum * t_op * n_mE
    # print("Overhead and Profit = $", C_op)

    # TOTAL COST for PSH
    C_total = C_sum + C_ws + C_md + C_sales + C_cont + C_epc + C_dev + C_op
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
# psh_costV2(h_vals, 21.6, 1849, 2.6)
