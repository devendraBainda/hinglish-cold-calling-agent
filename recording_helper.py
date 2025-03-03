# recording_helper.py
import speech_recognition as sr
import threading
import time

class RecordingHelper:
    """
    Helper class for managing speech recognition without interfering with Pygame
    """
    def __init__(self, language_code="hi-IN"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language_code = language_code
        self.recording = False
        self.recording_thread = None
        self.audio_data = None
        self.is_complete = False
        self.result_text = None
        self.error = None
    
    def start_recording(self):
        """Start recording in a separate thread"""
        if not self.recording:
            self.recording = True
            self.is_complete = False
            self.result_text = None
            self.error = None
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            return True
        return False
    
    def stop_recording(self):
        """Stop the recording"""
        self.recording = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1.0)
        return True
    
    def get_result(self):
        """Get the recognition result"""
        if self.is_complete:
            return self.result_text, self.error
        return None, None
    
    def _record_audio(self):
        """Record audio in a separate thread"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("🎤 Background recording started...")
                self.audio_data = self.recognizer.listen(source, timeout=10.0, phrase_time_limit=None)
                
            # Process the audio
            if self.audio_data:
                try:
                    self.result_text = self.recognizer.recognize_google(self.audio_data, language=self.language_code)
                    print(f"✅ Recognized Speech: {self.result_text}")
                except sr.UnknownValueError:
                    self.error = "Could not understand the audio."
                    print("❌ Could not understand the audio.")
                except sr.RequestError:
                    self.error = "Speech recognition service unavailable."
                    print("❌ Speech recognition service unavailable.")
                except Exception as e:
                    self.error = f"Error during speech recognition: {str(e)}"
                    print(f"❌ Error during speech recognition: {e}")
            else:
                self.error = "No audio was recorded."
                print("❌ No audio was recorded.")
        
        except Exception as e:
            self.error = f"Error recording audio: {str(e)}"
            print(f"❌ Error recording audio: {e}")
        
        finally:
            self.is_complete = True
            self.recording = False