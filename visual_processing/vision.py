import cv2

class VisionProcessing:
    
    def __init__(self):
        pass
    
    def analyze_image(self, video_path):
        image_path = self.extract_final_frame(video_path)
        return image_path
        
        
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
            image_path = f'images/{video_path.split("/")[-1].replace(".avi", ".jpg")}'  # Extract the last part of the video path and change the extension
            cv2.imwrite(f'resources/{image_path}', frame)
            return image_path
        else:
            print("Error: Could not read the last frame.")

        # Release the video capture object
        cap.release()
