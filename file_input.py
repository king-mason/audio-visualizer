import sys
import librosa
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                              QWidget, QPushButton, QFileDialog, QLabel, QGroupBox)
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

FONTSIZE = 8

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)

class AudioFeatureExtractor():
    def __init__(self, loadLabel=None):
        self.audio_data = None
        self.sample_rate = None
        self.loadLabel = loadLabel

        # matplotlib for visuals
        self.waveform_canvas = MplCanvas(self, width=8, height=2)
        self.spectral_canvas = MplCanvas(self, width=8, height=2)
        self.zcr_canvas = MplCanvas(self, width=8, height=2)

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
        self.waveform_canvas.fig.clear()
        ax = self.waveform_canvas.fig.add_subplot(111)
        times = np.arange(len(y)) / sr
        ax.plot(times, y, linewidth=0.5, alpha=0.7, color='blue')
        ax.set_xlabel('Time (s)', fontsize=FONTSIZE)
        ax.set_ylabel('Volume', fontsize=FONTSIZE)
        ax.set_title('Volume over Time', fontsize=FONTSIZE)
        ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
        ax.grid(True, alpha=0.3)
        self.waveform_canvas.fig.tight_layout()
        self.waveform_canvas.draw()

    def plot_spectral_centroid(self, spectral_centroids, sr):
        self.spectral_canvas.fig.clear()
        ax = self.spectral_canvas.fig.add_subplot(111)
        frames = range(len(spectral_centroids))
        t = librosa.frames_to_time(frames, sr=sr)
        ax2 = ax.twinx()
        ax2.plot(t, spectral_centroids, color='red', linewidth=2, label='Spectral Centroid')
        ax2.set_ylabel('Frequency (Hz)', color='red', fontsize=FONTSIZE)
        ax2.tick_params(axis='y', labelcolor='red', labelsize=FONTSIZE)
        ax.set_xlabel('Time (s)', fontsize=FONTSIZE)
        ax.set_ylabel('Brightness', fontsize=FONTSIZE)
        ax.set_title('Brightness over Time', fontsize=FONTSIZE)
        ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
        ax.grid(True, alpha=0.3)
        self.spectral_canvas.fig.tight_layout()
        self.spectral_canvas.draw()

    def plot_zcr(self, zcr, sr):
        self.zcr_canvas.fig.clear()
        ax = self.zcr_canvas.fig.add_subplot(111)
        frames = range(len(zcr))
        t = librosa.frames_to_time(frames, sr=sr)
        ax.plot(t, zcr, color='green', linewidth=2)
        ax.set_xlabel('Time (s)', fontsize=FONTSIZE)
        ax.set_ylabel('Percussion', fontsize=FONTSIZE)
        ax.set_title('Percussion over Time', fontsize=FONTSIZE)
        ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
        ax.grid(True, alpha=0.3)
        self.zcr_canvas.fig.tight_layout()
        self.zcr_canvas.draw()


if __name__ == "__main__":
    # Create test window
    app = QApplication(sys.argv)
    
    extractor = AudioFeatureExtractor()
    extractor.load_audio("SampleAudio.wav")
    extractor.extract_and_visualize()
    
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(extractor.waveform_canvas)
    layout.addWidget(extractor.spectral_canvas)
    layout.addWidget(extractor.zcr_canvas)
    window.show()
    
    sys.exit(app.exec())

    
    
