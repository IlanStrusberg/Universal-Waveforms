import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
from time import time
import pickle


class UniversalWaveMode:
    def __init__(self, time: np.ndarray = np.arange(-3.e3, 100., 0.1), nu: float = 1.e-6, parity: str = 'e',
                 l: float = 2,
                 m: float = 2):
        if min(time) < -2.5e2 / nu or max(time) > 100.:
            time = time[(time >= -2.5e2 / nu) & (time <= 100.)]
            print('Time is out of bounds! We made it shorter')
        self.time = time  # time
        self.waveform = None  # waveform
        self.phase = None  # phase
        self.amplitude = None  # amplitude
        self.nu = nu  # symmetric mass ratio
        self.parity = parity  # parity
        self.l = l  # first multipolar index
        self.m = m  # second multipolar index
        self.generate_waveform()

    def generate_waveform(self) -> None:
        """
        Generates the full waveform of the mode.
        """
        start = time()
        # Calculated u_cut
        u_cut = self.u_cut(self.nu)
        adb_time_grid = self.time[self.time < u_cut]
        gui_time_grid = self.time[self.time > u_cut]
        if len(gui_time_grid) != 0:
            # Generate gui phase array
            with open("Data/Polynomials/gui_phase_polynomial.pkl", "rb") as f:
                gui_phase_polynomial = pickle.load(f)
            gui_phase = gui_phase_polynomial(gui_time_grid)

            with open("Data/Polynomials/gui_amp_polynomial.pkl", "rb") as f:
                gui_amp_polynomial = pickle.load(f)
            gui_amplitude = gui_amp_polynomial(gui_time_grid)

            # Generate the adiabatic waveform
            gui_waveform = gui_amplitude * np.exp(1.j * gui_phase)

        if len(adb_time_grid) != 0:
            # Generate adiabatic phase array
            with open("Data/Polynomials/adb_phase_polynomial.pkl", "rb") as f:
                adb_phase_polynomial = pickle.load(f)
            adiabatic_phase = adb_phase_polynomial(nu * adb_time_grid)

            adiabatic_phase *= self.m / self.nu

            # Generate adiabatic amplitude array
            with open("Data/Polynomials/adb_amp_polynomial.pkl", "rb") as f:
                adb_amp_polynomial = pickle.load(f)
            adiabatic_amplitude = adb_amp_polynomial(nu * adb_time_grid)

            # Generate the adiabatic waveform
            adiabatic_waveform = adiabatic_amplitude * np.exp(1.j * adiabatic_phase)

            if len(gui_time_grid) == 0:
                # Generate full waveform
                self.phase = adiabatic_phase
                self.amplitude = adiabatic_amplitude
                self.waveform = adiabatic_waveform
            else:
                adiabatic_waveform *= np.exp(-1.j * (adiabatic_phase[-1] - gui_phase[0]))
                adiabatic_phase -= adiabatic_phase[-1] - gui_phase[0]

                # Generate full waveform
                self.phase = np.append(adiabatic_phase, gui_phase)
                self.amplitude = np.append(adiabatic_amplitude, gui_amplitude)
                self.waveform = np.append(adiabatic_waveform, gui_waveform)

        else:
            # Generate full waveform
            self.phase = gui_phase
            self.amplitude = gui_amplitude
            self.waveform = gui_waveform
        end = time()
        print(f'It took {format(end - start, ".2e")} seconds to calculate the waveform')

    def plot_waveform(self) -> None:
        """
        Plots the waveform with respect to the retarded time.
        """
        u = self.u_cut(self.nu)
        print(f"Plotting waveform with nu = {self.nu}")
        plt.plot(self.time[self.time < u], self.waveform.real[self.time < u], label='Adiabatic Waveform')
        plt.plot(self.time[self.time > u], self.waveform.real[self.time > u], label='GUI Waveform')
        # plt.plot(self.time, self.waveform.imag, label='Imag')
        plt.axvline(x=self.u_cut(self.nu), color='black', linestyle='--', linewidth=2, label=r'$u_{cut}$')
        plt.xlabel(r'$u$')
        plt.ylabel(rf'$\Re\left(\psi_{{{self.l}{self.m}}}^{{({self.parity})}}\right)/\nu$')
        plt.grid(True)
        plt.legend(loc='lower left')
        plt.show()

    def plot_phase(self) -> None:
        """
        plots the phase with respect to the retarded time.
        :return:
        """
        plt.plot(self.time, self.phase)
        plt.xlabel(r'$u$')
        plt.ylabel(rf'$\phi_{{{self.l}{self.m}}}^{{({self.parity})}}$')
        plt.grid(True)
        plt.show()

    def plot_amplitude(self) -> None:
        """
        plots the amplitude with respect to the retarded time.
        :return:
        """
        plt.plot(self.time, self.amplitude)
        plt.xlabel(r'$u$')
        plt.ylabel(rf'$A_{{{self.l}{self.m}}}^{{({self.parity})}}/\nu$')
        plt.grid(True)
        plt.show()

    @staticmethod
    def u_cut(nu):
        """
        Calculates the cutting retarded time of the GUI wave from merger.
        :param nu: symmetric mass ratio.
        :return: the cutting retarded time of the GUI wave.
        """
        return -101.6 * (nu ** -0.2) + 108.8 - 65 * (nu ** 0.2)


if __name__ == '__main__':
    nu = float(input("Write the symmetric mass ratio: "))
    while nu > 1:
        nu = float(input("Too large. Write a symmetric mass ratio lower than 1:"))
    while nu < 1.e-7:
        nu = float(input("Too small. Write a symmetric mass ratio higher than 1E-7:"))

    time_input = input("Enter the time interval (start,end,step) or press Enter to skip: ")
    time_interval = None
    if time_input:
        try:
            start, end, step = map(float, time_input.split(","))

            if end < start:
                raise ValueError("The end of the time interval can't be lower than the start!")

            time_interval = np.arange(start, end, step)

        except ValueError as e:
            print(e)  # This will print the error message from the raised exception
            print("Invalid time interval format. Please enter two numbers separated by a comma.")

    if time_interval is not None:
        dominant_mode = UniversalWaveMode(nu=nu, time=time_interval)
    else:
        dominant_mode = UniversalWaveMode(nu=nu)
        print(f'u cut is: {dominant_mode.u_cut(nu)}')
    # Plot the waveform
    dominant_mode.plot_waveform()
    dominant_mode.plot_phase()
    dominant_mode.plot_amplitude()
