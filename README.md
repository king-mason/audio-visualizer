# Audio Visualizer

Turns microphone or audio file input into visualization.

### Features
- Audio visualization of microphone input across time
    - Using Matplotlib graphing
- Real-time waveform visualization of frequency spectrum
    - Using single Qt window
- Audio visualization of file input
    - Processes sound using Librosa and graphs results

### Implementation
- `live_mic_input.py`: records sound first, then displays the recording with Matplotlib
    - uses sounddevice.rec() to record signal over time
    - graphing can be applied to file submission in the future
- `qt_live_input.py`: real-time visual of sound using PyQt plot widget
    - uses sounddevice.InputStream() to record signal over frequency
    - sends input stream directly to plot through automatic PyQt handling
    - uses numpy for managing data
- `file_input_visual.py`: accepts audio file input, processes its' data and then visualizes it
    - uses Librosa to get data for volume, brightness and percussion from the audio file
    - volume - raw data loaded in through Librosa
    - brightness - spectral centroids, or where most of the sound's frequencies are
    - percussion - zero crossing rate, or when the waveform crosses 0 Db

### Development
See latest documentation report for current development goals and progress
