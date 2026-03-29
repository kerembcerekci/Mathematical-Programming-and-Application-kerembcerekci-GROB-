# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 18:07:22 2026

@author: kerem
"""

import pandas as pd
import gurobipy as gp
from gurobipy import GRB

# Veri

df = pd.read_csv(r'C:\Users\kerem\Desktop\emu414_assigment2_kerem_berkalp_çerekçi\forest_data.csv', sep='\t')


# Veriyi grobi'nin anlayacağı formata dönüştürme

ap_pairs, acres, net_value, timber, grazing, wilderness = gp.multidict({
    (int(row['analysis_area']), int(row['prescription'])): [
        row['acres'],
        row['net_value'],
        row['timber'],
        row['grazing'],
        row['wilderness_index']
    ]
    for _, row in df.iterrows()
})



# Her analiz bölgesinin toplam arazi büyüklüğünü hesaplama

areas = list(df['analysis_area'].unique())
total_acres = {a: df[df['analysis_area'] == a]['acres'].iloc[0] for a in areas}
prescriptions = list(df['prescription'].unique())
total_area = sum(total_acres.values())



# Gurobi modeli

model = gp.Model("Orman_Tahsisi")



# Karar değişkenleri: x[i,j] = i. analiz alanında j. acre

x = model.addVars(ap_pairs, name="x", lb=0)



# Amaç fonksiyonu: Max(toplam net değer) 

model.setObjective(gp.quicksum(net_value[i,j] * x[i,j] for i,j in ap_pairs), GRB.MAXIMIZE)



# Kısıtlar
# Her bölgedeki tüm reçetelere ayrılan arazi, o bölgenin toplam arazisine eşit olmalı

for a in areas:
    model.addConstr(
        gp.quicksum(x[a,j] for j in prescriptions if (a,j) in ap_pairs) == total_acres[a],
        name=f"alan_{a}_denge"
    )

# Kereste kısıtı: en az 40.000 

model.addConstr(gp.quicksum(timber[i,j] * x[i,j] for i,j in ap_pairs) >= 40000, name="kereste")

# Otlatma kısıtı: en az 5 

model.addConstr(gp.quicksum(grazing[i,j] * x[i,j] for i,j in ap_pairs) >= 5, name="otlatma")

# Doğa endeksi kısıtı: ağırlıklı ortalama en az 70 

model.addConstr(gp.quicksum(wilderness[i,j] * x[i,j] for i,j in ap_pairs) >= 70 * total_area, name="doga_endeksi")

# Modelin çözümü

model.optimize()


print("\n" + "="*60)
print("OPTİMAL ÇÖZÜM")
print("="*60)
if model.status == GRB.OPTIMAL:
    print(f"\nAmaç Fonksiyonu (Toplam Net Değer): {model.objVal:.2f}")
    print("\nKarar Değişkenleri:")
    print(f"{'Alan':<8} {'Reçete':<15} {'Arazi (acre)':>12}")
    print("-"*37)
    for i,j in ap_pairs:
        val = x[i,j].X
        if val > 0.001:
            print(f"{i:<8} {j:<15} {val:>12.2f}")
    timber_val = sum(timber[i,j]*x[i,j].X for i,j in ap_pairs)
    grazing_val = sum(grazing[i,j]*x[i,j].X for i,j in ap_pairs)
    wilderness_val = sum(wilderness[i,j]*x[i,j].X for i,j in ap_pairs) / total_area
    print(f"\nKereste:       {timber_val:.2f} (>= 40000)")
    print(f"Otlatma:       {grazing_val:.4f} (>= 5)")
    print(f"Doğa Endeksi:  {wilderness_val:.2f} (>= 70)")