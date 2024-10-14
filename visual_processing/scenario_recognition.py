import os
from dotenv import load_dotenv
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import cv2

class ScenarioRecognition:
    
    def __init__(self):
        load_dotenv()
        self.endpoint = os.getenv("AZURE_VISION_ENDPOINT")
        self.azure_vision_key = os.getenv("AZURE_VISION_KEY")


        self.client = ImageAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.azure_vision_key)
        )

    def analyze_image(self, video_path):
        key_frame = self.extract_final_frame(video_path)
        
        _, encoded_image = cv2.imencode('.jpg', key_frame)
        image_data = encoded_image.tobytes()
        
        result = self.client.analyze(
            image_data=image_data,
            visual_features=[
                VisualFeatures.DENSE_CAPTIONS,
            ],
            gender_neutral_caption=True,
        )

        # Check if dense captions exist in the response
        if 'denseCaptionsResult' in result and 'values' in result['denseCaptionsResult']:
            captions = result['denseCaptionsResult']['values']
            
            # Extract text from each caption
            extracted_texts = [caption['text'] for caption in captions]
            
            # Join the texts together with appropriate punctuation
            scenario = '. '.join(extracted_texts) + '.'
            
            return scenario
        else:
            return "No scenario found."
        
        
    def extract_final_frame(self, video_path):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video.")
            return

        # Move to the last frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)

        # Read the last frame
        ret, frame = cap.read()

        # Check if the last frame was read successfully
        if ret:
            # Save the last frame as an image
            cv2.imwrite("resources/final_frame.jpg", frame)
            return frame
        else:
            print("Error: Could not read the last frame.")

        # Release the video capture object
        cap.release()

if __name__ == "__main__":
    scenario_recognition = ScenarioRecognition()
    print(scenario_recognition.analyze_image("resources/test_video.mp4"))
