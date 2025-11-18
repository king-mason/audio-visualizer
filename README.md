# audio-visualizer

# File Input Mode
- When you run the .py file, it shows you a blank PyQT canvas from where you can input an audio file
- Once you've inputted your file, wait a few seconds for the graphs to populate
- The graphs show volume, brightness and percussion throughout the file
- Volume is the raw audio data loaded in through Librosa, brightness is the spectral centroids (where most of the sound's frequencies are) of the graph, and percussion is the zero crossing rate (when the waveform crosses 0 Db) of the sound through time