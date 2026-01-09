import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.fftpack import fft
from scipy import signal
from shazamio import Shazam
import asyncio
import wave
from collections import deque
import aiohttp

# ---------------- AUDIO SETUP
RATE = 44800
AUDIO_CHANNELS = 1
CHUNK = 2048
AUDIO_DEVICE_INDEX = 1
FORMAT = pyaudio.paFloat32

# ---------------- FFT SETUP
SMOOTHING = 0.7
PEAK_FALL_RATE = 0.01  # How fast peaks fall per frame
REFERENCE_LEVEL_DECAY = 0.995  # How fast the reference level decays (closer to 1 = slower)
REFERENCE_LEVEL_ATTACK = 1.5  # Multiplier when new peak exceeds reference
NUM_SEGMENTS = 20  # Number of vertical segments per band
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
SHAZAM_INTERVAL = 30  # How often to identify songs (seconds)

# Shared audio buffer
chunks_needed = int(RATE / CHUNK * SAMPLE_LENGTH)
audio_buffer = deque(maxlen=chunks_needed)


bands = [(int(low/FREQ_RESOLUTION), int(high/FREQ_RESOLUTION))
         for low, high in BAND_EDGES]
band_labels = ['Sub', 'Bass', 'Low Bass', 'Low Mid',
               'Mid', 'High Mid', 'Pres', 'Treble', 'Brill']

# Matplotlib setup - old school segmented style
plt.ion()
fig, ax = plt.subplots(figsize=(14, 7), facecolor='black')
ax.set_facecolor('black')

x_pos = np.arange(len(bands))

# Create segmented bars
segment_height = 1.0 / NUM_SEGMENTS
segment_gap = segment_height * 0.15  # 15% gap between segments
bar_width = 0.7

# Store segments for each band
segments = []
for band_idx in x_pos:
    band_segments = []
    for seg_idx in range(NUM_SEGMENTS):
        # Position of this segment
        y_bottom = seg_idx * segment_height
        y_pos = (seg_idx + 0.5) * segment_height

        # Color based on height: green (0-40%) -> yellow (40-70%) -> red (70-100%)
        if y_pos < 0.4:
            color = '#00ff00'  # Green
        elif y_pos < 0.7:
            color = '#ffff00'  # Yellow
        else:
            color = '#ff0000'  # Red

        # Create rectangle
        rect = Rectangle((band_idx - bar_width/2, y_bottom),
                         bar_width, segment_height - segment_gap,
                         facecolor=color, edgecolor='black', linewidth=1)
        rect.set_visible(False)  # Start hidden
        ax.add_patch(rect)
        band_segments.append(rect)
    segments.append(band_segments)

# Peak hold lines
peak_lines = []
for i in x_pos:
    line, = ax.plot([i - bar_width/2, i + bar_width/2], [0, 0],
                    color='#ffffff', linewidth=3, alpha=0.9)
    peak_lines.append(line)

ax.set_ylim(0, 1)
ax.set_xlim(-0.5, len(bands) - 0.5)
ax.set_xticks(x_pos)
ax.set_xticklabels(band_labels, color='#00ff00', fontsize=10, fontweight='bold')
ax.set_ylabel('Amplitude', color='#00ff00', fontsize=12, fontweight='bold')
ax.set_title('♪ SPECTRUM ANALYZER ♪', color='#00ff00', fontsize=16, fontweight='bold', pad=20)
ax.tick_params(axis='y', colors='#00ff00')
ax.tick_params(axis='x', colors='#00ff00')

# Style spines
for spine in ax.spines.values():
    spine.set_color('#00ff00')
    spine.set_linewidth(2)

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
    """Identify song from audio frames using Shazam"""
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


