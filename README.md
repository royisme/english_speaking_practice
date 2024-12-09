# English Speaking Practice Assistant

An interactive application to help improve English pronunciation and speaking skills using AI-powered feedback.

## Features

- Text input/upload for practice material
- Audio recording capability
- Real-time speech analysis
- AI-powered pronunciation feedback
- Phonetic guidance for difficult words
- Audio playback functionality

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Azure Speech Services subscription
- Microphone access

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

4. Edit `.env` file with your API credentials:
```
OPENAI_API_KEY=your_openai_api_key_here
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=your_azure_region_here
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL

3. Follow the on-screen instructions to:
   - Enter or upload text
   - Get pronunciation guidance
   - Record your speech
   - Receive feedback and analysis
   - Listen to your recording

## How It Works

1. **Text Input**: Enter text directly or upload a file
2. **Pronunciation Guide**: Get AI-generated phonetic guidance
3. **Recording**: Record your speech using your microphone
4. **Analysis**: 
   - Speech-to-text conversion using Azure Speech Services
   - Pronunciation analysis and feedback using OpenAI
5. **Feedback**: Receive detailed feedback on:
   - Pronunciation accuracy
   - Common mistakes
   - Improvement suggestions
   - Phonetic tips

## Security Note

- Never commit your `.env` file with actual API keys
- Keep your API keys secure and private
- Regularly rotate your API keys for better security
