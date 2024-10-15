import threading
import time
from audio_processing.asr import ASR
from reasoning_engine.nlu import NLU
from audio_processing.tts import TextToSpeech
from visual_processing.video_streaming import VideoRecorder
from visual_processing.scenario_recognition import ScenarioRecognition

def start_recording():
    global video_thread
    
    current_time = time.strftime("%Y%m%d-%H%M%S")
    video_name = f"record_{current_time}.avi"
    
    video_thread = VideoRecorder(name=video_name, fourcc="MJPG", sizex=640, sizey=480, camindex=0, fps=30)

    video_thread.start()
    
    return video_thread.save_path


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




if __name__ == "__main__":
    nlu = NLU()
    tts = TextToSpeech()
    scenario_recognition = ScenarioRecognition()
    asr_thread = ASR()
    
    while True:
        print("I'm hearing!")
        transcript = asr_thread.start()
        
        print("I'm recording!")
        video_path = start_recording()
        time.sleep(1)
        stop_recording()
        
        print("I'm analyzing!")
        scenario = scenario_recognition.analyze_image(video_path)
        
        print("I'm reasoning!")
        response = nlu.process(transcript, scenario)
        print(f"Gemini Response: {response}")
        
        print("I'm synthesizing!")
        tts.synthesize(response)
        print("Response complete. Ready for next input.")
        
        asr_thread.reset_transcript()
        
