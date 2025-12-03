import numpy as np
import pyqtgraph as pg

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class VisualizationManager:
    """Manages different visualization types and their rendering"""
    
    def __init__(self, plot_widget, extractor, chunk_size):
        self.plot_widget = plot_widget
        self.extractor = extractor
        self.chunk_size = chunk_size
        self.visualizations = {}
        self.current_viz = None
        self.file_mode = False
        
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
            "Stereo Bars": self._setup_stereo_bars,
            "Audio Stream": self._setup_audio_stream
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
        # ROSE CHANGE - DEC 2, 2025 
        """Setup simple color-changing waveform."""
        self.wave_curve = self.plot_widget.plot(
            pen=pg.mkPen('#00ffaa', width=5)
        )
        self.smoothed = None
        self.plot_widget.setYRange(-1, 1)
        
        #ROSE CHANGE END - DEC 2, 2025 
    
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
    
    def _setup_audio_stream(self):
        self.extractor.reset_audio_data()
        self.extractor.extract_and_visualize()

    
    def update(self, data):
        """Update visualization with new audio data"""
        update_methods = {
            "Frequency Bars": self._update_freq_bars,
            "Waveform": self._update_waveform,
            "Spectrum Line": self._update_spectrum_line,
            "Circular Spectrum": self._update_circular,
            "Stereo Bars": self._update_stereo_bars,
            "Audio Stream": self._update_audio_stream
        }
        
        if self.current_viz in update_methods:
            update_methods[self.current_viz](data)
    
    def _create_spectrum(self, data, max_values):
        windowed = data * np.hamming(len(data))
        fft = np.fft.rfft(windowed)
        spectrum = np.abs(fft[:max_values]) * 100 / self.chunk_size # amplify fft height
        return np.clip(spectrum, 0, 1)
    
    def _update_freq_bars(self, data):
        spectrum = self._create_spectrum(data, self.chunk_size // 2)
        
        # Smooth bars by reducing maximum change
        bars = self.visualizations['freq_bars']
        current = bars.opts['height']
        spectrum = np.maximum(spectrum, current * 0.7)
        bars.setOpts(height=spectrum)
    
    def _update_waveform(self, data):
        #ROSE CHANGE - DEC 2, 2025
        """Changing waveform with colors"""
        # animation 
        if self.smoothed is None:
            self.smoothed = data
        else:
            self.smoothed = 0.8 * self.smoothed + 0.2 * data
        y = self.smoothed
        # amplitude calculation 
        amplitude = np.sqrt(np.mean(y**2))
        # color change 
        if amplitude < 0.0025:
            c = (0, 180, 255)     
        elif amplitude < 0.010:
            c = (0, 255, 150)     
        else:
            c = (255, 50, 180)   
        self.wave_curve.setPen(pg.mkPen(c, width=5))
        self.wave_curve.setData(y)
        #ROSE CHANGE - DEC 2, 2025 
    
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
        spectrum = self._create_spectrum(data, self.chunk_size // 8)
        
        mirrored = np.append(spectrum[::-1], spectrum)

        self.visualizations['stereo_top'].setOpts(height=mirrored)
        self.visualizations['stereo_bottom'].setOpts(height=-mirrored)
    
    def _update_audio_stream(self, data):
        # print(data)
        self.extractor.update_audio_data(data)
        self.extractor.extract_and_visualize()
        # self.visualizations['waveform'].setData(data)
