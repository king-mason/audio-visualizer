# audio-visualizer
import numpy as np
import matplotlib.pyplot as plt

def plot_signal(signal):
    plt.rcParams.update({'font.size': 20})
    plt.figure(figsize=(12, 6))
    plt.plot(signal)
    plt.title("Signal Visualization")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()

def main():
    frequency = 440  # Hz (A4 note)
    sample_rate = 44100  # samples per second
    length_seconds = 5  # duration in seconds

    time = np.arange(length_seconds * sample_rate) / sample_rate
    sine = np.sin(2 * np.pi * frequency * time)

    # Plot the first 1000 samples for clarity
    plot_signal(sine[:1000])

if __name__ == '__main__':
    main()


