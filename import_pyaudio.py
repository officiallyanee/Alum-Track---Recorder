import pyaudio
import wave
import threading
from collections import deque
import time

def record_system_audio(device_index, stop_event, buffer_seconds=5):
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024

    buffer_size = int(RATE / CHUNK * buffer_seconds)

    audio = pyaudio.PyAudio()
    audio_deque = deque(maxlen=buffer_size)

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        input_device_index=device_index,
                        frames_per_buffer=CHUNK)

    print("Recording... Press Enter to stop.")

    while not stop_event.is_set():
        data = stream.read(CHUNK)
        audio_deque.append(data)

    print("Recording finished.")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()

    return audio_deque, CHANNELS, audio.get_sample_size(FORMAT), RATE

def save_deque_to_wav(audio_deque, output_filename, channels, sample_width, rate):
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(rate)

    wf.writeframes(b''.join(audio_deque))

    wf.close()
    print(f"Audio saved as {output_filename}")

def input_thread(stop_event):
    input("Press Enter to stop recording...\n")
    stop_event.set()

# Main execution
if __name__ == "__main__":
    device_index = 2  # Replace with your system audio device index
    buffer_seconds = 60  # Amount of audio to keep in the buffer
    
    stop_event = threading.Event()

    # Start the input thread
    input_thread = threading.Thread(target=input_thread, args=(stop_event,))
    input_thread.start()

    # Start recording
    audio_deque, channels, sample_width, rate = record_system_audio(device_index, stop_event, buffer_seconds)

    # Save the audio from the deque to a file
    save_deque_to_wav(audio_deque, "output.wav", channels, sample_width, rate)

    # Wait for the input thread to finish
    input_thread.join()