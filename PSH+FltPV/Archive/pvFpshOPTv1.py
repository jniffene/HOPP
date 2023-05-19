import numpy as np
from pymoo.core.problem import ElementwiseProblem
from psh_flt_solar_fxn import psh_flt_pvFXN
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination
from pymoo.optimize import minimize
import matplotlib.pyplot as plt

class pvFpshOpt(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=2,
                        n_obj=2,
                        n_ieq_constr = 0,
                        xl=np.array([0,0]),
                        # max area = 10,000m2 
                        # max depth = 10m
                        xu=np.array([100000, 10]))
    def _evaluate(self, x, out, *args, **kwargs):
        [f1, f2] = psh_flt_pvFXN(x[0], x[1])
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
plt.figure(figsize=(7,5))
plt.scatter(X[:,0], X[:,1], s=30,
            facecolors='none', edgecolors='r')
plt.xlim(xl[0], xu[0])
plt.ylim(xl[1], xu[1])
plt.title("Design Space")
plt.xlabel("PSH Reservoir Area (m2)")
plt.ylabel("PSH Reservoir Depth (m)")
plt.show()

plt.figure(figsize=(7,5))
plt.scatter(F[:,0],F[:,1], s=30,
            facecolors='none', edgecolors='blue')
plt.title("Objective Space")
plt.xlabel("Fraction that the Grid is Needed")
plt.ylabel("PSH + PV LCOE ($/kwh)")
plt.show()