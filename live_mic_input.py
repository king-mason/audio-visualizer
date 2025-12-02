# sounddevice docs: https://python-sounddevice.readthedocs.io/en/0.5.3/

import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def record_mic_input(duration, fs):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return recording

def plot_signal(signal):
    plt.rcParams.update({'font.size': 20})
    plt.figure(figsize=(12, 6))
    # design element implementation 
    x = np.arange(len(signal))
    colors = (signal.flatten() - signal.min()) / (signal.max() - signal.min())
    
    #making a more colorful gradient with faint lines behind 
    plt.scatter(x, signal, c=colors, cmap='plasma', s=1)  # colorful gradient
    plt.plot(signal, alpha=0.3, color="black")  # faint line behind points
    
    
    plt.title("Signal Visualization")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    
    #Adding an animation element 
    def animate_signal(signal):
        fig, ax = plt.subplots(figsize=(12, 6))
        line, = ax.plot([], [], lw=2)
        ax.set_xlim(0, len(signal))
        ax.set_ylim(signal.min(), signal.max())
        ax.set_title("Dynamic Audio Waveform")
        ax.set_xlabel("Sample Index")
        ax.set_ylabel("Amplitude")

    def update(frame):
        # Growing window slice
        line.set_data(np.arange(frame), signal[:frame])
        line.set_color(plt.cm.viridis(frame / len(signal)))
        return line,

    ani = animation.FuncAnimation(fig, update, frames=len(signal),
                                  interval=5, blit=True)
    plt.show()

def main():
    sample_rate = 44100  # samples per second
    length_seconds = 5  # duration in seconds

    recording = record_mic_input(length_seconds, sample_rate)

    plot_signal(recording)
    animate_signal(recording.flatten())

if __name__ == '__main__':
    main()

