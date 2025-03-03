import os
import time
import speech_recognition as sr
from datetime import datetime, timedelta
from google.cloud import speech, texttospeech
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pygame
from pygame import mixer
import platform
import subprocess

from system_prompts import SYSTEM_PROMPTS

# Global variables to be initialized in main.py
speech_client = None
tts_client = None
calendar_service = None
llm = None

def recognize_speech_from_mic(language_code="hi-IN"):
    
    # Captures speech from microphone and returns recognized text
   
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

def recognize_speech_with_manual_control(language_code="hi-IN"):
    """
    Captures speech from microphone with manual control using spacebar
    and returns recognized text
    """
    # Initialize pygame for keyboard input
    pygame.init()
    screen = pygame.display.set_mode((300, 100))
    pygame.display.set_caption("Press SPACE to record")
    font = pygame.font.Font(None, 36)
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    recording = False
    audio = None
    
    print("Press SPACE to start recording, press SPACE again to stop.")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    recording = not recording
                    if recording:
                        # Start recording
                        print("🔴 Recording started... Press SPACE to stop.")
                        
                        # Clear screen and show recording message
                        screen.fill((0, 0, 0))
                        text = font.render("Recording...", True, (255, 0, 0))
                        screen.blit(text, (75, 40))
                        pygame.display.flip()
                        
                        with microphone as source:
                            recognizer.adjust_for_ambient_noise(source)
                            audio = recognizer.listen(source, phrase_time_limit=None)
                    else:
                        # Stop recording
                        print("⏹️ Recording stopped. Processing...")
                        
                        # Clear screen and show processing message
                        screen.fill((0, 0, 0))
                        text = font.render("Processing...", True, (0, 255, 0))
                        screen.blit(text, (75, 40))
                        pygame.display.flip()
                        
                        # Process audio and exit the loop
                        running = False
        
        # Update the display
        if not recording and running:
            screen.fill((0, 0, 0))
            text = font.render("Press SPACE to record", True, (255, 255, 255))
            screen.blit(text, (40, 40))
            pygame.display.flip()
    
    pygame.quit()
    
    if audio:
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
    else:
        print("❌ No audio recorded.")
        return None

def recognize_speech_from_file(audio_path, language_code="hi-IN"):
    """
    Recognizes speech from an audio file
    """
    global speech_client
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
    global llm
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
    global tts_client
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, 
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
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
    # Schedules a demo in Google Calendar
    
    global calendar_service
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
   # Logs customer interaction to a file-based CRM
 
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
   # Handles demo scheduling based on user input
    
    ai_response = get_ai_response(user_input, scenario="demo_scheduling")

    if "स्केड्यूलिंग मीटिंग" in ai_response or "Scheduling Meeting" in ai_response:
        event_link = schedule_demo(user_email)
        print(event_link)    
    track_customer("Potential Customer", user_email, f"Q: {user_input}, A: {ai_response}", "demo_scheduling")
    
    return ai_response

def handle_candidate_interview(user_input):
    # Handles interview questions
    
    ai_response = get_ai_response(user_input, scenario="candidate_interviewing")
    
    track_customer("Candidate", "candidate@example.com", f"Q: {user_input}, A: {ai_response}", "candidate_interviewing")
    
    return ai_response

def handle_payment_followup(user_email, user_input):
    #Handles payment follow-up conversations
    
    ai_response = get_ai_response(user_input, scenario="payment_followup")
    
    track_customer("Customer", user_email, f"Q: {user_input}, A: {ai_response}", "payment_followup")
    
    return ai_response

def play_audio(file_path):
   # Plays the audio file using platform-specific methods
    
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