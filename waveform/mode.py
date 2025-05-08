import matplotlib.pyplot as plt
import numpy as np
from time import time
import pickle
import os
import logging

logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more verbosity
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class UniversalWaveMode:
    """
       A class to compute and visualize universal gravitational waveforms consisting of an
       adiabatic and GUI (geodesic universal inspiral) parts.
    """

    def __init__(
            self,
            time_array: np.ndarray = np.arange(-3.e3, 100., 0.1),
            nu: float = 1.e-6,
            parity: str = 'e',
            l: float = 2,
            m: float = 2,
            polynomial_dir: str = "Polynomials"
    ):
        """
          Initialize the UniversalWaveMode instance and generate the waveform.
        :param time_array: Time array over which the waveform is computed.
        :param nu: Symmetric mass ratio, must be in (0, 0.25).
        :param parity: 'e' for even or 'o' for odd parity.
        :param l: Multipolar index l.
        :param m: Multipolar index m.
        :param polynomial_dir: Directory where polynomial files are stored.
        """
        if not (0 < nu < 0.25):
            raise ValueError("nu must be in (0, 0.25)")
        if parity not in {'e', 'o'}:
            raise ValueError("parity must be 'e' or 'o'")

        if min(time_array) < -2.5e2 / nu or max(time_array) > 100.:
            time_array = time_array[(time_array >= -2.5e2 / nu) & (time_array <= 100.)]
            logging.warning('Time is out of bounds! We made it shorter')

        self.time_array = time_array
        self.waveform = None
        self.phase = None
        self.amplitude = None
        self.nu = nu
        self.u_cut_value = self.u_cut(self.nu)
        self.parity = parity
        self.l = l
        self.m = m
        self.polynomial_dir = polynomial_dir

        self.generate_waveform()

    def generate_waveform(self) -> None:
        """Compute the waveform by stitching adiabatic and GUI parts."""
        start = time()

        adb_time_grid = self.time_array[self.time_array <= self.u_cut_value]
        gui_time_grid = self.time_array[self.time_array > self.u_cut_value]

        adiabatic = self._generate_adiabatic_part(adb_time_grid) if len(adb_time_grid) else None
        gui = self._generate_gui_part(gui_time_grid) if len(gui_time_grid) else None

        self._stitch_waveforms(adiabatic, gui)

        end = time()
        logging.info(f'It took {end - start:.2e} seconds to calculate the waveform')

    def _generate_adiabatic_part(self, time_grid):
        """Generate the adiabatic part of the waveform."""
        nu_scaled_time = self.nu * (time_grid - self.u_cut_value)

        phase_poly = self._load_polynomial("adb_phase_polynomial.pkl")
        amplitude_poly = self._load_polynomial("adb_amp_polynomial.pkl")

        phase = phase_poly(nu_scaled_time) * self.m / self.nu
        amplitude = amplitude_poly(nu_scaled_time)
        waveform = amplitude * np.exp(1.j * phase)

        return {"time": time_grid, "phase": phase, "amplitude": amplitude, "waveform": waveform}

    def _generate_gui_part(self, time_grid):
        """Generate the GUI (geodesic universal inspiral) part of the waveform."""
        phase_poly = self._load_polynomial("gui_phase_polynomial.pkl")
        amplitude_poly = self._load_polynomial("gui_amp_polynomial.pkl")

        phase = phase_poly(time_grid)
        amplitude = amplitude_poly(time_grid)
        waveform = amplitude * np.exp(1.j * phase)

        return {"time": time_grid, "phase": phase, "amplitude": amplitude, "waveform": waveform}

    def _stitch_waveforms(self, adiabatic, gui):
        """Combine adiabatic and GUI waveform segments into a complete waveform."""
        if adiabatic and gui:
            phase_shift = adiabatic["phase"][-1] - gui["phase"][0]
            adiabatic["phase"] -= phase_shift
            adiabatic["waveform"] *= np.exp(-1.j * phase_shift)

            self.phase = np.append(adiabatic["phase"], gui["phase"])
            self.amplitude = np.append(adiabatic["amplitude"], gui["amplitude"])
            self.waveform = np.append(adiabatic["waveform"], gui["waveform"])

        elif adiabatic:
            self.phase = adiabatic["phase"]
            self.amplitude = adiabatic["amplitude"]
            self.waveform = adiabatic["waveform"]

        elif gui:
            self.phase = gui["phase"]
            self.amplitude = gui["amplitude"]
            self.waveform = gui["waveform"]

        else:
            raise ValueError("Empty time grid — no waveform to generate.")

    def _load_polynomial(self, filename):
        """Load a polynomial from the given filename within the polynomial directory."""
        path = os.path.join(self.polynomial_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Polynomial file not found: {path}")
        with open(path, "rb") as f:
            return pickle.load(f)

    def plot_waveform(self) -> None:
        """Plot the real part of the waveform over time."""
        logging.info(
            f"Plotting waveform with ν = {self.nu:.2e}, u_cut = {self.u_cut_value:.2f}, l = {self.l}, m = {self.m} ")
        plt.plot(self.time_array[self.time_array > self.u_cut_value],
                 self.waveform.real[self.time_array > self.u_cut_value],
                 label='GUI Waveform')
        plt.plot(self.time_array[self.time_array < self.u_cut_value],
                 self.waveform.real[self.time_array < self.u_cut_value],
                 label='Adiabatic Waveform')
        plt.axvline(x=self.u_cut_value, color='black', linestyle='--', linewidth=2, label=r'$u_{cut}$')
        plt.xlabel(r'$u$')
        plt.ylabel(rf'$\Re\left(\psi_{{{self.l}{self.m}}}^{{({self.parity})}}\right)/\nu$')
        plt.grid(True)
        plt.legend(loc='lower left')
        plt.show()

    def plot_phase(self) -> None:
        """Plot the phase of the waveform over time."""
        plt.plot(self.time_array, self.phase)
        plt.xlabel(r'$u$')
        plt.ylabel(rf'$\phi_{{{self.l}{self.m}}}^{{({self.parity})}}$')
        plt.grid(True)
        plt.show()

    def plot_amplitude(self) -> None:
        """Plot the amplitude of the waveform over time."""
        plt.plot(self.time_array, self.amplitude)
        plt.xlabel(r'$u$')
        plt.ylabel(rf'$A_{{{self.l}{self.m}}}^{{({self.parity})}}/\nu$')
        plt.grid(True)
        plt.show()

    @staticmethod
    def u_cut(nu):
        """Return the u_cut value as a function of the symmetric mass ratio nu."""
        return -101.6 * (nu ** -0.2) + 108.8 - 65 * (nu ** 0.2)
