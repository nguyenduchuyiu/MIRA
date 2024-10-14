import threading
import time
import cv2
import queue
from audio_processing.asr import ASR
from reasoning_engine.nlu import NLU
from audio_processing.tts import TextToSpeech
from visual_processing.video_streaming import VideoRecorder
from visual_processing.scenario_recognition import ScenarioRecognition

def start_recording():
    global video_thread
    global asr_thread
    
    current_time = time.strftime("%Y%m%d-%H%M%S")
    video_name = f"record_{current_time}.avi"
    
    video_thread = VideoRecorder(name=video_name, fourcc="MJPG", sizex=640, sizey=480, camindex=0, fps=30)
    asr_thread = ASR()
    
    video_thread.start()
    transcript = asr_thread.start()
    
    print("Recording started")
    
    return transcript, video_thread.save_path


def stop_recording():
    frame_counts = video_thread.frame_counts
    elapsed_time = time.time() - video_thread.start_time
    recorded_fps = frame_counts / elapsed_time
    print("total frames " + str(frame_counts))
    print("elapsed time " + str(elapsed_time))
    print("recorded fps " + str(recorded_fps))
    video_thread.stop() 

    # Makes sure the threads have finished
    print(threading.active_count())
    while threading.active_count() > 1:
        time.sleep(1)


def nlu_process(nlu, transcript, scenario):
    response = nlu.process(transcript, scenario)
    print(f"Gemini Response: {response}")
    return response


if __name__ == "__main__":
    asr = ASR()
    nlu = NLU()
    tts = TextToSpeech()
    scenario_recognition = ScenarioRecognition()
    
    while True:
        transcript, video_path = start_recording()
        stop_recording()
        scenario = scenario_recognition.analyze_image(video_path)
        response = nlu_process(nlu, transcript, scenario)
        tts.synthesize(response)
        print("Response complete. Ready for next input.")
        asr.reset_transcript()
