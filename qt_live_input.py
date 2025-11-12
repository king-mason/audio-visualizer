import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.uic import loadUi
import pyqtgraph as pg

fs = 44100
chunk = 1024
class AudioVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Sound Visualizer")

        # Load UI
        loadUi("main_window.ui", self)
        
        # Set the row stretch factors
        # self.gridLayout.setRowStretch(0, 1)
        # self.gridLayout.setRowStretch(1, 1)

        self.startButton.clicked.connect(self.on_click)
        self.stopButton.clicked.connect(self.on_click_b)
        
        # Setup plot
        self.plot_widget = pg.PlotWidget()
        # self.gridLayout.addWidget(self.plot_widget, 0, 0)  # Add to the first row (0), first column (0)
        # self.display_widget.deleteLater()  # Remove the placeholder display widget
        self.init_plot()

        self.timer = QTimer()
        

    def init_plot(self):
        self.plot_widget.setYRange(-0.5, 0.5)
        self.plot_widget.setXRange(0, chunk)
        # Disable mouse interactions
        self.plot_widget.setMouseEnabled(x=False, y=False)  # Disable mouse panning
        self.plot_widget.getViewBox().setMenuEnabled(False)  # Disable right-click menu
        self.plot_widget.hideButtons()  # Hide auto-scale button
        
        self.plot = self.plot_widget.plot(pen='y')
        self.data = np.zeros(chunk)

        self.gridLayout.addWidget(self.plot_widget, 0, 0)

    def start_audio_stream(self):
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)

        # Start audio stream
        self.stream = sd.InputStream(channels=1, samplerate=fs, blocksize=chunk, callback=self.audio_callback)
        self.stream.start()

    def on_click(self):
        print("Button clicked!")
        # self.setCentralWidget(self.plot_widget)
        self.start_audio_stream()

    def on_click_b(self):
        # self.setCentralWidget(self.gridLayoutWidget)
        self.stream.stop()

    def keyPressEvent(self, event):
        pass

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