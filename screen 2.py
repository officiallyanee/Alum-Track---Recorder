import time
import cv2
import numpy as np
from mss import mss
import threading

class CustomQueue:
    def __init__(self, max_size):
        self.queue = []
        self.max_size = max_size

    def add(self, element):
        if len(self.queue) == self.max_size:
            self.queue.pop()  # Remove the last element
        self.queue.insert(0, element)  # Add the new element to the front

    def get(self):
        if self.queue:
            return self.queue.pop()  # Remove the oldest element (the last in the list)
        return None

    def empty(self):
        return len(self.queue) == 0

    def qsize(self):
        return len(self.queue)

def capture_screenshots(duration=5, fps=40, max_queue_size=100):
    screenshot_queue = CustomQueue(max_queue_size)
    interval = 1 / fps
    sct = mss()
    monitor = sct.monitors[0]
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        loop_start = time.time()
        screenshot = np.array(sct.grab(monitor))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

        screenshot_queue.add(screenshot)  # Use custom queue method
        
        frame_count += 1
        processing_time = time.time() - loop_start
        sleep_time = max(0, interval - processing_time)
        time.sleep(sleep_time)
    
    actual_fps = frame_count / duration
    print(f"Captured {frame_count} frames in {duration} seconds (approx. {actual_fps:.2f} fps)")
    
    return screenshot_queue

def process_screenshots(queue, stop_event):
    while not stop_event.is_set() or not queue.empty():
        if not queue.empty():
            screenshot = queue.get()
            try:
                cv2.imwrite(f"screenshot_{time.time()}.png", screenshot)
                print(f"Processed a screenshot. Queue size: {queue.qsize()}")
            except Exception as e:
                print(f"Error saving screenshot: {e}")
        else:
            time.sleep(0.1)

def create_video_from_queue(queue, output_filename, fps, duration):
    while queue.empty():
        time.sleep(0.1)
    first_frame = queue.get()
    height, width, layers = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
    out.write(cv2.cvtColor(first_frame, cv2.COLOR_RGB2BGR))
    total_frames = int(fps * duration)
    frames_written = 1

    while frames_written < total_frames:
        if not queue.empty():
            frame = queue.get()
            out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            frames_written += 1
        else:
            time.sleep(0.01)

    out.release()
    print(f"Video saved as {output_filename}")

# Main execution
screenshot_queue = capture_screenshots(duration=10, fps=40, max_queue_size=500)
stop_event = threading.Event()
processing_thread = threading.Thread(target=process_screenshots, args=(screenshot_queue, stop_event))
processing_thread.start()

# Wait for processing to complete
while not screenshot_queue.empty():
    time.sleep(0.1)

stop_event.set()  # Signal to stop processing
processing_thread.join()  # Wait for the processing thread to finish

print("All screenshots processed")

video_thread = threading.Thread(target=create_video_from_queue, 
                                args=(screenshot_queue, "output_video.mp4", 30, 60))
video_thread.start()
video_thread.join()  # Wait for video creation to complete

print("Video creation completed")
