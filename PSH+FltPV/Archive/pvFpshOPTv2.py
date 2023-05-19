import numpy as np
from pymoo.core.problem import ElementwiseProblem
from psh_flt_solar_fxnV2 import psh_flt_pvFXNv2
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination
from pymoo.optimize import minimize
import matplotlib.pyplot as plt


class pvFpshOpt(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=3,
                        n_obj=2,
                        n_ieq_constr = 0,
                        xl=np.array([1,1,1]),
                        # max area = 100,000m2 
                        # max depth = 100m
                        # max static head = 100m
                        xu=np.array([100000, 100, 100]))
    def _evaluate(self, x, out, *args, **kwargs):
        [f1, f2] = psh_flt_pvFXNv2(x[0], x[1], x[2])
        out["F"] = [f1,f2] 

problem =  pvFpshOpt()

algorithm = NSGA2(
    pop_size=40,
    n_offsprings=10,
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

xl,xu = problem.bounds()
fig = plt.figure(figsize=(7,5))
ax = fig.add_subplot(projection="3d")
ax.grid(visible = True, color='grey', linestyle='-.', linewidth = 0.3, alpha = 0.2)
ax.scatter(X[:,0], X[:,1], X[:,2], color = 'red', marker = 'o')
ax.set_xlim(xl[0], xu[0])
ax.set_ylim(xl[1], xu[1])
ax.set_zlim(xl[2], xu[2])
plt.title("Design Space")
ax.set_xlabel('PSH Reservoir Area (m2)')
ax.set_ylabel('PSH Reservoir Depth (m)')
ax.set_zlabel('PSH Static Head (m)')
plt.show()

plt.figure(figsize=(7,5))
plt.scatter(F[:,0],F[:,1], s=30,
            facecolors='none', edgecolors='blue')
plt.title("Objective Space")
plt.xlabel("Fraction that the Grid is Needed")
plt.ylabel("PSH + PV LCOE ($/kwh)")
plt.show()