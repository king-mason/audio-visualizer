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
