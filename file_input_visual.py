import sys
import librosa
import librosa.display
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                              QWidget, QPushButton, QFileDialog, QLabel, QGroupBox)
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)

class AudioFeatureExtractor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_data = None
        self.sample_rate = None
        self.filename = None
        self.init_ui()

    def init_ui(self):
        # qt canvas
        self.setWindowTitle('Audio File Input')
        self.setGeometry(100, 100, 1200, 900)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        control_layout = QHBoxLayout()
        self.load_btn = QPushButton('Load Audio File')
        self.load_btn.clicked.connect(self.load_audio)
        control_layout.addWidget(self.load_btn)
        self.file_label = QLabel('No file loaded')
        control_layout.addWidget(self.file_label)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # matplotlib for visuals
        self.waveform_canvas = MplCanvas(self, width=8, height=2)
        main_layout.addWidget(QLabel('Volume:'))
        main_layout.addWidget(self.waveform_canvas)
        self.spectral_canvas = MplCanvas(self, width=8, height=2)
        main_layout.addWidget(QLabel('Brightness:'))
        main_layout.addWidget(self.spectral_canvas)
        self.zcr_canvas = MplCanvas(self, width=8, height=2)
        main_layout.addWidget(QLabel('Percussion/Beats:'))
        main_layout.addWidget(self.zcr_canvas)

        self.show()

    def load_audio(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a);;All Files (*)")
        if filename:
            try:
                self.filename = filename
                self.file_label.setText(f'Loading: {filename.split("/")[-1]}...')
                QApplication.processEvents()  # update
                self.audio_data, self.sample_rate = librosa.load(filename, sr=None)
                self.file_label.setText(f'Loaded: {filename.split("/")[-1]} (SR: {self.sample_rate} Hz)')
                self.extract_and_visualize()
            except Exception as e:
                self.file_label.setText(f'Error: {str(e)}')

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
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Volume')
        ax.set_title('Volume over Time')
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
        ax2.set_ylabel('Frequency (Hz)', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Brightness')
        ax.set_title('Brightness over Time')
        ax.grid(True, alpha=0.3)
        self.spectral_canvas.fig.tight_layout()
        self.spectral_canvas.draw()

    def plot_zcr(self, zcr, sr):
        self.zcr_canvas.fig.clear()
        ax = self.zcr_canvas.fig.add_subplot(111)
        frames = range(len(zcr))
        t = librosa.frames_to_time(frames, sr=sr)
        ax.plot(t, zcr, color='green', linewidth=2)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Percussion')
        ax.set_title('Percussion over Time')
        ax.grid(True, alpha=0.3)
        self.zcr_canvas.fig.tight_layout()
        self.zcr_canvas.draw()

def main():
    app = QApplication(sys.argv)
    window = AudioFeatureExtractor()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()