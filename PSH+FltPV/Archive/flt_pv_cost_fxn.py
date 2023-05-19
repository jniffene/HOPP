    # Floating PV Cost Model from NREL
import numpy as np
import numpy_financial as npf
from pathlib import Path


def fltPVcost(P_cap_kW):
    P_cap = P_cap_kW/1000 # capacity in MW
    I_int = P_cap * 1.28524387305415 * 1000000 # initial investment
    I_1st = 0.04 * 0.2 * 10 * 10 ** 6 # 1st follow on investment
    n_1st = 10 # 1st follow-on investment year
    I_2nd = 0 # 2nd follow on investment
    n_2nd = 20 # 2nd follow on investment year
    r_i = 0.05 # interest rates
    Lev = 0.718 # leverage
    n_debt = 18 # debt term
    r_enom = 0.0775 # nominal equity rate
    r_inf = 0.025 # inflation rate
    r_ereal = ((1 + r_enom)/(1 + r_inf)) - 1 # real equity rate
    r_tax = 0.21 + 0.06 * (1 - 0.21) # tax rate
    v_res = 0 # residual value
    Pr = 1483 * 1.03 # initial annual system production
    f_pv2b = 0 # percent of gen solar fed to battery
    Q_pv = 0 # round trip energy losses from PV/battery/grid
    Q_grid = 0 # round trip energy losses from battery/grid
    C_om = 15.5 # O&M $/kW*yr
    d_pv = 0.007 # PV degradation
    E_grid = 0 # annual electricity purchased from the grid
    itc = 0.26 # ITC
    n_total = 30

    # Depreciation schedule
    d_1 = 0.2 # depreciation for year 1
    d_2 = 0.32 
    d_3 = 0.192
    d_4 = 0.115
    d_5 = 0.115
    d_6 = 0.058
    d_i = [d_1, d_2, d_3, d_4, d_5, d_6] # depreciation over multiple years

    # Depreciation of Initial Investment
    D_ii = np.empty(n_total)
    for i in range(len(D_ii)):
        if i+1 <= len(d_i):
            D_ii[i] = I_int * d_i[i] * (1 - itc/2)
        else:
            D_ii[i] = 0   

    # Depreciation of 1st Follow-On Investment
    D_1st = np.empty(n_total)
    for i in range(len(D_1st)):
        if i+1 <= n_1st:
            D_1st[i] = 0
        elif i+1 <= n_1st + len(d_i):
            D_1st[i] = I_1st * d_i[i-n_1st]
        else:
            D_1st[i] = 0
    #print(D_1st)

    # Depreciation of 2nd Follow-On Investment
    D_2nd = np.empty(n_total)
    for i in range(len(D_2nd)):
        if i+1 <= n_2nd:
            D_2nd[i] = 0
        elif i+1 <= n_2nd + len(d_i):
            D_2nd[i] = I_2nd * d_i[i-n_2nd]
        else:
            D_2nd[i] = 0
    # print(D_2nd)

    # O&M yearly costs
    OMy = np.empty(n_total)
    for i in range(len(OMy)):
        OMy[i] = C_om * P_cap * 1000
    # print(OMy)

    # Direct solar production (MWh)
    E_pv = np.empty(n_total)
    for i in range(len(E_pv)):
        n = i + 1
        E_pv[i] = P_cap * Pr * (1 - f_pv2b) * (1 - d_pv) ** (n - 1)
    # print(E_pv)

    # Production of energy through battery (MWh)
    E_bat = np.empty(n_total)
    for i in range(len(E_bat)):
        n = i + 1
        E_bat[i] = P_cap * Pr * f_pv2b * (1 - Q_pv) * (1 - d_pv)**(n - 1)

    # Principal payment
    C_pp = np.empty(n_total)
    for i in range(len(C_pp)):
        n = i + 1
        if n <= n_debt:
            C_pp[i] = -1 * npf.ppmt(r_i, n, n_debt, I_int * Lev)
        else:
            C_pp[i] = 0
    # print(C_pp)

    # Interest payment
    C_ip = np.empty(n_total)
    for i in range(len(C_ip)):
        n = i + 1
        if n <= n_debt:
            C_ip[i] = -1 * npf.ipmt(r_i, n, n_debt, I_int * Lev)
        else:
            C_ip[i] = 0
    # print(C_ip)

    # Charging costs
    C_c = np.empty(n_total)
    for i in range(len(C_c)):
        C_c[i] = 0

    # Electricity purchased from the grid
    Elect_grid = np.empty(n_total)
    for i in range(len(Elect_grid)):
        Elect_grid[i] = 0

    # LCOSS
    lcoss = (I_int * (1-Lev) - I_int * itc + I_1st/(1 + r_ereal)**n_1st + I_2nd/(1 + r_ereal)**n_2nd - r_tax * npf.npv(r_enom, D_ii) - r_tax * npf.npv(r_enom, D_1st) - r_tax * npf.npv(r_enom, D_2nd) + (1 - r_tax)*(npf.npv(r_enom, OMy) + npf.npv(r_enom, C_ip) + npf.npv(r_ereal, C_c) + (v_res/(1+v_res))**30) + npf.npv(r_enom, C_pp))/((1-r_tax)*(npf.npv(r_ereal, E_pv) + npf.npv(r_ereal, E_bat) + (1-Q_grid)*npf.npv(r_ereal, Elect_grid)))
    # print("LCOSS = $", lcoss, "/ MWh")
    lcoss_kwh = lcoss / 1000
    # print("LCOSS = $", lcoss * 1000, "/ kWh")
    return lcoss_kwh

# cost_test = fltPVcost(15500)
# print("Floating PV Cost ($/kWh) = ",cost_test)