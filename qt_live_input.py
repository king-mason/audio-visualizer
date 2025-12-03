import sys
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, QFile, QTextStream
from PyQt6.uic.load_ui import loadUi
import pyqtgraph as pg

from file_input import AudioFeatureExtractor
from vis_manager import VisualizationManager


# TODO:
# 1. final functionality work
#     - file play
#     - polishing
# 2. update audio sensitivity

# Audio configuration
FS = 44100
CHUNK = 2048
UPDATE_INTERVAL = 20


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

        self.extractor = AudioFeatureExtractor(self.loadLabel)
        
        self.setup_plot_widget()
        self.viz_manager = VisualizationManager(self.plot_widget, CHUNK)
        self.viz_manager.setup("Frequency Bars")

        self.liveInputButton.hide()
        
        self.audio_stream = AudioStream(self.audio_callback)

        self.axes_shown = True
        
        self.connect_signals()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
    

    def connect_signals(self):
        """Connect UI signals to slots"""
        self.startButton.clicked.connect(self.toggle_audio)
        self.vizCombo.currentTextChanged.connect(self.on_viz_change)
        self.sensitivitySlider.valueChanged.connect(self.update_sensitivity)
        self.axesButton.clicked.connect(self.toggle_axes)
        self.loadButton.clicked.connect(self.load_audio)
        self.liveInputButton.clicked.connect(self.switch_to_live_viz)

    def on_viz_change(self, viz_type):
         """Handle visualization type change"""
         pass
         if viz_type == "Audio Stream":
            self.switch_to_matplotlib()
         else:
            self.switch_from_matplotlib()
            self.viz_manager.setup(viz_type)


    def load_audio(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a);;All Files (*)")
        self.extractor.load_audio(filename)
        self.switch_to_file_viz()

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
        
        # Create file visualization container (hidden initially)
        self.file_viz_widget = QWidget()
        self.file_viz_layout = QVBoxLayout(self.file_viz_widget)
        self.file_viz_layout.setContentsMargins(0, 0, 0, 0)
        self.file_viz_layout.addWidget(self.extractor.waveform_canvas)
        self.file_viz_layout.addWidget(self.extractor.spectral_canvas)
        self.file_viz_layout.addWidget(self.extractor.zcr_canvas)
        
        # Replace placeholder - add live plot by default
        old_widget = self.plotWidget
        self.plotLayout.replaceWidget(old_widget, self.plot_widget)
        old_widget.deleteLater()
        
        self.current_plot_mode = 'live'
    
    def switch_to_matplotlib(self):
        self.plotLayout.replaceWidget(self.plot_widget, self.file_viz_widget)
        self.plot_widget.hide()
        self.file_viz_widget.show()

    def switch_from_matplotlib(self):
        self.plotLayout.replaceWidget(self.file_viz_widget, self.plot_widget)
        self.file_viz_widget.hide()
        self.plot_widget.show()

    def switch_to_file_viz(self):
        """Switch plot area to show file visualizations"""
        if self.current_plot_mode == 'live':
            self.vizCombo.setCurrentText("Audio Stream")
            self.liveInputButton.show()
            self.current_plot_mode = 'file'

    def switch_to_live_viz(self):
        """Switch plot area to show live visualizations"""
        if self.current_plot_mode == 'file':
            self.liveInputButton.hide()
            self.current_plot_mode = 'live'
            self.loadLabel.setText('Live input mode')
    
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
        self.startButton.style().unpolish(self.startButton) # refresh
        self.startButton.style().polish(self.startButton)
    
    def stop_audio(self):
        """Stop audio capture"""
        self.audio_stream.stop()
        self.timer.stop()
        self.startButton.setText("▶ START")
        self.startButton.setProperty("isActive", "false")
        self.startButton.style().unpolish(self.startButton) # refresh
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