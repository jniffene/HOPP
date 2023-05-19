import numpy as np
from pymoo.core.problem import ElementwiseProblem
from psh_flt_solar_fxnV7 import psh_flt_pvFXNv7
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination
from pymoo.optimize import minimize
import matplotlib.pyplot as plt
from pymoo.decomposition.asf import ASF
from pshTankVis import plot_3D_cylinder
from psh_flt_solar_details import psh_flt_pvDetails

A_max = 100000 # max area = 100,000m2
z_max = 100 # max depth = 100m
h_max = 100 # max static head = 100m
P_kW_max = 10000 # max motor capacity = 10 MW

class pvFpshOpt(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=4,
                        n_obj=4,
                        n_ieq_constr = 0,
                        xl=np.array([1,1,1,1]),
                        xu=np.array([A_max, z_max, h_max, P_kW_max]))
    def _evaluate(self, x, out, *args, **kwargs):
        [f1, f2, f3, f4] = psh_flt_pvFXNv7(x[0], x[1], x[2], x[3])
        out["F"] = [f1,f2,f3,f4] 

problem =  pvFpshOpt()

algorithm = NSGA2(
    pop_size=100,
    n_offsprings=25,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation= PM(eta=20),
    eliminate_duplicates=True
)

termination = get_termination("n_gen", 40)

res = minimize(problem,
               algorithm,
               termination,
               seed=1,
               save_history=True,
               verbose=True)
X = res.X
F = res.F

# Normalization of objectives
fl=F.min(axis=0)
fu=F.max(axis=0)
print(f"Range f1 (Frac Grid Used): [{fl[0]}, {fu[0]}]")
print(f"Range f2 ($/kWh): [{fl[1]}, {fu[1]}]")
print(f"Range f3 (PSH Capital Cost $): [{fl[2]}, {fu[2]}]")
print(f"Range f4 (Utilization Factor): [{fl[3]}, {fu[3]}]")


approx_ideal = fl
approx_nadir = fu
nF = (F - approx_ideal)/(F - approx_nadir)

weights = np.array([0.95,0.02,0.02,0.01])
decomp = ASF()
i = decomp.do(nF, 1 / weights).argmin()
print("Best regarding ASF: Point \ni = %s\nX = %s\nF = %s" % (i, X[i], F[i]))
print("Recommended Design:") 
print("Reservoir Area =",X[i,0],"m2")
print("Reservoir Max Depth =",X[i,1],"m")
print("Reservoir Static Head =",X[i,2],"m")
print("Motor/ Generatory Capacity =",X[i,3],"kW")
print("Percent the Grid is Needed =",F[i,0]*100, "%")
print("PSH + PV LCOE ($/kWh) =", F[i,1])
print("PSH Capital Cost = $", F[i,2])
print("PSH Utilization Factor =", F[i,3]*-100, "%")



xl,xu = problem.bounds()
fig = plt.figure(figsize=(7,5))
ax = fig.add_subplot(projection="3d")
ax.grid(visible = True, color='grey', linestyle='-.', linewidth = 0.3, alpha = 0.2)
ax.scatter(X[:,0], X[:,1], X[:,2], color = 'red', marker = 'o')
ax.scatter(X[i,0], X[i,1], X[i,2], color ='green', marker = '*',label="Point Determined with Weights (ASF)")
plt.legend()
ax.set_xlim(xl[0], xu[0])
ax.set_ylim(xl[1], xu[1])
ax.set_zlim(xl[2], xu[2])
plt.title("Design Space")
ax.set_xlabel('PSH Reservoir Area (m2)')
ax.set_ylabel('PSH Reservoir Depth (m)')
ax.set_zlabel('PSH Static Head (m)')
plt.show()


fig = plt.figure(figsize=(7,5))
ax = fig.add_subplot(projection="3d")
ax.grid(visible = True, color='grey', linestyle='-.', linewidth = 0.3, alpha = 0.2)
ax.scatter(F[:,0]*100, F[:,1], F[:,2], color = 'blue', marker = 'o')
ax.scatter(approx_ideal[0]*100, approx_ideal[1], approx_ideal[2], color ='red', marker = '*', label="Ideal Point (Approx)")
ax.scatter(approx_nadir[0]*100, approx_nadir[1], approx_nadir[2], color ='black', marker = 'x', label="Nadir Point (Approx)")
ax.scatter(F[i,0]*100, F[i,1], F[i,2], color ='green', marker = '*',label="Point Determined with Weights (ASF)")
plt.legend()
plt.title("Objective Space")
ax.set_xlabel('Percent that the Grid is Needed')
ax.set_ylabel('PSH + PV LCOE ($/kwh)')
ax.set_zlabel('PSH Capital Cost ($)')
plt.show()

print("Additional Details on Design:")
psh_flt_pvDetails(X[i,0],X[i,1],X[i,2], X[i,3])

# params
A_opt = X[i,0]
radius = np.sqrt(A_opt/np.pi)
height = X[i,1]
elevation = X[i,2]
resolution = 100
color = 'c'
x_center = 0
y_center = 0
R_max = np.sqrt(A_max/np.pi)
Z_max = z_max + h_max

plot_3D_cylinder(radius, height, elevation=elevation, resolution=resolution, color=color, x_center=x_center, y_center=y_center, r_max=R_max, z_max=Z_max)