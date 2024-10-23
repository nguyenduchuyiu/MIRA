# MIRA - Maybe Intelligent, Rather Adequate

## Overview
MIRA is an intelligent assistant that processes real-time audio and visual inputs, utilizing advanced technologies for speech recognition, computer vision, and natural language understanding.

## Core Functionalities
- **Audio Input**: Real-time capture, speech-to-text conversion and noise reduction.
- **Visual Input**: Real-time video/image capture, object/face detection, and OCR.
- **Data Processing**: NLU for audio, computer vision for visuals, contextual awareness, and error handling.
- **Response Generation**: Responses via speech, text, or visual feedback, with integration to external APIs for advanced reasoning.

## Architecture
MIRA features a modular design with:
- Audio Processing Module
- Visual Processing Module
- Reasoning Engine Module
- Response Generation Module
- Database Module

## Technology Stack
- **Primary Language**: Python
- **Optional**: C++, JavaScript/HTML/CSS
- **Libraries**: SpeechRecognition, PyAudio, gTTS, OpenCV, SQLite, FastAPI/Flask.

## Getting Started
### Prerequisites
- Python 3.10.12
- Required libraries (see `requirements.txt`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/nguyenduchuyiu/mira.git
   cd mira
   ```

2. Install libraries:
   ```bash
   pip install -r requirements.txt
   ```
## API Setup

### Azure Speech-to-Text
1. **Create a Azure Speech Service** and enable the Speech-to-Text API.
2. **Set the environment variable:**
   ```bash
   export AZURE_SPEECH_KEY="your-api-key"
   ```

### Gemini API
1. **Obtain your API key** from the Gemini API provider.
2. **Set up API in your environment:**
  ```bash
  export API_KEY="your_gemini_api_key"
  ```

### Running MIRA
Start the application with:
```bash
python3 app.py
```
Open http://127.0.0.1:5000/ in browser.

## Contribution
Contributions are welcome! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
Licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Contact
For questions or feedback, contact [nguyenduchuyiu@gmail.com](mailto:nguyenduchuyiu@gmail.com).
