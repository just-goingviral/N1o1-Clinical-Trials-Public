
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import solve_ivp

# PARAMETERS
eGFR = 90.0
rbc_count = 4.5e6
dose_IR = 30.0
half_life = 0.5
t_peak = 0.5
baseline = 0.2
peak = 4.0
t_max = 6
points = 360

# FUNCTIONS
def renal_clearance_rate(egfr):
    return 0.1 * (egfr / 60.0)

def rbc_scavenging_rate(rbc_count):
    return 0.02 * (rbc_count / 1.0e6)

def dose_input(t, dose=30.0, t_IR=0.0):
    if t_IR <= t < (t_IR + 0.083):
        return (dose / 0.083)
    return 0.0

def no2_ode(t, y, k_clear, k_rbc):
    input_flux = dose_input(t, dose=dose_IR)
    dcdt = input_flux - (k_clear + k_rbc) * y[0]
    return [dcdt]

# SOLVE ODE
k_clear = renal_clearance_rate(eGFR)
k_rbc = rbc_scavenging_rate(rbc_count)
t_eval = np.linspace(0, t_max, points)
sol = solve_ivp(lambda t, y: no2_ode(t, y, k_clear, k_rbc), [0, t_max], [baseline], t_eval=t_eval)
plasma_no2 = sol.y[0]

# DERIVED OUTPUTS
def calculate_cgmp(no2_array):
    return 10 * (no2_array / max(no2_array))

def calculate_vasodilation(cgmp_array):
    return 100 + 50 * (cgmp_array / max(cgmp_array))

cgmp_levels = calculate_cgmp(plasma_no2)
vasodilation = calculate_vasodilation(cgmp_levels)

# ANIMATION
fig, ax = plt.subplots(figsize=(12, 6))
line_no2, = ax.plot([], [], lw=2, color='purple', label='Plasma NO₂⁻ (µM)')
line_cgmp, = ax.plot([], [], lw=2, color='green', linestyle='--', label='cGMP (a.u.)')
line_vaso, = ax.plot([], [], lw=2, color='blue', linestyle=':', label='Vasodilation (%)')

time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
conc_text = ax.text(0.02, 0.90, '', transform=ax.transAxes)

ax.set_xlim(0, t_max * 60)
ax.set_ylim(0, max(vasodilation) * 1.2)
ax.set_xlabel('Time (minutes)')
ax.set_ylabel('Response (relative units)')
ax.set_title('N1O1 Lozenge Simulation – Plasma NO₂⁻, cGMP, Vasodilation')
ax.grid(True)
ax.legend(loc='upper right')

x_data, no2_data, cgmp_data, vaso_data = [], [], [], []

def init():
    line_no2.set_data([], [])
    line_cgmp.set_data([], [])
    line_vaso.set_data([], [])
    time_text.set_text('')
    conc_text.set_text('')
    return line_no2, line_cgmp, line_vaso, time_text, conc_text

def update(frame):
    t_min = t_eval[frame] * 60
    no2 = plasma_no2[frame]
    cgmp = cgmp_levels[frame]
    vaso = vasodilation[frame]

    x_data.append(t_min)
    no2_data.append(no2)
    cgmp_data.append(cgmp)
    vaso_data.append(vaso)

    line_no2.set_data(x_data, no2_data)
    line_cgmp.set_data(x_data, cgmp_data)
    line_vaso.set_data(x_data, vaso_data)

    time_text.set_text(f"Time: {int(t_min)} min")
    conc_text.set_text(f"NO₂⁻: {no2:.2f} µM | cGMP: {cgmp:.1f} | Vasodilation: {vaso:.1f}%")
    return line_no2, line_cgmp, line_vaso, time_text, conc_text

ani = animation.FuncAnimation(fig, update, frames=len(t_eval),
                              init_func=init, blit=True, interval=1000/6)

plt.tight_layout()
plt.show()
