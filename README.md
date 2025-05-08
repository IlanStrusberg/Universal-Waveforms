# Gravitational Waveform Generator

This Python tool computes and plots the dominant mode of the gravitational waveforms using adiabatic and GUI parts. It allows users to generate gravitational waveforms based on the symmetric mass ratio (ν) and a custom time range. The generated waveforms can be plotted as amplitude, phase, or the full waveform.

## Requirements

Ensure you have the required dependencies installed:

- Python
- NumPy
- Matplotlib
- pytest (for testing)

You can install the required dependencies with the following command:

```bash
pip install -r requirements.txt
```

## Usage

To generate a gravitational waveform and plot it, use the following command:

```bash
python main.py --nu 0.01 --time "-1000,100,0.5"
```

## Testing

To run the tests for this project, make sure you have `pytest` installed and the environment variable `PYTHONPATH` set correctly. You can run tests with the following command:

```bash
pytest tests/test_waveform.py
```