import gurobipy as gp
from gurobipy import GRB

"""
700 Stunden/Monat -> Maschine 1
500 Stunden/Monat -> Maschine 2

bis zu 600 Stunden/Monat für 8€/Stunde (Expertenarbeit)
bis zu 650 Stunden/Monat für 6€/Stunde (Ungelernte Arbeit)

                                                    y_u                 y_e
Produkt 1:  Maschine 1 (11)  Maschine 2 (4)  Ungelernte Arbeiter (8) Experten (7)    Preis (300)
Produkt 2:  Maschine 1 (7)   Maschine 2 (6)  Ungelernte Arbeiter (5) Experten (8)    Preis (260)
Produkt 3:  Maschine 1 (6)   Maschine 2 (5)  Ungelernte Arbeiter (5) Experten (7)    Preis (220)
Produkt 4:  Maschine 1 (5)   Maschine 2 (4)  Ungelernte Arbeiter (6) Experten (4)    Preis (180)

max x_1 * 300 + x_2 * 260 + x_3 * 220 + x_4 * 180 - y_u * 6 - y_e * 8

s.t.    y_u <= 650
        y_e <= 600
        11x_1 + 7x_2 + 6x_3 + 5x_4 <= 700
        4x_1 + 6x_2 + 5x_3 + 4x_4 <= 500
        8x_1 + 5x_2 + 5_x3 + 6x_4 - y_u <= 0
        7x_1 + 8x_2 + 7_x3 + 4x_4 = y_e
"""

import gurobipy as gp
from gurobipy import GRB

try:
    # Create a new model
    m = gp.Model("mip1")

    # Create variables
    x_1 = m.addVar(vtype=GRB.CONTINUOUS, name="x_1")
    x_2 = m.addVar(vtype=GRB.CONTINUOUS, name="x_2")
    x_3 = m.addVar(vtype=GRB.CONTINUOUS, name="x_3")
    x_4 = m.addVar(vtype=GRB.CONTINUOUS, name="x_4")
    y_u = m.addVar(vtype=GRB.CONTINUOUS, name="y_u")
    y_e = m.addVar(vtype=GRB.CONTINUOUS, name="y_e")

    # Set objective
    m.setObjective(x_1 * 300 + x_2 * 260 + x_3 * 220 + x_4 * 180 - y_u * 6 - y_e * 8, GRB.MAXIMIZE)

    m.addConstr(y_u <= 650, "c0")
    m.addConstr(y_e <= 600, "c1")
    m.addConstr(11 * x_1 + 7 * x_2 + 6 * x_3 + 5 * x_4 <= 700, "c2")
    m.addConstr(4 * x_1 + 6 * x_2 + 5 * x_3 + 4 * x_4 <= 500, "c3")
    m.addConstr(8 * x_1 + 5 * x_2 + 5 * x_3 + 6 * x_4 - y_e <= 0, "c4")
    m.addConstr(7 * x_1 + 8 * x_2 + 7 * x_3 + 4 * x_4 - y_u == 0, "c5")
    m.addConstr(x_1 >= 0, "c6")
    m.addConstr(x_2 >= 0, "c7")
    m.addConstr(x_3 >= 0, "c8")
    m.addConstr(x_4 >= 0, "c9")
    m.addConstr(y_u >= 0, "c10")
    m.addConstr(y_e >= 0, "c11")

    # Optimize model
    m.optimize()

    for v in m.getVars():
        print(f"{v.VarName} {v.X:g}")

    print(f"Obj: {m.ObjVal:g}")

except gp.GurobiError as e:
    print(f"Error code {e.errno}: {e}")

except AttributeError:
    print("Encountered an attribute error")