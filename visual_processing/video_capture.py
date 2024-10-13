import cv2
import threading
import time

class VideoRecorder():
    "Video class based on openCV"
    def __init__(self, name="temp_video.avi", fourcc="MJPG", sizex=640, sizey=480, camindex=0, fps=30):
        self.open = True
        self.device_index = camindex
        self.fps = fps
        self.fourcc = fourcc
        self.frameSize = (sizex, sizey)
        self.video_filename = name
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()
        self.video_thread = None  # Add this line

    def record(self):
        "Video starts being recorded"
        while self.open:
            ret, video_frame = self.video_cap.read()
            if ret:
                self.video_out.write(video_frame)
                self.frame_counts += 1
                time.sleep(1/self.fps)
            else:
                break

    def stop(self):
        "Finishes the video recording therefore the thread too"
        if self.open:
            self.open = False
            try:
                self.video_out.release()
                self.video_cap.release()
                cv2.destroyAllWindows()
            except Exception as e:
                print(f"An error occurred while stopping video: {e}")

    def start(self):
        "Launches the video recording function using a thread"
        self.video_thread = threading.Thread(target=self.record)
        self.video_thread.start()

    def join(self):
        "Waits for the video thread to finish"
        if self.video_thread is not None:
            self.video_thread.join()
