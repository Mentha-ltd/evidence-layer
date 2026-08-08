from mentha.spectra.loaders import load_spectrum
from matplotlib import pyplot as plt
import numpy as np

# 2 THE CONSTANTS
CYCLES=[0, 45,90,116,135,180,204]

# 3 FUNCTIONS DEFINITION

def plot_nyquist(path, cell_id):
    spectrum =load_spectrum(path, cell_id)
    plt.plot(spectrum.z_real_ohm, -spectrum.z_imag_ohm, "o-")
    plt.gca().set_aspect("equal")
    plt.xlabel("Z' (ohm)")
    plt.ylabel("-Z'' (ohm)")
    plt.savefig("figures/nyquist_lipo_1_cycle90.png", dpi=150)
    plt.close()

def plot_ageing(path_new, path_old, cell_id):
    new = load_spectrum(path_new, cell_id)
    old = load_spectrum(path_old, cell_id)
    plt.plot(new.z_real_ohm, -new.z_imag_ohm, "o-", label="cycle 0")
    plt.plot(old.z_real_ohm, -old.z_imag_ohm, "s-", label="cycle 204")
    # second plot call for old, with its own label
    plt.legend()
    plt.gca().set_aspect("equal")
    plt.xlabel("Z' (ohm)")
    plt.ylabel("-Z'' (ohm)")
    plt.title(f"{cell_id} — ageing at 100% SoC")
    plt.savefig("figures/ageing_lipo1.png", dpi=150)
    plt.close()

def plot_ageing_series(cell_dir,cell_id):
    capacity=np.loadtxt(f'{cell_dir}/Capacity/Capacity_std.csv')
    initial=capacity[0,1]

    for cycle in CYCLES:
        path=f'{cell_dir}/EIS_Charge_discharge/EIS_{cycle}/0_EIS.csv'
        spectrum = load_spectrum(path, cell_id)

        # find the cycles capacity in array and calculate the soh as percentage of initial
        soh = capacity[capacity[:,0]==cycle, 1][0] / initial * 100
        # then one plt.plot call with label=f'cycle {cycle} -{soh:.1f}% SOH
        
        plt.plot(spectrum.z_real_ohm, -spectrum.z_imag_ohm, "o-", label=f"cycle {cycle} - {soh:.1f}% SOH")
    plt.legend(fontsize=8, loc="upper left",bbox_to_anchor=(1.02,1), borderaxespad=0)
    plt.tight_layout()
    plt.gca().set_aspect('equal')
    plt.xlabel('Z\' (ohm)')
    plt.ylabel("-Z'' (ohm)")
    plt.title(f'{cell_id}- impedance vs state of health, 100% Soc')
    plt.savefig("figures/ageing_series_lipo1.png", dpi=150)
    plt.close()
    
def print_r0_series(cell_dir, cell_id):
        capacity = np.loadtxt(f"{cell_dir}/Capacity/Capacity_std.csv")
        initial = capacity[0, 1]
        for cycle in CYCLES:
            s = load_spectrum(f"{cell_dir}/EIS_Charge_discharge/EIS_{cycle}/0_EIS.csv", cell_id)
            soh = capacity[capacity[:, 0] == cycle, 1][0] / initial * 100
            print(f"cycle {cycle:4d}  SoH {soh:5.1f}%  "
              f"Zreal first {s.z_real_ohm[0]:.4f}  last {s.z_real_ohm[-1]:.4f}  "
              f"n={len(s)}")

if __name__ == "__main__":
    plot_nyquist(
        "data/raw/galeotti2023/LiPO_1/EIS_Charge_discharge/EIS_90/6_EIS.csv",
        cell_id="LiPO_1",
    )
    plot_ageing(
        "data/raw/galeotti2023/LiPO_1/EIS_Charge_discharge/EIS_0/0_EIS.csv",
        "data/raw/galeotti2023/LiPO_1/EIS_Charge_discharge/EIS_204/0_EIS.csv",
        cell_id="LiPO_1",
    )
    plot_ageing_series(
        "data/raw/galeotti2023/LiPO_1",
        cell_id="LiPO_1",
    )
    print_r0_series(
        "data/raw/galeotti2023/LiPO_1",
        cell_id="LiPO_1",
    )
