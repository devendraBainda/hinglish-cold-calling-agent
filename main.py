import os
import time
import speech_recognition as sr
from datetime import datetime, timedelta

from google.cloud import speech, texttospeech
from googleapiclient.discovery import build
from google.oauth2 import service_account

from langchain_openai import ChatOpenAI

import pygame
from pygame import mixer
import platform
import subprocess

from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_FILE_PATH")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE

openai_api_key = os.environ.get("OPEN_AI_API_KEY")

SYSTEM_PROMPTS = {
    "demo_scheduling": """
    You are an intelligent AI assistant that specializes in scheduling product demos for an ERP system in Hinglish (a mix of Hindi and English). 
    Your job is to call potential customers and persuade them to schedule a demo for our advanced ERP system.
    
    Key points about our ERP system:
    - Comprehensive modules for inventory, sales, accounting, HR, and production
    - Cloud-based with 24/7 access from any device
    - Easy customization for specific business needs
    - Seamless integration with existing systems
    - Affordable pricing with flexible payment options
    
    Guidelines for your conversation:
    - Start with a polite introduction in Hinglish
    - Explain the key benefits of our ERP system
    - Listen carefully to the customer's requirements and concerns
    - Address objections professionally
    - Try to schedule a demo at a convenient time
    - If they're not interested now, ask when would be a good time to follow up
    - Always maintain a conversational, human-like tone
    - Use natural Hinglish phrases, not direct translations from English
    
    Remember: The goal is to schedule a demo, but the customer's experience is equally important.
    """,
    
    "candidate_interviewing": """
    You are an intelligent AI assistant conducting initial screening interviews for job candidates in Hinglish (a mix of Hindi and English).
    Your job is to assess candidates for technical and cultural fit in our organization.
    
    Job details:
    - Role: AI/ML Engineer
    - Required skills: Python, Machine Learning, Natural Language Processing
    - Experience: 2+ years
    - Education: B.Tech/M.Tech in Computer Science or related field
    
    Interview structure:
    - Start with a warm introduction and explain the interview process
    - Ask about the candidate's background, education, and experience
    - Inquire about specific projects they've worked on
    - Ask technical questions related to the role
    - Evaluate soft skills and cultural fit
    - Allow time for the candidate to ask questions
    - Explain next steps in the hiring process
    
    Guidelines:
    - Maintain a professional yet friendly tone
    - Speak in natural Hinglish, not direct translations
    - Listen carefully and adapt your questions based on responses
    - Take note of both technical abilities and communication skills
    - Be respectful of the candidate's time and experience
    
    Remember: The goal is to make a preliminary assessment while giving the candidate a positive impression of our company.
    """,
    
    "payment_followup": """
    You are an intelligent AI assistant handling payment follow-ups and order reminders in Hinglish (a mix of Hindi and English).
    Your job is to politely remind customers about pending payments or orders while maintaining good customer relationships.
    
    Guidelines for your conversation:
    - Start with a friendly greeting and identify yourself clearly
    - Politely remind about the pending payment or order
    - Provide all necessary details (invoice number, amount due, deadline)
    - Ask if there are any concerns or issues causing the delay
    - Offer solutions for easy payment processing
    - If they need more time, work out a reasonable timeline
    - Thank them for their business and continued support
    - End the call on a positive note
    
    Important points:
    - Maintain professionalism and courtesy at all times
    - Be understanding of genuine issues
    - Use natural Hinglish expressions, not direct translations
    - Keep the tone conversational and non-confrontational
    - Focus on problem-solving rather than demanding payment
    
    Remember: While collecting payments is important, preserving the customer relationship is equally crucial.
    """
}

llm = ChatOpenAI(model_name="gpt-4", api_key=openai_api_key)

try:
    speech_client = speech.SpeechClient()
    
    tts_client = texttospeech.TextToSpeechClient()
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    calendar_service = build("calendar", "v3", credentials=credentials)
    
    print("All Google services initialized successfully")
except Exception as e:
    print(f"Error initializing Google services: {e}")
    raise

