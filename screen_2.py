import time
import cv2
import numpy as np
from mss import mss
import threading

class CustomQueue:
    def __init__(self, max_size):
        self.queue = []
        self.max_size = max_size
        self.lock = threading.Lock()

    def add(self, element):
        with self.lock:
            if len(self.queue) == self.max_size:
                self.queue.pop(0)  # Remove the oldest element
            self.queue.append(element)  # Add the new element to the end

    def get(self):
        with self.lock:
            if self.queue:
                return self.queue.pop(0)  # Remove and return the oldest element
        return None

    def empty(self):
        with self.lock:
            return len(self.queue) == 0

    def qsize(self):
        with self.lock:
            return len(self.queue)

def capture_screenshots(screenshot_queue, stop_event, fps=40):
    interval = 1 / fps
    sct = mss()
    monitor = sct.monitors[0]
    
    start_time = time.time()
    frame_count = 0
    
    while not stop_event.is_set():
        loop_start = time.time()
        screenshot = np.array(sct.grab(monitor))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

        screenshot_queue.add(screenshot)
        
        frame_count += 1
        processing_time = time.time() - loop_start
        sleep_time = max(0, interval - processing_time)
        time.sleep(sleep_time)
    
    duration = time.time() - start_time
    actual_fps = frame_count / duration
    print(f"Captured {frame_count} frames in {duration:.2f} seconds (approx. {actual_fps:.2f} fps)")

def create_video_from_queue(queue, output_filename, fps):
    if queue.empty():
        print("No frames to process. Video creation aborted.")
        return

    first_frame = queue.get()
    height, width, layers = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
    out.write(cv2.cvtColor(first_frame, cv2.COLOR_RGB2BGR))
    frames_written = 1

    while not queue.empty():
        frame = queue.get()
        out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        frames_written += 1

    out.release()
    print(f"Video saved as {output_filename} with {frames_written} frames")

def input_thread(stop_event):
    input("Press Enter to stop recording...\n")
    stop_event.set()

# Main execution
if __name__ == "__main__":
    fps = 40
    max_queue_size = fps * 60  # 60 seconds of footage at 40 fps
    stop_event = threading.Event()
    screenshot_queue = CustomQueue(max_queue_size)
    
    # Start the screenshot capture thread
    capture_thread = threading.Thread(target=capture_screenshots, args=(screenshot_queue, stop_event, fps))
    capture_thread.start()

    # Start the input thread
    input_thread = threading.Thread(target=input_thread, args=(stop_event,))
    input_thread.start()

    # Wait for the capture thread to finish
    capture_thread.join()

    print("Screenshot capture completed")

    # Create video from the queue
    create_video_from_queue(screenshot_queue, "output_video.mp4", fps)

    print("Video creation completed")