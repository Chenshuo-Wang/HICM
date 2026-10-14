import numpy as np

# Let's inspect startup cycles in detail
f_sw = 1.536e6
T = 1.0 / f_sw
V_out1 = 8.32
V_sw_high = 8.70
V_sw_low = 0.05
V_D = 0.38
N = 6
C_fly = 10e-9
C_res = 10e-9
R_diode = 5.0
R_sw = 0.35 # internal switch Ron

V_res = np.zeros(N + 1)
V_res[0] = V_out1
V_fly = np.zeros(N + 1)

total_energy_dissipated_in_sw = 0.0
max_charge_per_cycle = 0.0

cycle_data = []

for cycle in range(800):
    # SW1 LOW:
    dq_low_total = 0.0
    for k in range(1, N + 1):
        v_avail = V_res[k-1] - (V_fly[k] + V_sw_low) - V_D
        if v_avail > 0:
            if k == 1:
                dq = v_avail * C_fly
                V_fly[k] += dq / C_fly
            else:
                c_eq = (C_res * C_fly) / (C_res + C_fly)
                dq = v_avail * c_eq
                V_res[k-1] -= dq / C_res
                V_fly[k] += dq / C_fly
            dq_low_total += dq
            
    # SW1 HIGH:
    dq_high_total = 0.0
    for k in range(1, N + 1):
        v_avail = (V_fly[k] + V_sw_high) - V_res[k] - V_D
        if v_avail > 0:
            c_eq = (C_res * C_fly) / (C_res + C_fly)
            dq = v_avail * c_eq
            V_fly[k] -= dq / C_fly
            V_res[k] += dq / C_res
            dq_high_total += dq
            
    max_charge_per_cycle = max(max_charge_per_cycle, dq_high_total)
    
    # Energy transferred from SW1 high:
    # E_sw = dq_high_total * V_sw_high
    # And when SW1 switches low, any remaining capacitance on SW1 is discharged into R_sw
    
    if cycle < 10 or cycle % 50 == 0:
        cycle_data.append((cycle, V_res[N], dq_low_total*1e9, dq_high_total*1e9))

print("Cycle | V_out (+56V) | Q_low (nC) | Q_high (nC)")
print("-" * 45)
for c, vo, ql, qh in cycle_data:
    print(f"{c:5d} | {vo:12.2f} V | {ql:10.3f} | {qh:10.3f}")

# Total charge pumped into the ladder:
# Final voltages on reservoir caps:
print("\nFinal voltages on stages:")
for k in range(1, N + 1):
    print(f"  Stage {k}: V_res[{k}] = {V_res[k]:.2f} V, V_fly[{k}] = {V_fly[k]:.2f} V")

# Total energy stored in all caps:
E_stored = 0.5 * sum(C_res * V_res[k]**2 + C_fly * V_fly[k]**2 for k in range(1, N + 1))
print(f"\nTotal electrostatic energy stored in ladder: {E_stored*1e3:.3f} mJ")
print(f"If charged in 400 us, average power during startup: {E_stored / 400e-6:.3f} W")
