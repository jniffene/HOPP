# Tank visualizer code test
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d as art3d
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

def plot_3D_cylinder(radius, height, elevation=0, resolution=100, color='r', x_center = 0, y_center = 0, r_max = 10, z_max = 10, A_ca=1.53):
    fig=plt.figure()
    ax = Axes3D(fig, azim=30, elev=30, auto_add_to_figure=False)
    fig.add_axes(ax)

    x = np.linspace(x_center-radius, x_center+radius, resolution)
    z = np.linspace(elevation, elevation+height, resolution)
    X, Z = np.meshgrid(x, z)

    Y = np.sqrt(radius**2 - (X - x_center)**2) + y_center # Pythagorean theorem

    ax.plot_surface(X, Y, Z, linewidth=0, color=color)
    ax.plot_surface(X, (2*y_center-Y), Z, linewidth=0, color=color)

    floor = Circle((x_center, y_center), radius, color=color)
    ax.add_patch(floor)
    art3d.pathpatch_2d_to_3d(floor, z=elevation, zdir="z")

    ceiling = Circle((x_center, y_center), radius, color=color)
    ax.add_patch(ceiling)
    art3d.pathpatch_2d_to_3d(ceiling, z=elevation+height, zdir="z")

    thin_radius = 0.5*radius

    x2 = np.linspace(x_center-thin_radius, x_center+thin_radius, resolution)
    z2 = np.linspace(0, elevation, resolution)
    X2, Z2 = np.meshgrid(x2, z2)

    Y2 = np.sqrt(radius**2 - (X2 - x_center)**2) + y_center # Pythagorean theorem

    ax.plot_surface(X2, Y2, Z2, linewidth=0, color='k')
    ax.plot_surface(X2, (2*y_center-Y2), Z2, linewidth=0, color='k')

    A_total = np.pi*(radius**2)

    A_pv = A_total - np.sqrt(2 * np.pi * A_total * A_ca)

    r_pv = np.sqrt(A_pv/np.pi)

    floor2 = Circle((x_center, y_center), r_pv, color='y')
    ax.add_patch(floor2)
    art3d.pathpatch_2d_to_3d(floor2, z=elevation, zdir="z")

    ceiling2 = Circle((x_center, y_center), r_pv, color='y')
    ax.add_patch(ceiling2)
    art3d.pathpatch_2d_to_3d(ceiling2, z=elevation+height+2, zdir="z")

    ax.set_xlabel('Length (m)')
    ax.set_ylabel('Width (m)')
    ax.set_zlabel('Height (m)')
    ax.axes.set_xlim3d(left=-1*r_max, right=r_max) 
    ax.axes.set_ylim3d(bottom=-1*r_max, top=r_max) 
    ax.axes.set_zlim3d(bottom=0, top=z_max)

    plt.show()

# params
# A_opt = 1220
# radius = np.sqrt(A_opt/np.pi)
# height = 60
# elevation = 68
# resolution = 100
# color = 'c'
# x_center = 0
# y_center = 0
# R_max = 178
# Z_max = 200

# plot_3D_cylinder(radius, height, elevation=elevation, resolution=resolution, color=color, x_center=x_center, y_center=y_center, r_max=R_max, z_max=Z_max)