import time
import cv2
from audio_processing.asr import ASR
from reasoning_engine.nlu import NLU
from response_generation.tts import TextToSpeech
from response_generation.gtts import GTextToSpeech
from visual_processing.vision import VisionProcessing
from audio_processing.speech_to_text import SpeechToText


def record_video(duration, fps=30):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    current_time = time.strftime("%Y%m%d-%H%M%S")
    video_name = f"resources/videos/record_{current_time}.avi"
    out = cv2.VideoWriter(video_name, fourcc, fps, (640, 480))

    start_time = time.time()  # Start timing
    frame_count = 0

    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Recording', frame)
            frame_count += 1
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    elapsed_time = time.time() - start_time  # End timing
    recorded_fps = frame_count / elapsed_time
    print(f"Total frames: {frame_count}")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Recorded FPS: {recorded_fps:.2f}")
    print(f"Video recording time: {elapsed_time:.2f} seconds")

    return video_name


if __name__ == "__main__":
    RECORD_DURATION = 3
    image_path = ''
    nlu = NLU()
    # tts = TextToSpeech()
    gtts = GTextToSpeech()
    vision_processing = VisionProcessing()
    # asr_thread = ASR()
    speech_to_text = SpeechToText()
    
    while True:
        # transcript = asr_thread.start()
        transcript = speech_to_text.start() 
        
        # transcript = input("Please enter the transcript: ")
        
        if ("can" in transcript.lower() and "see" in transcript.lower()):
            print("Let me see")
            # tts.synthesize("Let me see") #FIXME: Uncomment this
            video_path = record_video(duration=RECORD_DURATION)  # Record for 3 seconds
            
            if video_path is None:
                print("Video recording failed. Skipping analysis.")
                # tts.synthesize("Video recording failed.") #FIXME: Uncomment this
                continue
        
            image_path = vision_processing.analyze_image(video_path)
        
        elif ("i have no questions" in transcript.lower()):
            print("OK, Ask me anything if you want!")
            # tts.synthesize("OK, Ask me anything if you want!") #FIXME: Uncomment this
            exit()
        
        response = nlu.process(transcript, f'resources/{image_path}')
        print(f"Mira Response: {response}")
        
        # tts.synthesize(response) #FIXME: Uncomment this
        gtts.synthesize(response)
        # Reset
        image_path = ''
        # asr_thread.reset_transcript()
        # break
