# Floating PV LCOE model from Shyam 

import math
import pandas as pd

def flt_pv_cost_shy(P_cap, C_replacement):
    inr2usd = 0.01
    C_mod = 24 # inr/W
    C_inv = 2 # inr/W
    C_struct = 12.8 # inr/W
    C_bos = 3.5 # inr/W
    C_install = 4.7 # inr/W
    C_civ = 1.2 # inr/W
    C_site = 0.6 # inr/W
    C_h2o = 0.9 # inr/W
    C_trans = 0.3 # inr/W
    
    C_cap = inr2usd*P_cap*(C_mod + C_inv + C_struct + C_bos + C_install + C_civ + C_site + C_h2o + C_trans)