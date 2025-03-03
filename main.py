import os
from dotenv import load_dotenv
from google.cloud import speech, texttospeech
from googleapiclient.discovery import build
from google.oauth2 import service_account
from langchain_openai import ChatOpenAI

# Import from our modules
from system_prompts import SYSTEM_PROMPTS

import utils
from pygame_ui import run_ui

# Load environment variables
load_dotenv()

def initialize_services():
  
    SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_FILE_PATH")
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE
    
    openai_api_key = os.environ.get("OPEN_AI_API_KEY")
    
    try:
        # Initialize Google Speech client
        utils.speech_client = speech.SpeechClient()
        
        # Initialize Google Text-to-Speech client
        utils.tts_client = texttospeech.TextToSpeechClient()
        
        # Initialize Google Calendar service
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        utils.calendar_service = build("calendar", "v3", credentials=credentials)
        
        # Initialize OpenAI client
        utils.llm = ChatOpenAI(model_name="gpt-4", api_key=openai_api_key)
        
        print("All services initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing services: {e}")
        return False

def main_loop():
     #Main execution loop for the voice assistant
   
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
            "demo_scheduling": "Namaste! Mai iMax Global Ventures se bol raha hoon. Kya aap hamare ERP system ke baare mein baat karna chahenge?",
            "candidate_interviewing": "Namaste! Mai iMax Global Ventures se bol raha hoon. Hum aapka interview lene wale hain AI/ML Engineer position ke liye.",
            "payment_followup": "Namaste! Mai iMax Global Ventures se bol raha hoon. Mai aapke pending payment ke baare mein baat karna chahta hoon."
        }
        
        greeting = initial_greeting.get(scenario, "Namaste! Mai iMax Global Ventures se bol raha hoon.")
        print(f" Initial Greeting: {greeting}")
        greeting_audio = utils.synthesize_speech(greeting, output_path="greeting.mp3")
        utils.play_audio(greeting_audio)
        
        print("\nUse SPACE key to start and stop recording.")
        
        while True:
            print(f"\nRunning {scenario.replace('_', ' ')} scenario.")
            print("Speak in Hinglish (mix of Hindi and English).")
            
            # Use the manual control recording function instead of automatic
            recognized_text = utils.recognize_speech_with_manual_control()
            
            if recognized_text:
                if recognized_text.lower() in ["exit", "quit", "stop", "बंद", "बंद करो"]:
                    print("Exiting voice assistant...")
                    break
                
                if scenario == "demo_scheduling":
                    ai_response = utils.handle_demo_scheduling(user_email, recognized_text)
                elif scenario == "candidate_interviewing":
                    ai_response = utils.handle_candidate_interview(recognized_text)
                elif scenario == "payment_followup":
                    ai_response = utils.handle_payment_followup(user_email, recognized_text)
                else:
                    ai_response = utils.get_ai_response(recognized_text)
                
                print(f" AI Response: {ai_response}")
                
                audio_file = utils.synthesize_speech(ai_response)
                
                print("🔊 Playing audio response...")
                utils.play_audio(audio_file)
    except KeyboardInterrupt:
        print("\nVoice assistant stopped by user.")
    except Exception as e:
        print(f"Error in main loop: {e}")

def main():
    """
    Entry point for the application
    """
    if initialize_services():
        # Choose between terminal-based UI or Pygame UI
        use_pygame_ui = input("Use graphical interface? (y/n): ").lower().startswith('y')
        
        if use_pygame_ui:
            run_ui()
        else:
            main_loop()
    else:
        print("Failed to initialize services. Exiting...")

# Program entry point
if __name__ == "__main__":
    main()