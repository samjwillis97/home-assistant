import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal
from shazamio import Shazam
import asyncio
import wave

# ---------------- AUDIO SETUP
RATE = 44800
AUDIO_CHANNELS = 1
CHUNK = 2048
AUDIO_DEVICE_INDEX = 1
FORMAT = pyaudio.paFloat32

# ---------------- FFT SETUP
SMOOTHING = 0.7
BAND_EDGES = [
    (20, 80),
    (80, 160),
    (160, 320),
    (320, 640),
    (640, 1280),
    (1280, 2560),
    (2560, 5120),
    (5120, 10240),
    (10240, 20000)
]
FREQ_RESOLUTION = RATE / CHUNK

# ---------------- SHAZAM
SAMPLE_LENGTH = 10  # Seconds


bands = [(int(low/FREQ_RESOLUTION), int(high/FREQ_RESOLUTION))
         for low, high in BAND_EDGES]
band_labels = ['Sub', 'Bass', 'Low Bass', 'Low Mid',
               'Mid', 'High Mid', 'Pres', 'Treble', 'Brill']

# Matplotlib setup
plt.ion()
fig, ax = plt.subplots(figsize=(12, 6))
x_pos = np.arange(len(bands))
bars = ax.bar(x_pos, np.zeros(len(bands)), color='cyan',
              edgecolor='blue', linewidth=1.5)

ax.set_ylim(0, 1)
ax.set_xlim(-0.5, len(bands) - 0.5)
ax.set_xticks(x_pos)
ax.set_xticklabels(band_labels)
ax.set_ylabel('Amplitude')
ax.set_title('Music Visualizer - 9 Bands')
ax.grid(axis='y', alpha=0.3)

p = pyaudio.PyAudio()

# print(p.get_device_info_by_index(AUDIO_DEVICE_INDEX))

print("Starting audio stream...")

# input stream setup
stream = p.open(
    format=FORMAT,
    rate=RATE,
    channels=AUDIO_CHANNELS,
    input_device_index=AUDIO_DEVICE_INDEX,
    input=True,
    frames_per_buffer=CHUNK
)

window = signal.get_window('hann', CHUNK)


async def identify_song(audio_frames, filename='temp_audio.wav'):
    """Record audio to file and identify using Shazam"""
    # Save audio to WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(AUDIO_CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_frames))

    # Identify song
    shazam = Shazam()
    result = await shazam.recognize(filename)
    return result


async def main():
    # Record initial sample for song identification
    print(f"Recording {SAMPLE_LENGTH} seconds for song identification...")
    chunks_needed = int(RATE / CHUNK * SAMPLE_LENGTH)
    audio_frames = []
    band_values = np.zeros(9)

    for i in range(chunks_needed):
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        audio_frames.append(raw_data)

        # Still visualize while recording
        data = np.frombuffer(raw_data, dtype=np.float32)
        windowed = data * window
        fft_data = np.abs(np.fft.rfft(windowed))
        new_values = np.array([np.sum(fft_data[low:high])
                              for low, high in bands])
        band_values_local = SMOOTHING * \
            band_values + (1 - SMOOTHING) * new_values

        if band_values_local.max() > 0:
            normalized = np.sqrt(band_values_local / band_values_local.max())
        else:
            normalized = band_values_local

        for bar, value in zip(bars, normalized):
            bar.set_height(value)
        plt.pause(0.001)

    print("Identifying song...")
    try:
        result = await identify_song(audio_frames)
        print(result)
        if result.get('track'):
            track = result['track']
            print(
                f"Song identified: {track.get('title', 'Unknown')} by {track.get('subtitle', 'Unknown')}")
        else:
            print("Could not identify song")
    except Exception as e:
        print(f"Error identifying song: {e}")

    # Continue with visualization
    print("Continuing with visualization...")
    while True:
        data = np.frombuffer(stream.read(
            CHUNK, exception_on_overflow=False), dtype=np.float32)

        windowed = data * window
        fft_data = np.abs(np.fft.rfft(windowed))

        new_values = np.array([np.sum(fft_data[low:high])
                              for low, high in bands])

        band_values = SMOOTHING * band_values + (1 - SMOOTHING) * new_values

        # Prevent division by zero
        if band_values.max() > 0:
            normalized = np.sqrt(band_values / band_values.max())
        else:
            normalized = band_values

        # Update bars
        for bar, value in zip(bars, normalized):
            bar.set_height(value)

        plt.pause(0.001)  # Small pause to update plot


if __name__ == '__main__':
    asyncio.run(main())