def recognize_speech_from_mic(language_code="hi-IN"):
    """
    Captures speech from microphone and returns recognized text
    """
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        recognizer.adjust_for_ambient_noise(source)  
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=language_code)
        print(f"✅ Recognized Speech: {text}")
        return text

    except sr.UnknownValueError:
        print("❌ Could not understand the audio.")
        return None
    except sr.RequestError:
        print("❌ Speech recognition service unavailable.")
        return None
    except Exception as e:
        print(f"❌ Error during speech recognition: {e}")
        return None

def recognize_speech_from_file(audio_path, language_code="hi-IN"):
    """
    Recognizes speech from an audio file
    """
    try:
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=language_code
        )
        
        response = speech_client.recognize(config=config, audio=audio)
        return response.results[0].alternatives[0].transcript if response.results else ""
    except Exception as e:
        print(f"Error recognizing speech from file: {e}")
        return ""

def get_ai_response(text, scenario="demo_scheduling", max_retries=3):
    """
    Gets AI response from OpenAI model with retry logic
    
    Args:
        text (str): User input text
        scenario (str): One of 'demo_scheduling', 'candidate_interviewing', or 'payment_followup'
        max_retries (int): Maximum number of retry attempts
    """
    if not text:
        return "I didn't catch that. Please try again."
    
    system_prompt = SYSTEM_PROMPTS.get(scenario, SYSTEM_PROMPTS["demo_scheduling"])
    
    for attempt in range(max_retries):
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
            
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Error getting AI response (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {2**attempt} seconds...")
                time.sleep(2**attempt)
            else:
                return "I'm having trouble processing your request right now. Please try again later."


def synthesize_speech(text, output_path="response.mp3", language_code="hi-IN"):
    """
    Converts text to speech and saves to a file
    """
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, 
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
            
        print(f"Speech synthesized and saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error synthesizing speech: {e}")
        return None


def schedule_demo(user_email, date_time=None, duration_hours=1):
    """
    Schedules a demo in Google Calendar
    
    Args:
        user_email: Email of the attendee
        date_time: ISO format datetime string. If None, schedules for tomorrow
        duration_hours: Duration of the meeting in hours
    
    Returns:
        String with confirmation and link
    """
    try:
        if not date_time:
            tomorrow = datetime.now() + timedelta(days=1)
            date_time = tomorrow.replace(hour=15, minute=0, second=0).isoformat()
        
        start_dt = datetime.fromisoformat(date_time.replace('Z', '+00:00').replace('T', ' '))
        end_dt = start_dt + timedelta(hours=duration_hours)
        
        event = {
            'summary': 'AI Demo Session',
            'description': 'Demo session for our ERP system product.',
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'attendees': [{'email': user_email}],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        event = calendar_service.events().insert(calendarId='primary', body=event).execute()
        return f"Demo scheduled successfully! Details: {event.get('htmlLink')}"
    except Exception as e:
        print(f"Error scheduling demo: {e}")
        return f"Failed to schedule demo: {str(e)}"

def track_customer(name, email, interaction, scenario):
    """
    Logs customer interaction to a file-based CRM
    """
    try:
        os.makedirs("crm_data", exist_ok=True)
        
        file_path = os.path.join("crm_data", "customer_interactions.txt")
        
        with open(file_path, "a", encoding="utf-8") as crm_file:
            crm_file.write(f"{datetime.now()} - {name} ({email}) - {scenario}: {interaction}\n")
        
        return "Customer interaction logged successfully."
    except Exception as e:
        print(f"Error logging customer interaction: {e}")
        return f"Failed to log customer interaction: {str(e)}"

def handle_demo_scheduling(user_email, user_input):
    """
    Handles demo scheduling based on user input
    """
    if isinstance(user_input, str) and "schedule a demo" in user_input.lower():
        event_link = schedule_demo(user_email)
        return event_link
    
    ai_response = get_ai_response(user_input, scenario="demo_scheduling")
    
    track_customer("Potential Customer", user_email, f"Q: {user_input}, A: {ai_response}", "demo_scheduling")
    
    return ai_response

def handle_candidate_interview(user_input):
    """
    Handles interview questions
    """
    ai_response = get_ai_response(user_input, scenario="candidate_interviewing")
    
    track_customer("Candidate", "candidate@example.com", f"Q: {user_input}, A: {ai_response}", "candidate_interviewing")
    
    return ai_response

def handle_payment_followup(user_email, user_input):
    """
    Handles payment follow-up conversations
    """
    ai_response = get_ai_response(user_input, scenario="payment_followup")
    
    track_customer("Customer", user_email, f"Q: {user_input}, A: {ai_response}", "payment_followup")
    
    return ai_response

import pygame
from pygame import mixer
import os
import platform
import subprocess

def play_audio(file_path):
    """
    Plays the audio file using platform-specific methods
    """
    try:
        if platform.system() == "Windows":
            mixer.init()
            mixer.music.load(file_path)
            mixer.music.play()
            while mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            mixer.music.unload()
        elif platform.system() == "Darwin":
            subprocess.call(["afplay", file_path])
        else:
            if os.system("which mpg123 > /dev/null") == 0:
                subprocess.call(["mpg123", file_path])
            elif os.system("which mpg321 > /dev/null") == 0:
                subprocess.call(["mpg321", file_path])
            else:
                # Fallback to pygame
                mixer.init()
                mixer.music.load(file_path)
                mixer.music.play()
                while mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                mixer.music.unload()
        return True
    except Exception as e:
        print(f"Error playing audio: {e}")
        return False

def main_loop():
    """
    Main execution loop for the voice assistant
    """
    print("Starting Hinglish Cold Calling AI Agent. Press Ctrl+C to exit.")
    print("Select scenario:")
    print("1. Demo Scheduling for ERP System")
    print("2. Candidate Interviewing")
    print("3. Payment/Order Follow-up")
    
    try:
        scenario_choice = int(input("Enter choice (1-3): "))
        if scenario_choice == 1:
            scenario = "demo_scheduling"
            user_email = input("Enter customer email: ")
        elif scenario_choice == 2:
            scenario = "candidate_interviewing"
            user_email = "candidate@example.com"
        elif scenario_choice == 3:
            scenario = "payment_followup"
            user_email = input("Enter customer email: ")
        else:
            print("Invalid choice. Defaulting to demo scheduling.")
            scenario = "demo_scheduling"
            user_email = input("Enter customer email: ")
        
        initial_greeting = {
            "demo_scheduling": "Namaste! Main iMax Global Ventures se bol raha hoon. Kya aap hamare ERP system ke baare mein baat karna chahenge?",
            "candidate_interviewing": "Namaste! Main iMax Global Ventures se bol raha hoon. Hum aapka interview lene wale hain AI/ML Engineer position ke liye.",
            "payment_followup": "Namaste! Main iMax Global Ventures se bol raha hoon. Main aapke pending payment ke baare mein baat karna chahta hoon."
        }
        
        greeting = initial_greeting.get(scenario, "Namaste! Main iMax Global Ventures se bol raha hoon.")
        print(f"🤖 Initial Greeting: {greeting}")
        greeting_audio = synthesize_speech(greeting, output_path="greeting.mp3")
        play_audio(greeting_audio)
        
        while True:
            print(f"\nRunning {scenario.replace('_', ' ')} scenario.")
            print("Speak in Hinglish (mix of Hindi and English).")
            recognized_text = recognize_speech_from_mic()
            
            if recognized_text:
                if recognized_text.lower() in ["exit", "quit", "stop", "बंद", "बंद करो"]:
                    print("Exiting voice assistant...")
                    break
                
                if scenario == "demo_scheduling":
                    ai_response = handle_demo_scheduling(user_email, recognized_text)
                elif scenario == "candidate_interviewing":
                    ai_response = handle_candidate_interview(recognized_text)
                elif scenario == "payment_followup":
                    ai_response = handle_payment_followup(user_email, recognized_text)
                else:
                    ai_response = get_ai_response(recognized_text)
                
                print(f"🤖 AI Response: {ai_response}")
                
                audio_file = synthesize_speech(ai_response)
                
                print("🔊 Playing audio response...")
                play_audio(audio_file)
    except KeyboardInterrupt:
        print("\nVoice assistant stopped by user.")
    except Exception as e:
        print(f"Error in main loop: {e}")

# Program entry point
if __name__ == "__main__":
    main_loop()