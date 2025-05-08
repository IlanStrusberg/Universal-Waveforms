import argparse
import logging
import numpy as np
from waveform import UniversalWaveMode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate gravitational wave modes.")
    parser.add_argument("--nu", type=float, help="Symmetric mass ratio (0 < ν < 0.25)")
    parser.add_argument("--time", type=str, help="Time range as start, end, step")
    parser.add_argument("--plot", type=str, choices=["waveform", "phase", "amplitude", "all"], default="waveform",
                        help="Which plots to display")
    return parser.parse_args()


def get_user_nu() -> float:
    """Prompts the user for a valid symmetric mass ratio."""
    while True:
        try:
            nu = float(input("Write the symmetric mass ratio (0 < ν < 0.25): "))
            if nu >= 0.25:
                logging.warning("Too large. ν must be < 0.25")
            elif nu <= 1e-7:
                logging.warning("Too small. ν must be > 1e-7.")
            else:
                return nu
        except ValueError:
            logging.error("Invalid input. Please enter a number.")


def parse_time_string(time_str: str) -> np.ndarray | None:
    """Parses a time string like 'start,end,step' into a NumPy array."""
    try:
        start, end, step = map(float, time_str.split(","))
        if end < start:
            raise ValueError("End time must be greater than start time.")
        return np.arange(start, end, step)
    except Exception as e:
        logging.error(f"Invalid time format: {e}")
        return None


def get_time_interval() -> np.ndarray | None:
    """Prompts user for a custom time interval."""
    time_input = input("Enter time interval (start,end,step) or press Enter to skip: ")
    if not time_input:
        return None
    return parse_time_string(time_input)


def main() -> None:
    args = parse_args()

    # Handle symmetric mass ratio
    nu = args.nu if args.nu is not None else get_user_nu()

    # Handle time interval
    if args.time:
        time_array = parse_time_string(args.time)
        if time_array is None:
            logging.info("Falling back to interactive prompt for time.")
            time_array = get_time_interval()
    else:
        time_array = get_time_interval()

    try:
        if time_array is not None:
            mode = UniversalWaveMode(nu=nu, time_array=time_array)
        else:
            mode = UniversalWaveMode(nu=nu)
            logging.info(f"Using default time range. u_cut = {mode.u_cut(nu):.2f}")

        # Log summary of the mode
        logging.info(f"Waveform parameters: ν = {nu:.2e}, u_cut = {mode.u_cut_value:.2f}, l = {mode.l}, m = {mode.m}")

        # Plotting
        if args.plot in ["waveform", "all"]:
            mode.plot_waveform()
        if args.plot in ["phase", "all"]:
            mode.plot_phase()
        if args.plot in ["amplitude", "all"]:
            mode.plot_amplitude()

    except Exception as e:
        logging.error(f"Failed to generate waveform: {e}")


if __name__ == "__main__":
    main()
