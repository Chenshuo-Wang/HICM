import numpy as np

# Simulation parameters
f_sw = 1.536e6          # 1.536 MHz
T = 1.0 / f_sw          # ~651 ns
V_in = 5.0              # 5V USB
V_out1 = 8.32           # 8.32V boost output
D = 1.0 - (V_in / V_out1) # ~0.40
t_on = D * T
t_off = (1.0 - D) * T

L = 3.3e-6              # 3.3 uH
R_dson = 0.35           # internal switch Ron ~0.35 Ohm
V_diode_schottky = 0.35 # D2 and BAS70 Vf

# Charge pump components
N_stages = 6
C_fly = 10e-9           # 10 nF each (C41, C43, C48, C50, C53, C57)
C_res = 10e-9           # 10 nF each (C42, C47, C49, C51, C56, C60)
R_load = 1e9            # 1 Gohm load (capsule bias)

print(f"Switching freq: {f_sw/1e6:.3f} MHz, Period: {T*1e9:.1f} ns")
print(f"Duty cycle: {D:.3f}, t_on: {t_on*1e9:.1f} ns, t_off: {t_off*1e9:.1f} ns")
print(f"Number of stages: {N_stages}")
print(f"Flying caps: {N_stages} x {C_fly*1e9:.1f} nF = {N_stages*C_fly*1e9:.1f} nF total")

# Let's analyze charge transfer per cycle in steady state and startup
# In steady state:
# Output voltage target: V_target = V_out1 + N_stages * (V_out1 - 2*V_diode)
V_step = V_out1 - 2 * V_diode_schottky
V_ideal = V_out1 + N_stages * V_step
print(f"Ideal no-load output voltage: {V_ideal:.2f} V")

# But what about the source of energy?
# Energy taken from SW1:
# In each cycle, flying caps are charged when SW1=0V, and lifted when SW1=V_out1.
# When SW1 rises from 0V to V_out1:
# The current flows OUT of SW1 into the flying caps.
# When SW1 is pulled to 0V:
# The current flows INTO SW1 from the flying caps.
