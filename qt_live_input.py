import sys
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer, QFile, QTextStream
from PyQt6.uic import loadUi
import pyqtgraph as pg

# TODO:
# 1. organize setup and update functions
# 2. organize sensitivity in functions
# 3. add any more buttons

# Audio configuration
FS = 44100
CHUNK = 2048
UPDATE_INTERVAL = 20

class VisualizationManager:
    """Manages different visualization types and their rendering"""
    
    def __init__(self, plot_widget, chunk_size):
        self.plot_widget = plot_widget
        self.chunk_size = chunk_size
        self.visualizations = {}
        self.current_viz = None
        
    def setup(self, viz_type):
        """Setup visualization based on type"""
        # Clear other setups
        self.plot_widget.clear()
        self.visualizations.clear()
        self.plot_widget.setAspectLocked(False)
        
        viz_configs = {
            "Frequency Bars": self._setup_freq_bars,
            "Waveform": self._setup_waveform,
            "Spectrum Line": self._setup_spectrum_line,
            "Circular Spectrum": self._setup_circular,
            "Stereo Bars": self._setup_stereo_bars
        }
        
        if viz_type in viz_configs:
            viz_configs[viz_type]()
            self.current_viz = viz_type
    
    def _setup_freq_bars(self):
        self.visualizations['freq_bars'] = pg.BarGraphItem(
            x=np.arange(self.chunk_size // 2),
            height=np.zeros(self.chunk_size // 2),
            width=0.8, brush='#00d4ff'
        )
        self.plot_widget.addItem(self.visualizations['freq_bars'])
        self.plot_widget.setYRange(0, 1)
        self.plot_widget.setXRange(0, self.chunk_size // 2)
    
    def _setup_waveform(self):
        self.visualizations['waveform'] = self.plot_widget.plot(
            pen=pg.mkPen('#00ff88', width=2)
        )
        self.plot_widget.setYRange(-1, 1)
        self.plot_widget.setXRange(0, self.chunk_size)
    
    def _setup_spectrum_line(self):
        self.visualizations['spectrum'] = self.plot_widget.plot(
            pen=pg.mkPen('#ff00ff', width=3),
            fillLevel=0, brush=(255, 0, 255, 100)
        )
        self.plot_widget.setYRange(0, 1)
        self.plot_widget.setXRange(0, self.chunk_size // 2)
    
    def _setup_circular(self):
        self.visualizations['circular'] = self.plot_widget.plot(
            pen=pg.mkPen('#ff00ff', width=3)
        )
        self.plot_widget.setYRange(-1.5, 1.5)
        self.plot_widget.setXRange(-1.5, 1.5)
        self.plot_widget.setAspectLocked(True)
    
    def _setup_stereo_bars(self):
        self.visualizations['stereo_top'] = pg.BarGraphItem(
            x=np.arange(self.chunk_size // 4),
            height=np.zeros(self.chunk_size // 4),
            width=0.8, brush='#00d4ff'
        )
        self.visualizations['stereo_bottom'] = pg.BarGraphItem(
            x=np.arange(self.chunk_size // 4),
            height=np.zeros(self.chunk_size // 4),
            width=0.8, brush='#ff00ff'
        )
        self.plot_widget.addItem(self.visualizations['stereo_top'])
        self.plot_widget.addItem(self.visualizations['stereo_bottom'])
        self.plot_widget.setYRange(-1, 1)
        self.plot_widget.setXRange(0, self.chunk_size // 4)
    
    def update(self, data):
        """Update visualization with new audio data"""
        update_methods = {
            "Frequency Bars": self._update_freq_bars,
            "Waveform": self._update_waveform,
            "Spectrum Line": self._update_spectrum_line,
            "Circular Spectrum": self._update_circular,
            "Stereo Bars": self._update_stereo_bars
        }
        
        if self.current_viz in update_methods:
            update_methods[self.current_viz](data)
    
    def _compute_fft(self, data): # delete?
        """Compute FFT with Hamming window"""
        windowed = data * np.hamming(len(data))
        return np.fft.rfft(windowed)
    
    def _create_spectrum(self, data, max_values):
        windowed = data * np.hamming(len(data))
        fft = np.fft.rfft(windowed)
        spectrum = np.abs(fft[:max_values]) / self.chunk_size
        return np.clip(spectrum, 0, 1)
    
    def _update_freq_bars(self, data):
        spectrum = self._create_spectrum(data, self.chunk_size // 2)
        
        # Smooth bars by reducing maximum change
        bars = self.visualizations['freq_bars']
        current = bars.opts['height']
        spectrum = np.maximum(spectrum, current * 0.7)
        bars.setOpts(height=spectrum)
    
    def _update_waveform(self, data):
        self.visualizations['waveform'].setData(data)
    
    def _update_spectrum_line(self, data):
        spectrum = self._create_spectrum(data, self.chunk_size // 2)
        self.visualizations['spectrum'].setData(spectrum)
    
    def _update_circular(self, data):
        spectrum = self._create_spectrum(data, 180)
        
        # Using NumPy broadcasting
        angles = np.linspace(0, 2 * np.pi, 180)
        radius = 0.5 + spectrum
        x = np.append(radius * np.cos(angles), radius[0] * np.cos(angles[0]))
        y = np.append(radius * np.sin(angles), radius[0] * np.sin(angles[0]))
        
        self.visualizations['circular'].setData(x, y)
    
    def _update_stereo_bars(self, data):
        spectrum = self._create_spectrum(data, self.chunk_size // 4)
        
        self.visualizations['stereo_top'].setOpts(height=spectrum)
        self.visualizations['stereo_bottom'].setOpts(height=-spectrum)


class AudioStream:
    """Manages audio input stream"""
    
    def __init__(self, callback, sample_rate=FS, chunk_size=CHUNK):
        self.callback = callback
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.stream = None
    
    def start(self):
        """Start audio stream"""
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            callback=self.callback
        )
        self.stream.start()
    
    def stop(self):
        """Stop audio stream"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def is_active(self):
        """Check if stream is active"""
        return self.stream is not None and self.stream.active


class AudioVisualizer(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        loadUi("main_window.ui", self)
        
        self.data = np.zeros(CHUNK)
        self.sensitivity = 1.0
        
        self.setup_plot_widget()
        self.viz_manager = VisualizationManager(self.plot_widget, CHUNK)
        self.viz_manager.setup("Frequency Bars")
        
        self.audio_stream = AudioStream(self.audio_callback)

        self.axes_shown = True
        
        self.connect_signals()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
    
    def load_stylesheet(self, filename):
        """Load external QSS stylesheet"""
        file = QFile(filename)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
    
    def setup_plot_widget(self):
        """Setup pyqtgraph plot widget"""
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1a1a2e')
        self.plot_widget.showGrid(x=False, y=False)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.getViewBox().setMenuEnabled(False)
        self.plot_widget.hideButtons()
        self.plot_widget.getAxis('left').setPen('#444')
        self.plot_widget.getAxis('bottom').setPen('#444')
        
        # Replace placeholder
        old_widget = self.plotWidget
        self.plotLayout.replaceWidget(old_widget, self.plot_widget)
        old_widget.deleteLater()
    
    def connect_signals(self):
        """Connect UI signals to slots"""
        self.startButton.clicked.connect(self.toggle_audio)
        self.vizCombo.currentTextChanged.connect(self.viz_manager.setup)
        self.sensitivitySlider.valueChanged.connect(self.update_sensitivity)
        self.axesButton.clicked.connect(self.toggle_axes)
    
    def toggle_audio(self):
        """Toggle audio stream on/off"""
        if self.audio_stream.is_active():
            self.stop_audio()
        else:
            self.start_audio()
    
    def toggle_axes(self):
        self.axes_shown = not self.axes_shown
        plot_item = self.plot_widget.getPlotItem()
        if not plot_item:
            return False
        plot_item.showAxis('bottom', show=self.axes_shown)
        plot_item.showAxis('left', show=self.axes_shown)
        return True
    
    def start_audio(self):
        """Start audio capture"""
        self.audio_stream.start()
        self.timer.start(UPDATE_INTERVAL)
        self.startButton.setText("⏸ STOP")
        self.startButton.setProperty("isActive", "true")
        self.startButton.style().unpolish(self.startButton)
        self.startButton.style().polish(self.startButton)
    
    def stop_audio(self):
        """Stop audio capture"""
        self.audio_stream.stop()
        self.timer.stop()
        self.startButton.setText("▶ START")
        self.startButton.setProperty("isActive", "false")
        self.startButton.style().unpolish(self.startButton)
        self.startButton.style().polish(self.startButton)
    
    def update_sensitivity(self, value):
        """Update sensitivity setting"""
        self.sensitivity = value / 10.0
        self.sensValueLabel.setText(f"{self.sensitivity:.1f}x")
    
    def audio_callback(self, indata, frames, time, status):
        """Audio input callback"""
        self.data = np.squeeze(indata) * self.sensitivity
    
    def update_visualization(self):
        """Update visualization with latest audio data"""
        self.viz_manager.update(self.data * self.sensitivity)
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.stop_audio()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = AudioVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()