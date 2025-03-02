# Hinglish Cold Calling AI Agent

An intelligent voice-based AI assistant for conducting cold calls in Hinglish (Hindi-English mix) for business scenarios including product demo scheduling, candidate interviewing, and payment follow-up.

## 🚀 Features

- **Speech Recognition**: Captures and processes spoken Hinglish
- **Natural Language Understanding**: Interprets user intent and responds appropriately
- **Speech Synthesis**: Converts text responses to natural-sounding speech
- **Google Calendar Integration**: Automatically schedules demos with customers
- **CRM Tracking**: Logs all interactions for future reference
- **Multiple Business Scenarios**:
  - Product Demo Scheduling for ERP System
  - Candidate Interviewing for Technical Roles
  - Payment and Order Follow-up

## 📋 Requirements

- Python 3.8+
- Google Cloud account with Speech-to-Text, Text-to-Speech, and Calendar API enabled
- OpenAI API key
- PyAudio and compatible audio hardware

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone (https://github.com/devendraBainda/iMax_submission.git)
   cd iMax_submission
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Google Cloud credentials:
   - Create a service account in Google Cloud Console
   - Enable Speech-to-Text, Text-to-Speech, and Calendar APIs
   - Generate and download a JSON key file
   - Place the key file in the project directory as `api.json`

5. Configure settings:
   - Update `config/settings.py` with your API keys and preferences

## 🎮 Usage

Run the main application:

```bash
python main.py
```

Follow the on-screen prompts to:
1. Select a scenario (Demo Scheduling, Candidate Interviewing, or Payment Follow-up)
2. Enter customer email (for Demo Scheduling and Payment Follow-up)
3. Begin the conversation by speaking in Hinglish

### 🔉 Voice Commands

- Start speaking after the "Speak now..." prompt
- Say "exit", "quit", "stop", "बंद", or "बंद करो" to end the conversation

## 🔍 Scenario Details

### Demo Scheduling

This scenario focuses on scheduling product demos for an ERP system. The AI agent:
- Introduces the product benefits
- Addresses customer questions and concerns
- Arranges a demo session at a suitable time
- Creates a calendar event with the customer's email

### Candidate Interviewing

For initial screening of job candidates, the AI agent:
- Asks about background, skills, and experience
- Presents technical questions related to the role
- Evaluates communication skills
- Provides information about next steps

### Payment Follow-up

For handling payment reminders, the AI agent:
- Politely reminds customers about pending payments
- Provides payment details and options
- Addresses concerns about the payment process
- Maintains a positive customer relationship

## 📝 Notes on Hinglish Handling

The system is designed to handle Hinglish speech, which is a mix of Hindi and English commonly used in India. The speech recognition and synthesis are configured for this hybrid language pattern, using the `hi-IN` language code which provides good support for Hinglish.

## 🛠️ Troubleshooting

### PyAudio Installation Issues

If you encounter installation problems with PyAudio on Windows:
1. Download the appropriate wheel file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Install the wheel file directly:
   ```bash
   pip install [path-to-wheel-file].whl
   ```

### Speech Recognition Problems

If the system fails to recognize speech:
- Check your microphone settings
- Ensure you have a stable internet connection
- Try speaking more clearly and at a moderate pace
- Adjust ambient noise with `recognizer.adjust_for_ambient_noise(source, duration=1)`

## 🔒 Security Considerations

- API keys and sensitive information should be stored in environment variables or secure configuration files
- The service account used for Google Calendar should have minimal permissions
- Customer data should be handled according to relevant privacy regulations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Google Cloud Speech APIs](https://cloud.google.com/speech-to-text)
- [OpenAI](https://openai.com/) for GPT language model
- [LangChain](https://github.com/hwchase17/langchain) framework
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) library
