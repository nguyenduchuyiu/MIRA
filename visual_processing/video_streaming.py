import cv2
import threading
import time
import os

class VideoRecorder():
    "Video class based on openCV"
    def __init__(self, name="temp_video.avi", fourcc="MJPG", sizex=640, sizey=480, camindex=0, fps=30, resources_path="resources/"):
        self.open = True
        self.device_index = camindex
        self.fps = fps
        self.fourcc = fourcc
        self.frameSize = (sizex, sizey)
        self.save_path = resources_path + name
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.save_path, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()
        self.video_thread = None
        self.frames = []

    def record(self):
        "Video starts being recorded"
        while self.open:
            ret, video_frame = self.video_cap.read()
            if ret:
                self.video_out.write(video_frame)
                self.frames.append(video_frame)
                self.frame_counts += 1
                # Limit the size of the frames list to prevent memory overflow
                if len(self.frames) > 100:  # Example limit
                    self.frames.pop(0)
                # Removed cv2.imshow from here
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
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
                self.join()  # Ensure the thread is joined
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
            
if __name__ == "__main__":
    
    def start_recording(video_recorder):
        current_time = time.strftime("%Y%m%d-%H%M%S")
        video_name = f"record_{current_time}.avi"
        video_recorder.save_path = 'resources/' + video_name
        video_recorder.start()
        print(f"Recording started: {video_name}")

    def stop_recording(video_recorder):
        video_recorder.stop()
        print(f"Video saved to: {video_recorder.save_path}")
        return video_recorder.save_path
    
    video_recorder = VideoRecorder(name="record_0.avi", fourcc="MJPG", sizex=640, sizey=480, camindex=0, fps=30)
    start_recording(video_recorder)
    
    # Display frames in the main thread
    while video_recorder.open:
        if video_recorder.frames:
            cv2.imshow('Recording', video_recorder.frames[-1])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1/video_recorder.fps)
    
    stop_recording(video_recorder)
    cv2.destroyAllWindows()
