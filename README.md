# Hinglish Cold Calling AI Agent

A voice-enabled AI assistant that conducts cold calls in Hinglish (a mix of Hindi and English) for various business scenarios.

## Project Overview

This application provides an AI voice assistant that can conduct cold calls in Hinglish for three key business scenarios:

1. **Demo Scheduling for ERP System** - Convinces potential customers to schedule a demo for an ERP system
2. **Candidate Interviewing** - Conducts initial screening interviews for AI/ML Engineer positions
3. **Payment/Order Follow-up** - Handles payment reminders and order follow-ups while maintaining good customer relationships

The application uses speech recognition to understand user input in Hinglish, processes it with an AI language model, and responds with synthesized speech.

## Features

- **Speech Recognition** - Captures and recognizes speech in Hinglish (Hindi-English mix)
- **Natural Language Processing** - Uses advanced LLMs to understand context and generate appropriate responses
- **Text-to-Speech** - Converts AI responses to natural-sounding Hinglish speech
- **Google Calendar Integration** - Can schedule demos and appointments directly in Google Calendar
- **Multiple User Interfaces**:
  - Terminal-based command-line interface
  - Graphical user interface built with Pygame
- **Customer Interaction Tracking** - Logs all interactions in a file-based CRM system


## Technical Architecture

The application consists of several Python modules:

- **main.py** - Entry point and service initialization
- **utils.py** - Core functionality including speech recognition, TTS, and AI response handling
- **system_prompts.py** - Contains conversation prompts for different scenarios
- **recording_helper.py** - Helper class for managing speech recognition
- **pygame_ui.py** - Graphical user interface implementation

  
## Requirements

- Python 3.8+
- Google Cloud account with Speech-to-Text, Text-to-Speech, and Calendar API enabled
- OpenAI API key
- PyAudio and compatible audio hardware

##  Installation

1. Clone this repository:
   ```
   git clone [https://github.com/devendraBainda/hinglish-cold-calling-agent.git]
   cd hinglish-cold-calling-agent
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   GOOGLE_SERVICE_FILE_PATH=path-to-your-google-credentials.json
   OPEN_AI_API_KEY=your-openai-api-key
   ```

4. Ensure you have the necessary Google Cloud credentials file (JSON) for Speech-to-Text, Text-to-Speech, and Calendar APIs.

## Usage

Run the application with:

```
python main.py
```

You'll be prompted to choose between terminal-based UI or graphical UI, then select one of the three conversation scenarios.

### Terminal Interface

In terminal mode:
1. Select a scenario (1-3)
2. Enter the customer email when prompted
3. Use the SPACE key to start and stop recording
4. Speak in Hinglish (mix of Hindi and English)
5. Press Ctrl+C to exit

### Graphical Interface

In graphical mode:
1. Select a scenario by clicking on the appropriate button
2. Enter the customer email in the text field (pre-filled for candidate interviews)
3. Use the "Start Recording" button or press SPACE to begin recording
4. Speak in Hinglish
5. Press the "Stop Recording" button or SPACE again to stop and process
6. Click "Back" to return to scenario selection or "Exit" to quit

## Speech Recognition Tips

- Speak clearly in a mix of Hindi and English
- Minimize background noise during recording
- Use the manual recording control (SPACE key) to ensure complete phrases are captured

## Customization

### Adding New Scenarios

1. Create a new system prompt in `system_prompts.py`
2. Add a new handler function in `utils.py`
3. Update the scenario selection in `main.py` and `pygame_ui.py`

### Modifying Prompts

Edit the `SYSTEM_PROMPTS` dictionary in `system_prompts.py` to modify the behavior of the AI assistant for different scenarios.

## Troubleshooting

- **Speech Recognition Issues** - Check microphone settings and background noise
- **API Authentication Errors** - Verify your Google Cloud credentials and OpenAI API key
- **Calendar Integration Problems** - Ensure your service account has the necessary Calendar API permissions

## Development

To extend the application:

1. For new UI features, modify `pygame_ui.py`
2. For new AI capabilities, update `utils.py` and `system_prompts.py`
3. For additional service integrations, add new client initializations in `main.py`


## Security Considerations

- API keys and sensitive information should be stored in environment variables or secure configuration files
- The service account used for Google Calendar should have minimal permissions
- Customer data should be handled according to relevant privacy regulations

## Acknowledgements

- [Google Cloud Speech APIs](https://cloud.google.com/speech-to-text)
- [OpenAI](https://openai.com/) for GPT language model
- [LangChain](https://github.com/hwchase17/langchain) framework
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) library
