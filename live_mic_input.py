# sounddevice docs: https://python-sounddevice.readthedocs.io/en/0.5.3/

import sounddevice as sd
import numpy as np

duration = 10
fs = 44100  # Sample rate - captures 44100 samples per second
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
sd.wait()
print(myrecording)
