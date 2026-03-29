# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 18:34:20 2026

@author: kerem
"""
import gurobipy as gp
from gurobipy import GRB

# Veri: Görevlerin min süresi, max süresi, min maliyeti, max maliyeti ve öncülü

tasks = [1, 2, 3, 4, 5, 6, 7]

min_time  = {1:6,  2:8,  3:16, 4:14, 5:4,  6:12, 7:2}
max_time  = {1:12, 2:16, 3:24, 4:20, 5:16, 6:16, 7:12}
min_cost  = {1:1600, 2:2400, 3:2900, 4:1900, 5:3800, 6:2900, 7:1300}
max_cost  = {1:1000, 2:1800, 3:2000, 4:1300, 5:2000, 6:2200, 7:800}


# Öncül ilişkileri

precedences = [(2,3), (1,4), (2,4), (3,5), (3,6), (4,7)]


# Proje süre sınırı

deadline = 40


# Görevlerin maliyeti, süreyle ters orantılı olacak şekilde değişiyor.
# Kısa sürede tamamlamak pahalı, uzun sürede tamamlamak ucuz.

slope = {i: (max_cost[i] - min_cost[i]) / (max_time[i] - min_time[i]) for i in tasks}



# Model

model = gp.Model("Proje_Cizelgeleme")


# Değişkenler
# s[i] = i. görevin başlangıç zamanı
# d[i] = i. göreve ayrılan süre

s = model.addVars(tasks, name="s", lb=0)
d = model.addVars(tasks, name="d", lb=0)

# Amaç fonksiyonu: Min(toplam maliyet)

model.setObjective(
    gp.quicksum(min_cost[i] + slope[i] * (d[i] - min_time[i]) for i in tasks),
    GRB.MINIMIZE
)


# Kısıtlar
# Her görevin süresi min ve max arasında olmalı

for i in tasks:
    model.addConstr(d[i] >= min_time[i], name=f"min_sure_{i}")
    model.addConstr(d[i] <= max_time[i], name=f"max_sure_{i}")

# Öncül kısıtları: öncül görev tamamlanmalı

for (p, t) in precedences:
    model.addConstr(s[t] >= s[p] + d[p], name=f"oncel_{p}_{t}")

# Tüm görevler 40 gün içinde bitmeli

for i in tasks:
    model.addConstr(s[i] + d[i] <= deadline, name=f"deadline_{i}")


# Modelin çözümü

model.optimize()


print("\n" + "="*60)
print("OPTİMAL ÇÖZÜM")
print("="*60)
if model.status == GRB.OPTIMAL:
    print(f"\nAmaç Fonksiyonu (Toplam Maliyet): {model.objVal:.2f}")
    print(f"\n{'Görev':<8} {'Başlangıç':>12} {'Süre':>8} {'Maliyet':>10}")
    print("-"*42)
    for i in tasks:
        cost_i = min_cost[i] + slope[i] * (d[i].X - min_time[i])
        print(f"{i:<8} {s[i].X:>12.2f} {d[i].X:>8.2f} {cost_i:>10.2f}")