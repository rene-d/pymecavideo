import nbformat as nbf

def genere_notebook(pts, graphs=(True,True,True,True,True)):
    """
    fonction qui génère et retourne un Notebook Jupyter
    Arguments : 
    * pts : tuple [str] (t, x, y)
    * graphs : tuple [True/False] (chronogramme, vitesse, vecteurs variation de vitesse, accélération, énergies)
    """
    nb = nbf.v4.new_notebook()
    
    entete1 = """\
%matplotlib inline
%config InlineBackend.figure_format = 'svg'"""

    entete2 = """\
# Imports
import numpy as np
import matplotlib.pyplot as plt
# Paramètres matplotlib
plt.rcParams["figure.figsize"] = (9, 6)
plt.style.use('seaborn-whitegrid')
markersize = 10
style = 'b+'"""

    coord = """\
# Coordonnées de Pymecavideo
t = {0}
x = {1}
y = {2}""".format(pts[0], pts[1], pts[2])

    chrono0 = """### Chronogramme des positions"""

    chrono1 = """\
plt.plot(x, y, style, markersize = markersize)
plt.ylabel('Hauteur (m)')
plt.xlabel('Distance (m)')
plt.title("Chronogramme des positions")
plt.gca().set_aspect('equal', adjustable='datalim')
plt.show()"""

    vitesse0 = """### Vecteurs vitesse"""

    vitesse1 = """\
Δx = np.array([x[i+1]-x[i-1] for i in range(1, len(x)-1)])
Δy = np.array([y[i+1]-y[i-1] for i in range(1, len(y)-1)])
Δt = np.array([t[i+1]-t[i-1] for i in range(1, len(t)-1)])
vx = Δx/Δt
vy = Δy/Δt
plt.plot(x, y, style, markersize = markersize)
plt.ylabel('Hauteur (m)')
plt.title("Vecteurs vitesse")
plt.xlabel('Distance (m)')
plt.grid(True)
plt.quiver(x[1:-1], y[1:-1], vx, vy, scale_units = 'xy', angles = 'xy', width = 0.003)
plt.gca().set_aspect('equal', adjustable='datalim')
plt.show()"""

    variation0 = """### Vecteurs variation de vitesse"""

    variation1 = """\
Δvx = np.array([vx[i+1]-vx[i-1] for i in range(1, len(vx)-1)])
Δvy = np.array([vy[i+1]-vy[i-1] for i in range(1, len(vy)-1)])
plt.plot(x, y, style, markersize = markersize)
plt.ylabel('Hauteur (m)')
plt.xlabel('Distance (m)')
plt.title("Vecteurs variation de vitesse")
plt.grid(True)
plt.quiver(x[2:-2], y[2:-2], Δvx, Δvy, scale_units = 'xy', angles = 'xy', width = 0.003)
plt.gca().set_aspect('equal', adjustable='datalim')
plt.show()"""

    acceleration0 = """### Vecteurs accélération"""

    acceleration1 = """\
Δt_ = np.array([t[i+1]-t[i-1] for i in range(2, len(t)-2)])
Δvx = np.array([vx[i+1]-vx[i-1] for i in range(1, len(vx)-1)])
Δvy = np.array([vy[i+1]-vy[i-1] for i in range(1, len(vy)-1)])
ax = Δvx/Δt_
ay = Δvy/Δt_
plt.plot(x, y, style, markersize = markersize)
plt.ylabel('Hauteur (m)')
plt.xlabel('Distance (m)')
plt.title("Vecteurs accélération")
plt.grid(True)
plt.quiver(x[2:-2], y[2:-2], ax, ay, scale_units = 'xy', angles = 'xy', width = 0.003)
plt.gca().set_aspect('equal', adjustable='datalim')
plt.show()"""

    energie0 = """### Energies"""

    energie1 = """\
# Données
m = 1.00 # Masse du système (kg)
g = 9.81 # Intensité de la pesanteur (N/kg)"""

    energie2 = """\
t_ = t[1:-1]
Δx = np.array([x[i+1]-x[i-1] for i in range(1, len(x)-1)])
Δy = np.array([y[i+1]-y[i-1] for i in range(1, len(y)-1)])
Δt = np.array([t[i+1]-t[i-1] for i in range(1, len(t)-1)])
vx = Δx/Δt
vy = Δy/Δt
v = np.sqrt(vx**2+vy**2)
Ec = 0.5*m*v**2
Ep = m*g*y[1:-1]
Em = Ec + Ep
plt.plot(t_, Ec, label = 'Ec')
plt.plot(t_, Ep, label = 'Ep')
plt.plot(t_, Em, label = 'Em')
plt.xlabel('Temps (s)')
plt.ylabel('Energies (J)')
plt.legend()
plt.show()"""
    
    #Méta-données
    kernelspec = { "display_name" : "Python 3", "language" : "python", "name" : "python3"}
    language_info = { "codemirror_mode": {"name": "ipython", "version": 3}}
    nb['metadata']['kernelspec'] = kernelspec
    nb['metadata']['language_info'] = language_info
    nb['metadata']['file_extension'] = ".py"
    nb['metadata']['mimetype'] = "text/x-python"
    nb['metadata']['name'] = "python"
    nb['metadata']['nbconvert_exporter'] = "python"
    nb['metadata']['pygments_lexer'] = "ipython3"
    nb['metadata']['version'] = "3.9.2"
    # Cellules                   
    nb['cells'] = [nbf.v4.new_code_cell(entete1),
                nbf.v4.new_code_cell(entete2),
                nbf.v4.new_code_cell(coord)]
    if graphs[0] :
        nb['cells'] += [nbf.v4.new_markdown_cell(chrono0),
                        nbf.v4.new_code_cell(chrono1)]
    if graphs[1] :
        nb['cells'] += [nbf.v4.new_markdown_cell(vitesse0),
                        nbf.v4.new_code_cell(vitesse1)]
    if graphs[2] :
        nb['cells'] += [nbf.v4.new_markdown_cell(variation0),
                        nbf.v4.new_code_cell(variation1)]
    if graphs[3] :
        nb['cells'] += [ nbf.v4.new_markdown_cell(acceleration0),
                        nbf.v4.new_code_cell(acceleration1)]
    if graphs[4] :
        nb['cells'] += [ nbf.v4.new_markdown_cell(energie0),
                        nbf.v4.new_code_cell(energie1),
                        nbf.v4.new_code_cell(energie2)]
    return nb





