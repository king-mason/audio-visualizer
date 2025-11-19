# Audio Visualizer

Turns microphone or audio file input into visualization.

### Features
- Audio visualization of microphone input across time
    - Using Matplotlib graphing
- Real-time waveform visualization of frequency spectrum
    - Using single Qt window

### Implementation
- `live_mic_input.py`: records sound first, then displays the recording with Matplotlib
    - uses sounddevice.rec() to record signal over time
    - graphing can be applied to file submission in the future
- `qt_live_input.py`: real-time visual of sound using PyQt plot widget
    - uses sounddevice.InputStream() to record signal over frequency
    - sends input stream directly to plot through automatic PyQt handling
    - uses numpy for managing data

### Development
See latest documentation report for current development goals and progress

# audio-visualizer

# File Input Mode
- When you run the .py file, it shows you a blank PyQT canvas from where you can input an audio file
- Once you've inputted your file, wait a few seconds for the graphs to populate
- The graphs show volume, brightness and percussion throughout the file
- Volume is the raw audio data loaded in through Librosa, brightness is the spectral centroids (where most of the sound's frequencies are) of the graph, and percussion is the zero crossing rate (when the waveform crosses 0 Db) of the sound through time