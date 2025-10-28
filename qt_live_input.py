import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.uic import loadUi
import pyqtgraph as pg

fs = 44100
chunk = 1024
class AudioVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Sound Visualizer")

        # self.button = QPushButton("Click here", self)
        # self.button.setStyleSheet("font-size: 30px;")
        # self.button.setGeometry(150, 200, 200, 100)
        # self.button.clicked.connect(self.on_click)
        
        # Setup plot
        self.plot_widget = pg.PlotWidget()
        self.init_plot()

        self.timer = QTimer()
        self.start_timer()

        # Load UI
        # loadUi("mainui.ui", self)

    def init_plot(self):
        self.plot_widget.setYRange(-0.5, 0.5)
        self.plot_widget.setXRange(0, chunk)
        self.setCentralWidget(self.plot_widget)
        self.plot = self.plot_widget.plot(pen='y')
        self.data = np.zeros(chunk)

    def start_timer(self):
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)

        # Start audio stream
        self.stream = sd.InputStream(channels=1, samplerate=fs, blocksize=chunk, callback=self.audio_callback)
        self.stream.start()

    def on_click(self):
        print("Button clicked!")

    def audio_callback(self, indata, frames, time, status):
        self.data = np.squeeze(indata)

    def update_plot(self):
        self.plot.setData(self.data)

def main():
    app = QApplication(sys.argv)
    window = AudioVisualizer()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()