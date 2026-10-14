import numpy as np

f_sw = 1.536e6
T = 1.0 / f_sw
V_in = 5.0
V_out1 = 8.32
V_D_boost = 0.38
V_sw_high = V_out1 + V_D_boost # 8.70V
V_sw_low = 0.05               # NMOS drop ~0.05V

N = 6
C_fly = 10e-9
C_res = 10e-9
R_diode = 5.0 # series resistance of BAS70
V_D = 0.38    # forward voltage of BAS70
R_sw = 0.35   # ADP5070 internal NMOS Ron

# State variables:
# V_res[0] = V_out1 (constant regulated rail)
# V_res[1..6] (voltages across C42, C47, C49, C51, C56, C60)
# V_fly[1..6] (voltages across flying caps C41, C43, C48, C50, C53, C57: V_top - V_sw)

V_res = np.zeros(N + 1)
V_res[0] = V_out1
V_fly = np.zeros(N + 1)

# Let's simulate N_cycles
dt = 0.5e-9 # 0.5 ns time step
steps_per_cycle = int(T / dt)
steps_on = int(0.40 * steps_per_cycle)
steps_off = steps_per_cycle - steps_on

print(f"Time step: {dt*1e9:.2f} ns, Steps per cycle: {steps_per_cycle}")

# We will record:
# Energy delivered by SW1 per cycle: E_sw = integral(v_sw * i_sw dt)
# Energy dissipated in internal switch when pulling SW1 down

def run_simulation(n_cycles=5000):
    global V_res, V_fly
    V_res = np.zeros(N + 1)
    V_res[0] = V_out1
    V_fly = np.zeros(N + 1)
    
    cycle_history = []
    
    for cycle in range(n_cycles):
        # 1. Half-cycle: SW1 is LOW (NMOS ON)
        # v_sw = V_sw_low
        # C_fly[k] charges from C_res[k-1] through D_in[k]
        # In this phase, current flows from C_res[k-1] into C_fly[k], and from C_fly[k] into SW1!
        # Duration: t_on = ~260 ns.
        # Time constant tau ~ (R_diode) * (C_fly * C_res / (C_fly + C_res)) = 5 * 5nF = 25 ns.
        # 260 ns is > 10 tau, so charge completely equilibrates!
        # Let's compute charge transfer during SW1 LOW:
        q_low_sw = 0.0 # charge entering SW1
        for k in range(1, N + 1):
            # D_in[k] connects from V_res[k-1] to V_top[k] = V_fly[k] + V_sw_low
            v_avail = V_res[k-1] - (V_fly[k] + V_sw_low) - V_D
            if v_avail > 0:
                # Charge transfers between C_res[k-1] (if k>1) and C_fly[k]
                # If k=1, source is V_res[0] which is fixed at V_out1.
                if k == 1:
                    dq = v_avail * C_fly # since V_res[0] is stiff rail
                    V_fly[k] += dq / C_fly
                    q_low_sw += dq
                else:
                    # charge shared between C_res[k-1] and C_fly[k]
                    # delta_V = v_avail * (C_eff / C_fly), etc.
                    c_eq = (C_res * C_fly) / (C_res + C_fly)
                    dq = v_avail * c_eq
                    V_res[k-1] -= dq / C_res
                    V_fly[k] += dq / C_fly
                    q_low_sw += dq
        
        # 2. Half-cycle: SW1 is HIGH (NMOS OFF)
        # v_sw = V_sw_high
        # V_top[k] = V_fly[k] + V_sw_high
        # C_fly[k] discharges into C_res[k] through D_out[k]
        # Current flows OUT of SW1 into C_fly[k], through D_out[k], into C_res[k]!
        q_high_sw = 0.0 # charge leaving SW1
        for k in range(1, N + 1):
            v_avail = (V_fly[k] + V_sw_high) - V_res[k] - V_D
            if v_avail > 0:
                c_eq = (C_res * C_fly) / (C_res + C_fly)
                dq = v_avail * c_eq
                V_fly[k] -= dq / C_fly
                V_res[k] += dq / C_res
                q_high_sw += dq
        
        # Load discharge at stage N (1 Gohm load)
        # I_load = V_res[N] / 1e9
        V_res[N] -= (V_res[N] / 1e9) * T / C_res
        
        # Record every 100 cycles
        if cycle % 200 == 0 or cycle == n_cycles - 1:
            cycle_history.append((cycle, V_res[N], q_low_sw, q_high_sw))
            
    return cycle_history

history = run_simulation(5000)
print(f"Cycle 0: V_out = {history[0][1]:.2f} V")
print(f"Cycle 200: V_out = {history[1][1]:.2f} V, Q_sw = {history[1][3]*1e9:.3f} nC")
for h in history[2:10]:
    print(f"Cycle {h[0]}: V_out = {h[1]:.2f} V, Q_high_sw = {h[3]*1e9:.3f} nC")
print(f"Final Cycle {history[-1][0]}: V_out = {history[-1][1]:.2f} V, Q_high_sw = {history[-1][3]*1e12:.3f} pC")