async def get_track_duration_musicbrainz(title, artist):
    """Get track duration from MusicBrainz API"""
    try:
        # Build search query
        query = f'recording:"{title}" AND artist:"{artist}"'
        url = "https://musicbrainz.org/ws/2/recording/"
        params = {
            'query': query,
            'fmt': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'RaspberryPiMusicListener/0.1 (sam@williscloud.org)'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('recordings') and len(data['recordings']) > 0:
                        recording = data['recordings'][0]
                        # Duration is in milliseconds
                        duration_ms = recording.get('length')
                        if duration_ms:
                            return duration_ms / 1000  # Convert to seconds
        return None
    except Exception as e:
        print(f"Error fetching duration from MusicBrainz: {e}")
        return None


async def visualization_task():
    """Continuously visualize audio and populate the buffer"""
    band_values = np.zeros(9)
    peak_values = np.zeros(9)
    reference_level = 1.0  # Adaptive reference for normalization
    loop = asyncio.get_event_loop()

    while True:
        # Read audio in a non-blocking way
        raw_data = await loop.run_in_executor(
            None,
            lambda: stream.read(CHUNK, exception_on_overflow=False)
        )
        audio_buffer.append(raw_data)

        # Process for visualization
        data = np.frombuffer(raw_data, dtype=np.float32)
        windowed = data * window
        fft_data = np.abs(np.fft.rfft(windowed))
        new_values = np.array([np.sum(fft_data[low:high])
                              for low, high in bands])

        band_values = SMOOTHING * band_values + (1 - SMOOTHING) * new_values

        # Update adaptive reference level
        current_max = band_values.max()
        if current_max > reference_level:
            # Fast attack when signal exceeds reference
            reference_level = current_max * REFERENCE_LEVEL_ATTACK
        else:
            # Slow decay when signal is below reference
            reference_level *= REFERENCE_LEVEL_DECAY
            # Prevent reference from getting too small
            reference_level = max(reference_level, current_max * 0.5, 0.01)

        # Normalize against adaptive reference level
        if reference_level > 0:
            normalized = np.sqrt(band_values / reference_level)
            # Clip to max of 1.0
            normalized = np.minimum(normalized, 1.0)
        else:
            normalized = band_values

        # Update peaks: if current value exceeds peak, set new peak
        # Otherwise, let peak fall slowly
        for i, value in enumerate(normalized):
            if value > peak_values[i]:
                peak_values[i] = value
            else:
                peak_values[i] = max(0, peak_values[i] - PEAK_FALL_RATE)

        # Update segmented bars
        for band_idx, value in enumerate(normalized):
            # Determine how many segments to light up
            num_lit_segments = int(value * NUM_SEGMENTS)

            # Update visibility of segments
            for seg_idx, segment in enumerate(segments[band_idx]):
                if seg_idx < num_lit_segments:
                    segment.set_visible(True)
                else:
                    segment.set_visible(False)

        # Update peak lines
        for i, (line, peak) in enumerate(zip(peak_lines, peak_values)):
            line.set_ydata([peak, peak])

        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        await asyncio.sleep(0.001)  # Yield control to other tasks


async def shazam_task():
    """Periodically identify songs from the audio buffer"""
    print(
        f"Shazam task started - will identify every {SHAZAM_INTERVAL} seconds")

    while True:
        # Wait for buffer to fill
        while len(audio_buffer) < chunks_needed:
            await asyncio.sleep(0.1)

        print("Identifying song...")
        try:
            # Create a copy of current buffer
            audio_frames = list(audio_buffer)
            result = await identify_song(audio_frames)

            # Extract offset from matches
            offset = None
            if result.get('matches') and len(result['matches']) > 0:
                offset = result['matches'][0].get('offset')

            if result.get('track'):
                track = result['track']
                title = track.get('title', 'Unknown')
                artist = track.get('subtitle', 'Unknown')

                print(f"♪ Song identified: {title} by {artist}")

                # Print offset if available
                if offset is not None:
                    print(f"  Position: {offset:.1f}s into song")

                    # Get duration from MusicBrainz
                    duration = await get_track_duration_musicbrainz(title, artist)
                    if duration:
                        remaining = duration - offset
                        print(
                            f"  Remaining: {int(remaining // 60)}:{int(remaining % 60):02d} / {int(duration // 60)}:{int(duration % 60):02d}")
                        print("Sleeping until song ends...")
                        await asyncio.sleep(remaining + 1)
                    else:
                        print("  Could not fetch duration from MusicBrainz")
                        # Wait for the interval
                        await asyncio.sleep(SHAZAM_INTERVAL)

            else:
                print("Could not identify song")
        except Exception as e:
            print(f"Error identifying song: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Run visualization and Shazam tasks concurrently"""
    await asyncio.gather(
        visualization_task(),
        shazam_task()
    )


if __name__ == '__main__':
    asyncio.run(main())
