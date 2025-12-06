import os
import sys
import librosa
import numpy as np
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

FONTSIZE = 8
SR = 44100

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)

class AudioFeatureExtractor():
    def __init__(self, initial_data=None, sample_rate=SR, loadLabel=None):
        self.audio_data = initial_data if initial_data else np.array([0.0])
        self.sample_rate = sample_rate
        self.loadLabel = loadLabel

        # matplotlib for visuals
        self.waveform_canvas = MplCanvas(self, width=8, height=2)
        self.spectral_canvas = MplCanvas(self, width=8, height=2)
        self.zcr_canvas = MplCanvas(self, width=8, height=2)

        self.setup_plots()

    def load_audio(self, filename):
        if filename:
            try:
                if self.loadLabel:
                    self.loadLabel.setText(f'Loading: {filename.split("/")[-1]}...')
                self.audio_data, self.sample_rate = librosa.load(filename, sr=None)
                if self.loadLabel:
                    self.loadLabel.setText(f'Loaded: {filename.split("/")[-1]} (SR: {self.sample_rate} Hz)')
                self.extract_and_visualize()
            except Exception as e:
                if self.loadLabel:
                    self.loadLabel.setText(f'Error: {str(e)}')
                print(f'Error: {str(e)}')

    def setup_plots(self):
        # Waveform
        ax = self.waveform_canvas.fig.add_subplot(111)
        self.waveform_ax = ax
        self.waveform_line, = ax.plot([0],[0], linewidth=0.5, alpha=0.7, color='blue')
        ax.set_xlabel('Time (s)', fontsize=FONTSIZE)
        ax.set_ylabel('Volume', fontsize=FONTSIZE)
        ax.set_title('Volume over Time', fontsize=FONTSIZE)
        ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
        ax.grid(True, alpha=0.3)
        self.waveform_canvas.fig.tight_layout()

        # Brightness
        ax = self.spectral_canvas.fig.add_subplot(111)
        ax2 = ax.twinx()
        self.spectral_ax = ax2
        self.spectral_line, = ax2.plot([0], [0], color='red', linewidth=2, label='Spectral Centroid')
        ax2.set_ylabel('Frequency (Hz)', color='red', fontsize=FONTSIZE)
        ax2.tick_params(axis='y', labelcolor='red', labelsize=FONTSIZE)
        ax.set_xlabel('Time (s)', fontsize=FONTSIZE)
        ax.set_ylabel('Brightness', fontsize=FONTSIZE)
        ax.set_title('Brightness over Time', fontsize=FONTSIZE)
        ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
        ax.grid(True, alpha=0.3)
        self.spectral_canvas.fig.tight_layout()

        # Percussion
        ax = self.zcr_canvas.fig.add_subplot(111)
        self.zcr_ax = ax
        self.zcr_line, = ax.plot([0], [0], color='green', linewidth=2)
        ax.set_xlabel('Time (s)', fontsize=FONTSIZE)
        ax.set_ylabel('Percussion', fontsize=FONTSIZE)
        ax.set_title('Percussion over Time', fontsize=FONTSIZE)
        ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
        ax.grid(True, alpha=0.3)
        self.zcr_canvas.fig.tight_layout()
    
    def update_audio_data(self, data, sr=SR):
        self.audio_data = np.append(self.audio_data, data)
        self.sample_rate = sr

    def reset_audio_data(self):
        self.audio_data = np.array([0.0])

    def extract_and_visualize(self):
        if self.audio_data is None:
            return
        y = self.audio_data
        sr = self.sample_rate
        # 1. Waveform - Volume
        self.plot_waveform(y, sr)
        # 2. Spectral Centroid - Brightness
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        self.plot_spectral_centroid(spectral_centroids, sr)
        # 3. Zero Crossing Rate - Percussion/Beats
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        self.plot_zcr(zcr, sr)

    def plot_waveform(self, y, sr):
        times = np.arange(len(y)) / sr
        # self.waveform_ax.plot(times, y, linewidth=0.5, alpha=0.7, color='blue')
        self.waveform_line.set_data(times, y)
        self.waveform_ax.set_xlim(min(times), max(times))
        self.waveform_ax.set_ylim(min(y), max(y))
        self.waveform_canvas.draw()

    def plot_spectral_centroid(self, spectral_centroids, sr):
        
        frames = range(len(spectral_centroids))
        t = librosa.frames_to_time(frames, sr=sr)
        self.spectral_line.set_data(t, spectral_centroids)
        self.spectral_ax.set_xlim(min(t), max(t))
        self.spectral_ax.set_ylim(min(spectral_centroids), max(spectral_centroids))
        self.spectral_canvas.draw()

    def plot_zcr(self, zcr, sr):
        
        frames = range(len(zcr))
        t = librosa.frames_to_time(frames, sr=sr)
        self.zcr_line.set_data(t, zcr)
        self.zcr_ax.set_xlim(min(t), max(t))
        self.zcr_ax.set_ylim(min(zcr), max(zcr))
        self.zcr_canvas.draw()


if __name__ == "__main__":
    # Create test window
    app = QApplication(sys.argv)

    # get sample audio file
    audio_file = None
    folder_path = "./audio_files"
    for filename in os.listdir(folder_path):
        for type in [".wav", ".mp3", ".flac", ".ogg", ".m4a"]:
            if type in filename:
                print(f"Using file '{filename}'")
                audio_file = os.path.join(folder_path, filename)
                break
        if audio_file:
            break
    if not audio_file:
        raise RuntimeError("No audio file found")
    

    extractor = AudioFeatureExtractor()
    extractor.load_audio(audio_file)
    extractor.extract_and_visualize()
    
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(extractor.waveform_canvas)
    layout.addWidget(extractor.spectral_canvas)
    layout.addWidget(extractor.zcr_canvas)
    window.show()
    
    sys.exit(app.exec())



